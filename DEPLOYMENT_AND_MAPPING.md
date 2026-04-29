# HerbAPI Deployment and Capability Mapping

## Architecture Overview

- Django service runs on the lab server:
  - web/chat entry: `chat`
  - REST APIs: `data_api`
- MCP service runs on JD Cloud:
  - entry: `mcp_server.py`
  - streamable HTTP endpoint: `/mcp`
- Both API and MCP call the same business layer:
  - `data_api/services/*`

This keeps API and MCP behavior aligned and avoids duplicated logic.

## MCP Tool to REST API Mapping

Base path for REST endpoints: `/api/query/`

- `list_gene_herbs_tool(limit)` -> `GET /api/query/list_gene_herbs?limit=10`
- `get_gene_herb_tool(record_id)` -> `GET /api/query/get_gene_herb?record_id=1`
- `search_gene_herbs_by_gene_tool(gene, limit)` -> `GET /api/query/search_gene_herbs_by_gene?gene=AHR&limit=20`
- `search_gene_herbs_by_herb_name_tool(name, limit)` -> `GET /api/query/search_gene_herbs_by_herb_name?name=大麻&limit=20`
- `search_gene_drugs_by_gene_tool(gene, limit)` -> `GET /api/query/search_gene_drugs_by_gene?gene=STAT3&limit=20`
- `search_gene_drugs_by_drug_tool(drug, limit)` -> `GET /api/query/search_gene_drugs_by_drug?drug=metformin&limit=20`
- `search_herb_ingredients_by_herb_tool(herb, limit)` -> `GET /api/query/search_herb_ingredients_by_herb?herb=大麻&limit=20`
- `search_herb_ingredients_by_gene_tool(gene, limit)` -> `GET /api/query/search_herb_ingredients_by_gene?gene=AHR&limit=20`
- `get_herb_ingredient_by_name_tool(ingredient_name)` -> `GET /api/query/get_herb_ingredient_by_name?ingredient_name=quercetin`
- `query_gene_knowledge_tool(gene, limit)` -> `GET /api/query/query_gene_knowledge?gene=AHR&limit=10`
- `get_gene_evidence_sentences(gene, limit)` -> `GET /api/query/get_gene_evidence_sentences?gene=STAT3&limit=5`
- `resolve_herb_tool(name)` -> `GET /api/query/resolve_herb?name=大麻`

Health checks:

- Django API: `GET /api/health`
- MCP service: `GET /ping`

## Environment Variables

### Lab Server (Django)

```env
LLM_API_KEY=...
LLM_BASE_URL=...
LLM_MODEL=...

MCP_ENDPOINT=http://117.72.82.64:8087/mcp
MCP_PROTOCOL_VERSION=2025-12-05
MCP_HOST_HEADER=

DB_PATH=/opt/herbapi/precision_medicine.db
```

### JD Cloud Server (MCP)

```env
DJANGO_SETTINGS_MODULE=herbapi.settings
DB_PATH=/opt/herb_mcp/precision_medicine.db

MCP_HOST=0.0.0.0
MCP_PORT=8087
```

## Deploy Steps

## 1) JD Cloud: Deploy MCP Service

Suggested directory: `/opt/herb_mcp`

Required files:

- `mcp_server.py`
- `data_api/`
- `herbapi/` (for settings import used by `django.setup()`)
- `precision_medicine.db`
- `requirements.txt`
- `.env`

Commands:

```bash
cd /opt/herb_mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python mcp_server.py
```

Check:

```bash
curl http://127.0.0.1:8087/ping
```

Expected result contains `"status":"ok"`.

## 2) Lab Server: Deploy Django Service

Suggested directory: `/opt/herbapi`

Required files:

- complete Django project (`manage.py`, `chat/`, `data_api/`, `herbapi/`, `templates/`, `static/`)
- `precision_medicine.db`
- `requirements.txt`
- `.env`

Commands:

```bash
cd /opt/herbapi
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

## 3) Networking

- On JD Cloud security group, allow TCP `8087`.
- For production safety, only allow source IP of the lab server.
- Keep `MCP_ENDPOINT` on lab server pointing to `http://117.72.82.64:8087/mcp`.

## systemd (Recommended)

## MCP service unit (`/etc/systemd/system/herb-mcp.service`)

```ini
[Unit]
Description=Herb MCP Service
After=network.target

[Service]
User=root
WorkingDirectory=/opt/herb_mcp
EnvironmentFile=/opt/herb_mcp/.env
ExecStart=/opt/herb_mcp/.venv/bin/python /opt/herb_mcp/mcp_server.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

## Django service unit (`/etc/systemd/system/herb-django.service`)

```ini
[Unit]
Description=Herb Django Service
After=network.target

[Service]
User=root
WorkingDirectory=/opt/herbapi
EnvironmentFile=/opt/herbapi/.env
ExecStart=/opt/herbapi/.venv/bin/python /opt/herbapi/manage.py runserver 0.0.0.0:8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now herb-mcp
sudo systemctl enable --now herb-django
sudo systemctl status herb-mcp
sudo systemctl status herb-django
```

## One-Command Engineering Deployment

Files added under `deploy/`:

- `deploy/deploy_mcp.sh`
- `deploy/deploy_django.sh`
- `deploy/herb-mcp.service`
- `deploy/herb-django.service`
- `deploy/nginx-herbapi.conf`

Before running:

```bash
chmod +x deploy/deploy_mcp.sh deploy/deploy_django.sh
```

### MCP machine (JD Cloud)

Assume code path is `/opt/herb_mcp`:

```bash
cd /opt/herb_mcp
APP_DIR=/opt/herb_mcp bash deploy/deploy_mcp.sh
```

### Django machine (Lab server)

Assume code path is `/opt/herbapi`:

```bash
cd /opt/herbapi
APP_DIR=/opt/herbapi DOMAIN_OR_IP=your.domain.or.ip bash deploy/deploy_django.sh
```

If you only use server IP:

```bash
APP_DIR=/opt/herbapi DOMAIN_OR_IP=your_public_ip bash deploy/deploy_django.sh
```

## Quick Troubleshooting

- `400 Missing session ID`: client did not send `mcp-session-id` after initialize.
- `406 Not Acceptable`: `Accept` header must include both JSON and SSE.
- `421 Invalid Host header`: server/proxy rewrote host header incorrectly.
- `502`: service unreachable or upstream process not running.
