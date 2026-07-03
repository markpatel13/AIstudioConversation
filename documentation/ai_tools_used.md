# AI Tools Used

This document lists every AI tool, model, API, and AI-assisted library used in the development and operation of AI Conversation Studio.

---

## 1. Core AI / LLM Runtime

### Groq API
- **Role:** Primary LLM inference engine for the Conversation Playground
- **Model:** `llama-3.3-70b-versatile` (default; configurable via `GROQ_MODEL` env var)
- **Endpoint:** `https://api.groq.com/openai/v1/chat/completions`
- **Usage:** Called on every chat request when `GROQ_API_KEY` is set. Receives a system prompt (optionally including knowledge source context) and the user's message; returns a generated response.
- **Why Groq:** Ultra-low latency inference (LPU hardware); generous free tier; OpenAI-compatible API; supports large open-weight models
- **Fallback:** If `GROQ_API_KEY` is absent or the call fails, the system transparently falls back to MockLLM

---

## 2. LLM Models

| Model | Provider | Context Window | Parameters | Usage in This Project |
|---|---|---|---|---|
| `llama-3.3-70b-versatile` | Meta via Groq | 128k tokens | 70B | Default chat model |
| _(configurable)_ | Groq-supported models | varies | varies | Any Groq-compatible model can be set via `GROQ_MODEL` |

**Other Groq models that can be plugged in:**
- `llama-3.1-8b-instant` — faster, lighter responses
- `mixtral-8x7b-32768` — MoE architecture with 32k context
- `gemma2-9b-it` — Google Gemma 2, instruction-tuned

---

## 3. AI-Assisted Development Tools

### Google Gemini / Antigravity (Antigravity IDE)
- **Role:** AI pair-programming assistant used throughout the development of this project
- **Contribution:**
  - Scaffolded the full project structure (FastAPI backend + Streamlit frontend)
  - Generated SQLAlchemy model definitions and Pydantic schemas
  - Wrote all API route handlers
  - Implemented the EvaluationService scoring logic
  - Designed and implemented the Groq LLM integration with MockLLM fallback
  - Added the file-upload knowledge endpoint with PDF/DOCX parsing
  - Rewrote the frontend UI with custom CSS for the clean dark theme
  - Generated all documentation files (this folder)
- **Version:** Claude Sonnet 4.6 (Thinking) via Antigravity IDE

---

## 4. AI Libraries & Services in the Stack

### EvaluationService (Custom Rule-Based AI)
- **File:** `backend/app/services/evaluation.py`
- **Type:** Deterministic keyword-overlap evaluator (no external model call)
- **Metrics produced:**
  - **Relevance Score** — TF-IDF-style keyword overlap between prompt and response
  - **Groundedness Score** — Keyword overlap between knowledge context and response (or 0.5 for free chat)
  - **Coherence Score** — Normalised average sentence length as a readability proxy
  - **Hallucination Risk** — Boolean flag triggered when groundedness < 0.3 AND coherence < 0.5

### MockLLM (Custom Rule-Based LLM)
- **File:** `backend/app/services/mock_llm.py`
- **Type:** Deterministic response generator; no external dependency
- **Purpose:** Allows full demo of all platform features without an API key
- **Behaviour:** Keyword detection for greetings, explanations, and uncertainty; template-based responses; 200–800ms simulated latency

---

## 5. AI-Adjacent Libraries

| Library | Version | Purpose |
|---|---|---|
| PyPDF2 | 3.0.1 | Text extraction from uploaded PDF knowledge sources |
| python-docx | 1.1.2 | Text extraction from uploaded DOCX knowledge sources |
| Plotly | 5.24.0 | Interactive charts in the Analytics Dashboard |
| Pandas | 2.2.2 | Data manipulation for analytics query results |

---

## 6. AI Concepts & Techniques Applied

| Technique | Where Applied | Description |
|---|---|---|
| **Retrieval-Augmented Generation (RAG)** | Chat page + knowledge API | User-selected knowledge source content is injected into the Groq system prompt as context |
| **LLM Response Evaluation** | EvaluationService | Automated scoring of every response using relevance, groundedness, and coherence metrics |
| **Hallucination Detection** | EvaluationService | Rule-based proxy flagging ungrounded responses for human review |
| **Human-in-the-Loop Feedback** | Feedback API + Governance page | Thumbs-up/down and reviewer status workflow for oversight |
| **Prompt Templating** | Prompt Testing Lab | Parameterised prompt templates with `{input}` tokens for systematic prompt engineering |
| **Batch Prompt Testing** | Prompt Testing API | Run multiple test inputs against a template and compare evaluation scores |

---

## 7. AI Safety & Governance Features

The platform is designed around **AI Governance** principles:

- **Transparency** — Every response shows its source model, latency, and evaluation scores
- **Auditability** — Full audit trail of all conversations with filters for hallucination risk and reviewer status
- **Human Oversight** — Reviewers can approve or flag any conversation from the Governance page
- **Knowledge Grounding** — Responses can be grounded to vetted knowledge sources to reduce hallucination
- **Feedback Loop** — Human feedback is stored and used to drive the Analytics quality trend charts

---

## 8. Tools Not Used (Considered & Rejected)

| Tool | Why Not Used |
|---|---|
| OpenAI API | Groq is faster and has a more accessible free tier |
| LangChain | Added complexity not needed for this scope; implemented RAG manually |
| ChromaDB / Pinecone | Vector stores add infrastructure overhead; full-document injection was sufficient for hackathon |
| LlamaIndex | Same rationale as LangChain |
| Hugging Face Inference API | Slower than Groq for same model sizes |
