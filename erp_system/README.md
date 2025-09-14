# ERP System - Multi-Agent Chat Assistant

A production-style ERP assistant powered by multiple AI agents with memory, built on LangChain, FastAPI, and Streamlit. This README is aligned to the submission requirements.

## Submission Checklist (What’s included)
- Python script files for agents and tools (see backend/agents and backend/tools)
- README explaining:
   - System architecture and agent responsibilities
   - Tool integration and MCP compliance
   - Memory management and database usage
- Sample SQLite database `databases/erp_sample.db` with test tables and seed data
- Short video demo (record separately; suggested flow below)
- Modular, well-commented code organized under `backend/`, `frontend/`, `databases/`
- requirements.txt and instructions to run locally (Makefile), Docker, and Streamlit/FastAPI UI
- Deployment files (Dockerfile, docker-compose.yml) with a quick deploy guide

## 🚀 System Architecture

### Agents (backend/agents)
- Router Agent (`simple_router_agent.py`)
   - Classifies user intent and routes to Sales or Analytics
   - Logs tool usage and approvals
   - Uses LangChain ReAct
- Sales Agent (`SalesAgent.py`)
   - Customer/lead/order queries and CRM workflows
   - Tools: SQL read/write, RAG search (docs), lead scoring
   - Uses SQLite via shared DB utilities
- Analytics Agent (`AnalyticsAgent.py`)
   - NL → SQL analytics, reporting, and visualization specs
   - Optional RAG for business definitions with safe fallback

### Tools & MCP
- Tools live in `backend/tools` (e.g., `sales_tools.py`) and are exposed to agents as LangChain Tools (MCP-style contract: name, description, input schema, output).
- Each tool is pure and logs invocations (inputs/outputs) through memory.

### Memory Management (backend/memory)
- `base_memory.py` implements:
   - `RouterGlobalState`: conversations, messages, approvals, tool_calls (SQLite-backed)
   - `SalesEntityMemory`: customer-specific KV store
   - `AnalyticsReportMemory`: saved reports with statistics (run count, last_run)

### Database Usage
- SQLite database mounted at `databases/` (configurable via `DB_PATH` env)
- Agents access the same DB for consistent results
- Example tables used by agents: customers, products, orders, order_items, invoices, invoice_lines, payments, leads

## 🗃️ Sample SQLite Database
We ship a sample DB: `databases/erp_sample.db`
- If a full `databases/erp.db` exists, we copy it to `erp_sample.db` (richer data)
- Else we generate a minimal but representative dataset

Create/regenerate it with:
```bash
python create_sample_db.py
```

Set DB path via env (local) or compose (Docker):
```bash
export DB_PATH=databases/erp_sample.db
```

## 🧩 How to Run

### One-command (Docker)
```bash
make docker
```
UI: http://localhost:8501  •  API: http://localhost:8000/docs

### Local (no Docker)
```bash
make setup-local   # venv + deps + create_sample_db
make start-local   # start FastAPI + Streamlit
```

### Health & Logs
```bash
make health
make logs
```

## 💬 Demo Flow (<= 10 minutes)
1) Open UI and show agents list (/agents)
2) Sales examples: “how many customers”, “show leads”, “show orders”
3) Analytics: “revenue by month”, “top 5 products by revenue”, “AOV by month 2024”
4) Router: “count customers”, “leads with high score”, “revenue analysis 2024”
5) Show memory tables (conversations/messages) growing as you chat

## 🧠 Design Notes
- Agents use LangChain ReAct with clearly defined tools
- Memory is persisted in SQLite and auto-migrates missing columns
- Analytics RAG gracefully degrades if embeddings are unavailable

## 📦 Project Structure
```
erp_system/
├── backend/           # Agents, API, tools, memory
│   ├── agents/
│   ├── tools/
│   ├── memory/
│   └── api.py
├── frontend/          # Streamlit UI
├── databases/         # SQLite DBs (erp.db, erp_sample.db)
├── create_sample_db.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── Makefile
```

## 🔐 Configuration
- `.env` (copy from `.env.example`)
   - `GOOGLE_API_KEY=...`
   - `DB_PATH=databases/erp_sample.db` (optional; Docker sets `/app/databases/erp.db`)

## � Deployment
- Docker (recommended): `make docker`
- Production tip: front a reverse proxy (nginx) and persist volumes for `databases/` and `logs/`

---

ERP Chat Assistant – Intelligent Business Management Made Simple
