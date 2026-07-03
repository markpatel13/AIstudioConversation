# AI Conversation Studio

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?style=flat&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.29-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=flat&logo=sqlite&logoColor=white)

> A governance and observability platform for enterprise AI assistants. Provides knowledge management, conversation testing, response evaluation with explainable scoring, human feedback collection, governance audit trails, and analytics dashboards.

---

## Architecture

AI Conversation Studio uses a **3-tier architecture** designed for simplicity and rapid deployment:

| Layer | Technology | Role |
|---|---|---|
| **Frontend** | Streamlit | Multi-page app with dark theme, interactive Plotly charts, and real-time API integration |
| **Backend** | FastAPI | REST API with auto-generated OpenAPI docs, CRUD operations, Groq-backed chat with mock fallback, and evaluation pipeline |
| **Database** | SQLite via SQLAlchemy ORM | Zero-configuration persistent storage with full relational schema |
| **Deployment** | Docker Compose | Single-command setup with health checks, volume mounts, and service orchestration |

```
┌─────────────────────────────────────────────────────────┐
│                     Docker Compose                      │
│                                                         │
│  ┌──────────────────┐       ┌────────────────────────┐  │
│  │    Frontend       │       │       Backend          │  │
│  │   (Streamlit)     │──────▶│      (FastAPI)         │  │
│  │   Port: 8501      │  HTTP │      Port: 8000        │  │
│  │                   │       │                        │  │
│  │  • Knowledge Mgr  │       │  • REST API (/api/v1)  │  │
│  │  • Playground     │       │  • Mock LLM Engine     │  │
│  │  • Evaluation     │       │  • Eval Pipeline       │  │
│  │  • Prompt Lab     │       │  • CRUD Operations     │  │
│  │  • Governance     │       │                        │  │
│  │  • Analytics      │       │         │              │  │
│  └──────────────────┘       └─────────┼──────────────┘  │
│                                       │                 │
│                              ┌────────▼───────────┐     │
│                              │     Database       │     │
│                              │     (SQLite)       │     │
│                              │                    │     │
│                              │  • knowledge_items │     │
│                              │  • conversations   │     │
│                              │  • messages        │     │
│                              │  • evaluations     │     │
│                              │  • prompt_templates│     │
│                              └────────────────────┘     │
└─────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Using Docker (Recommended)

```bash
git clone <repo-url>
cd ai-conversation-studio
docker-compose up --build
```

Once running, access:
- **Frontend**: [http://localhost:8501](http://localhost:8501)
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **API Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)

### Local Development

**Backend:**
```bash
cd backend
pip install -r requirements.txt
copy ..\.env .env
uvicorn app.main:app --reload --port 8000
```

The backend loads environment variables from the project root `.env` file at startup, so keep `GROQ_API_KEY` and `GROQ_MODEL` there when running Uvicorn directly.

**Frontend** (in a separate terminal):
```bash
cd frontend
pip install -r requirements.txt
set BACKEND_URL=http://localhost:8000
streamlit run app/main.py
```

---

## Features

### 1. Knowledge Base Manager
Upload and manage knowledge sources (text documents) that serve as the ground-truth context for AI assistant responses. Supports create, read, update, and delete operations with content previews.

### 2. Conversation Playground
Interactive chat interface with a mock LLM engine. Send prompts, receive generated responses in real-time, and see evaluation scores alongside each response. Conversations are persisted for later review.

### 3. Response Evaluation
Automated, explainable scoring across four dimensions — **relevance**, **groundedness**, **hallucination risk**, and **coherence**. Every score includes a human-readable explanation of how it was computed.

### 4. Prompt Testing Lab
Create and version prompt templates with variable placeholders. Run batch tests across templates, compare outputs side-by-side, and track quality metrics over time.

### 5. Governance & Audit Trail
Browse all conversations with full message history. Reviewers can **approve** or **flag** conversations, attach notes, and maintain a complete audit trail for compliance and quality assurance.

### 6. Analytics Dashboard
Visual KPI dashboards built with Plotly — quality score trends over time, source usage distribution, feedback breakdown, and key performance indicators at a glance.

---

## Database Schema

| Table | Key Fields | Description |
|---|---|---|
| `knowledge_items` | `id`, `title`, `content`, `source_type`, `created_at` | Knowledge base documents used as context |
| `conversations` | `id`, `title`, `status`, `created_at`, `updated_at` | Chat sessions with lifecycle tracking |
| `messages` | `id`, `conversation_id`, `role`, `content`, `timestamp` | Individual messages within conversations |
| `evaluations` | `id`, `message_id`, `relevance_score`, `groundedness_score`, `hallucination_risk`, `coherence_score`, `explanation` | Scoring results for assistant responses |
| `prompt_templates` | `id`, `name`, `template`, `version`, `created_at` | Versioned prompt templates for testing |

---

## API Documentation

All endpoints are prefixed with `/api/v1`.

### Knowledge Base

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/knowledge` | List all knowledge items |
| `POST` | `/api/v1/knowledge` | Create a new knowledge item |
| `GET` | `/api/v1/knowledge/{id}` | Get a specific knowledge item |
| `PUT` | `/api/v1/knowledge/{id}` | Update a knowledge item |
| `DELETE` | `/api/v1/knowledge/{id}` | Delete a knowledge item |

