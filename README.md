# zbx-digest – Zabbix Incident Digest (CLI)

Ferramenta CLI para **coleta, sumarização e auto-ação de incidentes** do Zabbix via **JSON-RPC API**.

- 🔎 Coleta eventos/problemas por janela de tempo
- 📊 Gera **relatório Markdown** (e opcional **CSV**) com:
  - Incidentes por **severidade**
  - Top **hosts** mais incidentados
  - Tabela detalhada de eventos
- 🤖 (Opcional) **Auto-ack** de eventos que casam com **regex** (para ruído de lab/dev)
- 🧪 **Modo mock** para rodar sem Zabbix (útil pra correção/avaliação acadêmica)

---

## 🧰 Tecnologias
- Python 3.10+
- `requests`
- `python-dotenv`


## 🎯 Aprendizados (o que exercitei aqui)
- Consumo de **API JSON-RPC** (login + chamadas autenticadas)
- **Tratamento/normalização** de dados e agregação
- **CLI com argparse** (flags e DX)
- **Regex** para automação (auto-ack seletivo)
- Geração de **relatórios Markdown/CSV**
- Boas práticas: `.env`, `requirements.txt`, `dry-run`, `mock mode`

---

## 🚀 Como rodar

1. Clone o repositório e instale:
```bash
git clone https://github.com/tiagoalmeida10/zbx-digest.git
cd zbx-digest
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

2. Configure `.env` a partir de `.env.example`.

3. Exemplos de execução:

```bash
python main.py --from 2025-09-01 --to 2025-09-30 --out-md report.md
python main.py --mock --out-md report.md
python main.py --ack-regex "(lab|dev)" --auto-ack --no-dry-run --mock
```

---

## Estrutura
```
zbx-digest/
  ├─ main.py
  │─ zbx_api.py
  │─ utils.py
  ├─ requirements.txt
  ├─ .env.example
  └─ README.md
```
