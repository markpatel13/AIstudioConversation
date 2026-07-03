# AI Conversation Studio

> **Enterprise-grade Governance & Observability layer for AI assistants**  
> Built with FastAPI · SQLite · Streamlit · Groq API

---

## What It Does

AI Conversation Studio gives teams a single platform to:

- **Chat** with an AI assistant powered by the Groq API (llama-3.3-70b-versatile)
- **Manage knowledge sources** — paste text or upload files (TXT, PDF, DOCX, CSV, Markdown) to ground AI responses
- **Auto-evaluate** every response for Relevance, Groundedness, Coherence, and Hallucination Risk
- **Collect human feedback** (thumbs-up / thumbs-down) per conversation
- **Run prompt testing labs** — version prompt templates and batch-test them
- **Audit governance** — filter the full conversation audit trail by hallucination risk and reviewer status
- **Monitor analytics** — daily trends, quality scores, knowledge source usage, feedback ratios

---

## Project Structure

```
phonon/
├── backend/                    # FastAPI REST API
│   ├── app/
│   │   ├── api/                # Route handlers (chat, knowledge, feedback, ...)
│   │   ├── core/               # Config, DB session
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   └── services/           # GroqLLM, MockLLM, EvaluationService
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # Streamlit multi-page app
│   ├── app/
│   │   ├── main.py             # Conversation Playground (home page)
│   │   ├── pages/
│   │   │   ├── 1_Knowledge_Base.py
│   │   │   ├── 2_Prompt_Testing.py
│   │   │   ├── 3_Governance.py
│   │   │   └── 4_Analytics.py
│   │   ├── components/styles.py
│   │   └── utils/api_client.py
│   ├── requirements.txt
│   └── Dockerfile
├── database/                   # SQLite database file (auto-created)
├── documentation/              # This folder — all hackathon docs
├── docker-compose.yml
└── .env.example
```

---

## Quick Start

### Option 1 — Docker Compose (Recommended)

**Prerequisites:** Docker Desktop installed and running.

```bash
# 1. Navigate to the project root
cd phonon

# 2. Set your Groq API key
cp .env.example .env
# Edit .env and paste your key from https://console.groq.com/keys

# 3. Start everything
docker-compose up --build
```

| Service   | URL                        |
|-----------|---------------------------|
| Frontend  | http://localhost:8501      |
| Backend   | http://localhost:8000      |
| API Docs  | http://localhost:8000/docs |

---

### Option 2 — Run Locally (without Docker)

**Prerequisites:** Python 3.11+

**Backend**
```bash
cd backend
pip install -r requirements.txt

# PowerShell
$env:GROQ_API_KEY = "gsk_your_key_here"
$env:DATABASE_URL  = "sqlite:///./database/studio.db"

uvicorn app.main:app --reload --port 8000
```

**Frontend** (new terminal)
```bash
cd frontend
pip install -r requirements.txt

$env:BACKEND_URL = "http://localhost:8000"

streamlit run app/main.py
```

---

## Environment Variables

| Variable        | Required | Default                             | Description                                   |
|-----------------|----------|-------------------------------------|-----------------------------------------------|
| `GROQ_API_KEY`  | Yes*     | _(empty)_                           | Groq API key. Falls back to MockLLM if unset. |
| `GROQ_MODEL`    | No       | `llama-3.3-70b-versatile`           | Groq model to use                             |
| `DATABASE_URL`  | No       | `sqlite:///./database/studio.db`    | SQLAlchemy connection string                  |
| `BACKEND_URL`   | No       | `http://localhost:8000`             | Backend URL consumed by the frontend          |

*Without `GROQ_API_KEY` the app still works but uses a rule-based MockLLM.

---

## Features at a Glance

| Page                     | Key Features                                                               |
|--------------------------|----------------------------------------------------------------------------|
| Conversation Playground  | Groq-powered chat, knowledge grounding, real-time eval scores, feedback    |
| Knowledge Base           | Paste text or upload TXT/PDF/DOCX/CSV/MD files; auto text extraction       |
| Prompt Testing Lab       | Create versioned templates, run batch tests, compare outputs               |
| Governance & Audit       | Filter by hallucination risk / reviewer status; approve or flag responses  |
| Analytics Dashboard      | Conversation trends, quality scores over time, source usage charts         |

---

## Tech Stack

| Layer        | Technology                                         |
|--------------|----------------------------------------------------|
| LLM          | Groq API (`llama-3.3-70b-versatile`)               |
| Backend API  | FastAPI 0.115, Uvicorn, SQLAlchemy 2.0, Pydantic 2 |
| Database     | SQLite (file-based, zero-config)                   |
| Frontend     | Streamlit 1.38, Plotly, Pandas                     |
| File Parsing | PyPDF2, python-docx                                |
| Container    | Docker + Docker Compose                            |

---

## Seeding Demo Data

Click **"Seed Demo Data"** in the sidebar of any page to populate the database with sample conversations, evaluations, and feedback so you can explore all features immediately.

---

## Documentation Index

| Document                                              | Contents                                  |
|-------------------------------------------------------|-------------------------------------------|
| [README.md](README.md)                                | This file — setup & overview              |
| [architecture.md](architecture.md)                   | System architecture & component diagram   |
| [api_documentation.md](api_documentation.md)         | Full REST API reference                   |
| [database_schema.md](database_schema.md)             | Table definitions, columns, relationships |
| [assumptions.md](assumptions.md)                     | Design decisions and constraints          |
| [ai_tools_used.md](ai_tools_used.md)                 | AI tools, models, and libraries           |