### Conversations

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/conversations` | List all conversations |
| `POST` | `/api/v1/conversations` | Create a new conversation |
| `GET` | `/api/v1/conversations/{id}` | Get conversation with messages |
| `DELETE` | `/api/v1/conversations/{id}` | Delete a conversation |
| `POST` | `/api/v1/conversations/{id}/messages` | Send a message and get AI response |

### Evaluations

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/evaluations` | List all evaluations |
| `GET` | `/api/v1/evaluations/{message_id}` | Get evaluation for a message |

### Prompt Templates

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/prompts` | List all prompt templates |
| `POST` | `/api/v1/prompts` | Create a prompt template |
| `PUT` | `/api/v1/prompts/{id}` | Update a prompt template |
| `DELETE` | `/api/v1/prompts/{id}` | Delete a prompt template |
| `POST` | `/api/v1/prompts/{id}/test` | Test a prompt template |

### Governance

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/governance/{conversation_id}/review` | Submit a review (approve/flag) |
| `GET` | `/api/v1/governance/reviews` | List all reviews |

### Analytics

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/analytics/summary` | Get KPI summary |
| `GET` | `/api/v1/analytics/trends` | Get quality score trends |

> **Full interactive API documentation** is available at [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI) when the backend is running.

---

## Evaluation Methodology

The platform uses **explainable NLP heuristics** to score AI responses. Each metric is transparent and auditable:

| Metric | Range | How It's Computed |
|---|---|---|
| **Relevance Score** | 0.0 – 1.0 | Keyword overlap (Jaccard similarity) between the user prompt and the AI response. Higher scores indicate the response addresses the question's key terms. |
| **Groundedness Score** | 0.0 – 1.0 | Token overlap between the AI response and the knowledge base context. Measures how much of the response is grounded in provided source material. |
| **Hallucination Risk** | `true` / `false` | Flagged when groundedness < 0.3 **or** when uncertainty phrases are detected (e.g., "I think", "probably", "not sure"). Provides early warning for unverifiable claims. |
| **Coherence Score** | 0.0 – 1.0 | Based on response structure — sentence count, average length, and completeness. Well-structured, substantive responses score higher. |

Each evaluation includes a natural-language **explanation** summarizing the scoring rationale.

---

## Project Structure

```
ai-conversation-studio/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI entry point, CORS, routes
│   │   ├── models.py            # SQLAlchemy ORM models
│   │   ├── schemas.py           # Pydantic request/response schemas
│   │   ├── crud.py              # Database CRUD operations
│   │   └── engine.py            # Mock LLM + evaluation pipeline
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── main.py              # Streamlit multi-page app
│   │   └── components.py        # Reusable UI components
│   ├── Dockerfile
│   └── requirements.txt
├── database/
│   └── .gitkeep                 # Ensures directory exists in git
├── docker-compose.yml           # Service orchestration
├── .gitignore
└── README.md
```

---

## Technical Decisions & Assumptions

- **Groq Integration**: The backend uses Groq when `GROQ_API_KEY` is set and falls back to `MockLLM` when the key is missing or the request fails.
- **SQLite**: Chosen for zero-configuration setup and portability. The schema is designed to be compatible with PostgreSQL for production migration.
- **Explainable Evaluation**: NLP heuristics (token overlap, pattern matching) are used intentionally for transparency. Every score can be traced back to specific text evidence, unlike black-box ML models.
- **CORS**: Enabled with permissive settings for development convenience. Should be restricted to specific origins in production.
- **Authentication**: Skipped per project requirements. Governance workflows simulate reviewer identity via name input rather than authenticated sessions.

---

## AI Tools Used

- **Google Gemini (Antigravity IDE)**: Used for code generation, architecture design, and implementation across all project files.

---

## License

MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
