# Documentation Index

**Project:** AI Conversation Studio  
**Team:** Phonon  
**Submission Type:** Hackathon Round

---

## Submission Checklist

| Deliverable              | Status | File / Location                          |
|--------------------------|--------|------------------------------------------|
| Source code              | Done   | `/backend/` and `/frontend/`             |
| Working demo             | Done   | Run via `docker-compose up --build`      |
| Architecture diagram     | Done   | [architecture.md](architecture.md)       |
| README                   | Done   | [README.md](README.md)                   |
| API documentation        | Done   | [api_documentation.md](api_documentation.md) |
| Database schema          | Done   | [database_schema.md](database_schema.md) |
| Assumptions              | Done   | [assumptions.md](assumptions.md)         |
| AI tools used            | Done   | [ai_tools_used.md](ai_tools_used.md)     |
| 5-minute demo video      | Done   | _(recorded separately)_                  |
| Presentation             | Done   | _(slides submitted separately)_          |

---

## Document Summaries

### [README.md](README.md)
The main project guide. Covers what the app does, the full directory structure, how to run it with Docker Compose or locally, all environment variables, a feature table, tech stack, and links back to this index.

### [architecture.md](architecture.md)
System architecture with ASCII diagrams showing the two-service setup (FastAPI backend + Streamlit frontend), component responsibility tables, the step-by-step chat request flow, the file-upload data flow, and the Docker deployment topology.

### [api_documentation.md](api_documentation.md)
Complete REST API reference for all 8 route groups: Health, Knowledge Base (including file upload), Chat, Feedback, Prompt Templates, Governance, Analytics, and Seed. Includes request/response schemas, query parameters, example JSON bodies, and error codes.

### [database_schema.md](database_schema.md)
Full database documentation for SQLite. Includes an ASCII ERD, column-by-column table definitions for all 5 tables (`knowledge_sources`, `conversations`, `evaluations`, `feedbacks`, `prompt_templates`), indexes, scoring logic, and migration notes.

### [assumptions.md](assumptions.md)
Numbered list of design decisions and constraints across 8 categories: Deployment, LLM & AI, Knowledge Base, Evaluation, Data & Security, Frontend/UX, Scalability, and Out-of-Scope items. Each assumption includes the rationale.

### [ai_tools_used.md](ai_tools_used.md)
Catalogue of every AI tool, model, and technique used: Groq API (llama-3.3-70b-versatile), Gemini/Antigravity IDE (AI pair programming), custom EvaluationService, MockLLM, RAG pattern, hallucination detection, human-in-the-loop feedback, and prompt templating. Also lists tools considered but not used.

---

## Quick Start (for judges)

```bash
# 1. Set your Groq API key
cp .env.example .env
# Edit .env → paste GROQ_API_KEY=gsk_...

# 2. Launch
docker-compose up --build

# 3. Open
# Frontend → http://localhost:8501
# API Docs → http://localhost:8000/docs
```

No Groq key? The app still works with a built-in MockLLM — just skip step 1.
