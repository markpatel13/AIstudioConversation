# Assumptions

This document records the key design decisions, constraints, and assumptions made during the development of AI Conversation Studio.

---

## 1. Deployment & Infrastructure

| # | Assumption | Rationale |
|---|------------|-----------|
| 1.1 | Docker Compose is the primary deployment method | Ensures identical environments across machines; avoids "works on my machine" issues |
| 1.2 | A single Docker host with shared-volume SQLite is sufficient for the hackathon | Simplifies setup; no cloud DB account or credentials required |
| 1.3 | Ports `8000` (backend) and `8501` (frontend) are available on the host | Standard defaults; expected to be unoccupied in a demo environment |
| 1.4 | Internet access is available for the backend container | Required to reach `api.groq.com` for LLM inference |

---

## 2. LLM & AI

| # | Assumption | Rationale |
|---|------------|-----------|
| 2.1 | The Groq API is the primary LLM provider | Groq offers the fastest open-weight model inference available; free tier is sufficient for a hackathon demo |
| 2.2 | `llama-3.3-70b-versatile` is the default model | Strong general-purpose model with 128k context; good balance of quality and speed |
| 2.3 | The app is fully functional without a Groq API key | A deterministic MockLLM provides responses so reviewers can explore all features even without an API key |
| 2.4 | The system prompt is stateless per turn | Chat history is stored in the frontend session state only; the backend does not maintain multi-turn context with Groq |
| 2.5 | Max 1024 output tokens per Groq request is sufficient | Covers typical question-answer scenarios; adjustable via the `max_tokens` parameter in `groq_llm.py` |

---

## 3. Knowledge Base & RAG

| # | Assumption | Rationale |
|---|------------|-----------|
| 3.1 | Full-document retrieval (not chunked) is acceptable for the hackathon | Avoids the complexity of a vector database and embedding pipeline while still grounding responses |
| 3.2 | The entire knowledge source content is passed as context | Works well for short-to-medium documents; Groq's 128k context window handles most realistic cases |
| 3.3 | Files up to a few MB are acceptable uploads | SQLite TEXT columns have no practical size limit; Groq's context window is the binding constraint |
| 3.4 | PDF and DOCX parsing is best-effort | PyPDF2 does not always extract text from scanned PDFs; users should upload text-based documents for best results |
| 3.5 | Only one knowledge source can ground a chat session at a time | Keeps the UI simple; multi-source retrieval would require a more complex RAG pipeline |

---

## 4. Evaluation

| # | Assumption | Rationale |
|---|------------|-----------|
| 4.1 | Evaluation is rule-based (keyword overlap), not LLM-as-a-judge | Avoids a second LLM call per turn (latency and cost); suitable for demonstrating the evaluation pipeline concept |
| 4.2 | Scores are on a 0–1 scale | Intuitive for humans; maps directly to percentage displays in the UI |
| 4.3 | Hallucination risk is inferred from low groundedness + low coherence | A lightweight proxy; not a true hallucination detector |
| 4.4 | Every chat response is auto-evaluated immediately | Enables real-time feedback display without a separate evaluation step |

---

## 5. Data & Security

| # | Assumption | Rationale |
|---|------------|-----------|
| 5.1 | No authentication or authorisation is implemented | Scope limited to local/demo use; adding OAuth would take more time than allowed |
| 5.2 | All data is stored locally in a SQLite file | No cloud database costs; data stays on the demo machine |
| 5.3 | The Groq API key is provided via environment variable and never stored in code | Follows security best practice; `.env` is in `.gitignore` |
| 5.4 | Conversation data (prompts and responses) may be sent to Groq's servers | Groq's API terms apply; users should not submit sensitive PII in the demo |
| 5.5 | CORS is open (`*`) on the backend | Acceptable for a local demo; must be restricted before any production deployment |

---

## 6. Frontend & UX

| # | Assumption | Rationale |
|---|------------|-----------|
| 6.1 | Streamlit is an appropriate frontend framework for this scope | Rapid prototyping; built-in data widgets; no separate JS build step |
| 6.2 | The app targets desktop browsers | Streamlit's responsive layout works on desktop; mobile was not tested |
| 6.3 | Chat history is stored in Streamlit session state (in-memory) | Simplifies state management; history is lost on page refresh (full history is still in the DB) |
| 6.4 | A single reviewer persona is assumed | The governance/feedback system supports named reviewers but multi-user sessions are not isolated |

---

## 7. Scalability

| # | Assumption | Rationale |
|---|------------|-----------|
| 7.1 | Concurrency requirements are low (single-user demo) | SQLite has write-lock limitations; adequate for a hackathon but not production |
| 7.2 | Analytics queries run over the full dataset (no pagination beyond 200/500 row limits) | Simplifies the query layer; acceptable for demo-scale data volumes |
| 7.3 | The seed data endpoint is safe to run multiple times | Seed data has deterministic IDs; running it twice will create duplicates (acceptable for demo) |

---

## 8. Out of Scope

The following were considered but intentionally excluded from this submission:

- Vector embeddings / semantic search for knowledge retrieval
- Multi-turn memory sent to the LLM on each call
- User authentication / multi-tenant access control
- Production database (PostgreSQL / MySQL)
- CI/CD pipeline
- Unit and integration test suite
- Rate limiting and API key rotation
- Mobile-optimised UI
