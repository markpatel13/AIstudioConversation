# Architecture Diagram

## System Overview

AI Conversation Studio is a two-service containerised application: a **FastAPI backend** that owns all data and AI logic, and a **Streamlit frontend** that provides the interactive user interface. Both services are orchestrated by Docker Compose and communicate over HTTP.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             User's Browser                                  │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │ HTTP  :8501
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        FRONTEND  (Streamlit :8501)                          │
│                                                                             │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────────┐  │
│  │  Conversation    │  │  Knowledge Base  │  │  Prompt Testing Lab      │  │
│  │  Playground      │  │  Manager         │  │                          │  │
│  │  (main.py)       │  │  (page 1)        │  │  (page 2)                │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────────────┘  │
│  ┌──────────────────┐  ┌──────────────────┐                                 │
│  │  Governance &    │  │  Analytics       │                                 │
│  │  Audit Trail     │  │  Dashboard       │                                 │
│  │  (page 3)        │  │  (page 4)        │                                 │
│  └──────────────────┘  └──────────────────┘                                 │
│                                                                             │
│                   api_client.py  (REST wrapper)                             │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │ HTTP  :8000
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        BACKEND  (FastAPI :8000)                             │
│                                                                             │
│  ┌─────────┐ ┌───────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────────┐ │
│  │  /api/  │ │  /api/    │ │  /api/   │ │  /api/   │ │  /api/            │ │
│  │  chat   │ │ knowledge │ │ feedback │ │governance│ │  analytics        │ │
│  └────┬────┘ └─────┬─────┘ └────┬─────┘ └────┬─────┘ └─────────┬─────────┘ │
│       │            │            │             │                 │           │
│  ┌────▼────────────▼────────────▼─────────────▼─────────────────▼─────────┐ │
│  │                      SQLAlchemy ORM Layer                               │ │
│  └────────────────────────────────┬────────────────────────────────────────┘ │
│                                   │                                         │
│  ┌─────────────────────────────────▼───────────────────────────────────┐    │
│  │                  SQLite Database  (studio.db)                        │    │
│  │  knowledge_sources | conversations | evaluations | feedbacks         │    │
│  │  prompt_templates                                                    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌──────────────────────┐   ┌─────────────────────────────────────────┐    │
│  │    GroqLLM Service   │   │         EvaluationService               │    │
│  │   (groq_llm.py)      │   │         (evaluation.py)                 │    │
│  └──────────┬───────────┘   └─────────────────────────────────────────┘    │
└─────────────┼───────────────────────────────────────────────────────────────┘
              │ HTTPS
              ▼
┌─────────────────────────────┐
│   Groq Cloud API            │
│   llama-3.3-70b-versatile   │
│   api.groq.com              │
└─────────────────────────────┘
```

---

## Component Descriptions

### Frontend (Streamlit)

| Component                 | File                          | Responsibility                                           |
|---------------------------|-------------------------------|----------------------------------------------------------|
| Conversation Playground   | `app/main.py`                 | Chat UI, knowledge source selector, feedback buttons     |
| Knowledge Base Manager    | `pages/1_Knowledge_Base.py`   | Create/upload/delete knowledge sources                   |
| Prompt Testing Lab        | `pages/2_Prompt_Testing.py`   | Manage templates, run batch tests, view results          |
| Governance & Audit Trail  | `pages/3_Governance.py`       | Filter and review conversations, update reviewer status  |
| Analytics Dashboard       | `pages/4_Analytics.py`        | Plotly charts for quality trends and usage stats         |
| API Client                | `utils/api_client.py`         | Typed wrapper for all backend REST calls                 |
| Styles                    | `components/styles.py`        | Shared CSS, score bar HTML helpers, sidebar renderer     |

---

### Backend (FastAPI)

| Module                    | Path                          | Responsibility                                            |
|---------------------------|-------------------------------|-----------------------------------------------------------|
| Chat API                  | `api/chat.py`                 | Receive prompt, call LLM, persist & evaluate, return     |
| Knowledge API             | `api/knowledge.py`            | CRUD + file-upload endpoint for knowledge sources         |
| Feedback API              | `api/feedback.py`             | Submit and retrieve human feedback                        |
| Governance API            | `api/governance.py`           | Audit trail with filters, reviewer status update          |
| Prompts API               | `api/prompts.py`              | Template CRUD and batch test runner                       |
| Analytics API             | `api/analytics.py`            | Aggregate SQL queries for dashboard metrics               |
| Seed API                  | `api/seed.py`                 | One-click demo data seeding                               |
| GroqLLM Service           | `services/groq_llm.py`        | Calls Groq API; falls back to MockLLM if key absent      |
| MockLLM Service           | `services/mock_llm.py`        | Deterministic keyword-based response generator            |
| EvaluationService         | `services/evaluation.py`      | Scores each response for relevance, groundedness, etc.    |
| ORM Models                | `models/models.py`            | SQLAlchemy table definitions                              |
| Pydantic Schemas          | `schemas/schemas.py`          | Request validation & response serialisation               |
| Database                  | `core/database.py`            | SQLite engine, session factory, Base                      |
| Config                    | `core/config.py`              | Environment variable loading                              |

---

## Request Flow — Chat Message

```
User types message
       │
       ▼
Streamlit frontend (main.py)
  → api_client.send_message(prompt, session_id, source_id)
       │  POST /api/chat/
       ▼
FastAPI  chat.py
  1. Fetch KnowledgeSource content (if source_id provided)
  2. Call GroqLLM.generate(prompt, context)
       │  HTTPS POST api.groq.com/openai/v1/chat/completions
       │  (or MockLLM if GROQ_API_KEY not set)
       ▼
  3. Persist Conversation row in SQLite
  4. EvaluationService.evaluate(prompt, response, context)
  5. Persist Evaluation row
  6. Return ChatResponse (with evaluation scores)
       │
       ▼
Streamlit renders chat bubble + evaluation expander
```

---

## Data Flow — File Upload (Knowledge Base)

```
User selects file in browser
       │
       ▼
Streamlit file_uploader widget
  → api_client.upload_knowledge_file(name, bytes, filename, tags)
       │  POST /api/knowledge/upload  (multipart/form-data)
       ▼
FastAPI  knowledge.py  _extract_text()
  .txt / .md / .csv  →  UTF-8 decode
  .pdf               →  PyPDF2 page extraction
  .docx              →  python-docx paragraph extraction
       │
       ▼
KnowledgeSource row saved to SQLite
       │
       ▼
Source appears in Knowledge Source selector on chat page
```

---

## Deployment Topology

```
Docker Host
├── studio-backend  (port 8000)   ←── GROQ_API_KEY, DATABASE_URL
│   └── volume: ./database        (SQLite file persisted on host)
└── studio-frontend (port 8501)   ←── BACKEND_URL=http://backend:8000
```

Both containers share a Docker bridge network. The frontend never touches the database directly — it always goes through the backend REST API.
