import os
import csv
import re
import argparse
from datetime import datetime, timezone
from dotenv import load_dotenv

from utils import summarize_events, render_markdown
from zbx_api import ZabbixAPI

def to_ts(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    local_dt = dt.astimezone()
    return int(local_dt.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())

def end_of_day_ts(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    local_dt = dt.astimezone()
    return int(local_dt.replace(hour=23, minute=59, second=59, microsecond=0).timestamp())

def write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["eventid", "time", "host", "severity", "name", "acknowledged"])
        w.writeheader()
        for r in rows:
            w.writerow(r)

MOCK_EVENTS = [
    {"eventid": "30001", "clock": 1756821453, "severity": 4, "name": "High CPU usage > 85% for 5m", "acknowledged": "0",
     "hosts": [{"hostid": "10101", "host": "app-01"}]},
    {"eventid": "30002", "clock": 1756825011, "severity": 3, "name": "Average I/O wait > 25%", "acknowledged": "1",
     "hosts": [{"hostid": "10102", "host": "db-01"}]},
    {"eventid": "30003", "clock": 1756828711, "severity": 2, "name": "WARNING: Disk /var > 80%", "acknowledged": "0",
     "hosts": [{"hostid": "10103", "host": "lab-01"}]},
    {"eventid": "30004", "clock": 1756832311, "severity": 5, "name": "DISASTER: Core link down", "acknowledged": "0",
     "hosts": [{"hostid": "10104", "host": "gw-core"}]},
    {"eventid": "30005", "clock": 1756835911, "severity": 2, "name": "WARNING: Memory usage > 90%", "acknowledged": "0",
     "hosts": [{"hostid": "10101", "host": "app-01"}]},
]

def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Zabbix Incident Digest CLI")
    parser.add_argument("--from", dest="from_date", help="YYYY-MM-DD")
    parser.add_argument("--to", dest="to_date", help="YYYY-MM-DD")
    parser.add_argument("--out-md", dest="out_md", help="Salvar relatório Markdown em PATH")
    parser.add_argument("--out-csv", dest="out_csv", help="Salvar CSV em PATH")
    parser.add_argument("--ack-regex", dest="ack_regex", help="Regex para auto-ack (ex.: '(lab|dev)')")
    parser.add_argument("--auto-ack", dest="auto_ack", action="store_true", help="Executa acknowledge dos eventos que casarem com o regex")
    parser.add_argument("--dry-run", dest="dry_run", action="store_true", default=True, help="Simular ações (padrão)")
    parser.add_argument("--no-dry-run", dest="dry_run", action="store_false", help="Executar ações reais")
    parser.add_argument("--verify-ssl", dest="verify_ssl", choices=["true", "false"], help="Sobrescreve verificação SSL do .env")
    parser.add_argument("--mock", action="store_true", help="Usar dados mock (sem chamar Zabbix)")
    parser.add_argument("-v", "--verbose", action="store_true")

    args = parser.parse_args()

    zbx_url = os.getenv("ZBX_URL")
    zbx_user = os.getenv("ZBX_USER")
    zbx_pass = os.getenv("ZBX_PASS")
    verify_ssl_env = os.getenv("ZBX_VERIFY_SSL", "true").lower() == "true"
    verify_ssl = verify_ssl_env if args.verify_ssl is None else (args.verify_ssl == "true")

    if args.mock:
        events = MOCK_EVENTS
        period_label = "MOCK DATA"
    else:
        if not (zbx_url and zbx_user and zbx_pass):
            raise SystemExit("Defina ZBX_URL, ZBX_USER, ZBX_PASS no .env (ou use --mock).")
        if not (args.from_date and args.to_date):
            raise SystemExit("Informe --from YYYY-MM-DD e --to YYYY-MM-DD (ou use --mock).")

        t_from = to_ts(args.from_date)
        t_to = end_of_day_ts(args.to_date)
        period_label = f"{args.from_date} → {args.to_date}"

        api = ZabbixAPI(zbx_url, zbx_user, zbx_pass, verify_ssl=verify_ssl)
        if args.verbose:
            print(f"[INFO] Login em {zbx_url} (verify_ssl={verify_ssl})")
        api.login()
        if args.verbose:
            print(f"[INFO] Coletando eventos de {period_label}")

        events = api.event_get(time_from=t_from, time_till=t_to, severities=None, value=1)

    if args.verbose:
        print(f"[INFO] Eventos coletados: {len(events)}")

    summary = summarize_events(events)

    md = render_markdown(summary, title="Zabbix Incident Digest", period=period_label)
    if args.out_md:
        with open(args.out_md, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"[OK] Markdown salvo em: {args.out_md}")
    else:
        print(md)

    if args.out_csv:
        write_csv(args.out_csv, summary["rows"])
        print(f"[OK] CSV salvo em: {args.out_csv}")
