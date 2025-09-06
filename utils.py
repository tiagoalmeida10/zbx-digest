from datetime import datetime, timezone
from collections import Counter

SEVERITY_MAP = {
    0: "Not classified",
    1: "Information",
    2: "Warning",
    3: "Average",
    4: "High",
    5: "Disaster",
}

def ts_to_str(ts):
    return datetime.fromtimestamp(ts, tz=timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S")

def summarize_events(events):
    by_sev = Counter()
    by_host = Counter()
    flat = []
    for ev in events:
        sev = SEVERITY_MAP.get(int(ev.get("severity", 0)), str(ev.get("severity")))
        hosts = ev.get("hosts", [])
        host = hosts[0]["host"] if hosts else "-"
        by_sev[sev] += 1
        by_host[host] += 1
        flat.append({
            "eventid": ev["eventid"],
            "time": ts_to_str(int(ev["clock"])),
            "host": host,
            "severity": sev.upper(),
            "name": ev.get("name", ""),
            "acknowledged": ev.get("acknowledged", "0"),
        })
    top_hosts = by_host.most_common(10)
    return {
        "by_severity": by_sev,
        "top_hosts": top_hosts,
        "rows": flat
    }

def render_markdown(summary, title="Zabbix Incident Digest", period=""):
    lines = [f"# {title}", ""]
    if period:
        lines.append(f"**Período:** {period}")
        lines.append("")
    lines.append("## Resumo por Severidade")
    for sev, cnt in summary["by_severity"].most_common(None):
        lines.append(f"- **{sev.upper()}**: {cnt}")
    lines.append("")
    lines.append("## Top Hosts")
    for host, cnt in summary["top_hosts"]:
        lines.append(f"- `{host}` ({cnt})")
    lines.append("")
    lines.append("## Eventos")
    lines.append("| EventID | Time | Host | Severity | Problem | Ack |")
    lines.append("|---------|------|------|----------|---------|-----|")
    for r in summary["rows"]:
        lines.append(f"| {r['eventid']} | {r['time']} | {r['host']} | {r['severity']} | {r['name']} | {r['acknowledged']} |")
    lines.append("")
    return "\n".join(lines)
