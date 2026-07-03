# Database Schema

**Database Engine:** SQLite (file: `database/studio.db`)  
**ORM:** SQLAlchemy 2.0  
**Schema Management:** Tables are auto-created on first startup via `Base.metadata.create_all()`

---

## Entity Relationship Diagram

```
┌──────────────────────────────┐
│       knowledge_sources      │
│──────────────────────────────│
│ PK  id           INTEGER     │
│     name         VARCHAR(256)│
│     content      TEXT        │
│     tags         VARCHAR(512)│
│     created_at   DATETIME    │
└──────────────┬───────────────┘
               │ 1
               │
               │ 0..*
┌──────────────▼───────────────┐         ┌──────────────────────────────┐
│         conversations        │  1   0..1│         evaluations          │
│──────────────────────────────│──────────│──────────────────────────────│
│ PK  id           INTEGER     │         │ PK  id              INTEGER   │
│     session_id   VARCHAR(64) │         │ FK  conversation_id INTEGER   │
│     prompt       TEXT        │         │     relevance_score  FLOAT    │
│     response     TEXT        │         │     groundedness_score FLOAT  │
│     latency_ms   FLOAT       │         │     hallucination_risk BOOLEAN│
│ FK  source_id    INTEGER     │         │     coherence_score  FLOAT    │
│     model_name   VARCHAR(64) │         │     detail_scores   TEXT(JSON)│
│     created_at   DATETIME    │         │     evaluated_at    DATETIME  │
└──────────────┬───────────────┘         └──────────────────────────────┘
               │ 1
               │
               │ 0..*
┌──────────────▼───────────────┐
│           feedbacks          │
│──────────────────────────────│
│ PK  id              INTEGER  │
│ FK  conversation_id INTEGER  │
│     thumbs_up       BOOLEAN  │
│     reviewer_name   VARCHAR  │
│     reviewer_status VARCHAR  │
│     comments        TEXT     │
│     created_at      DATETIME │
└──────────────────────────────┘

┌──────────────────────────────┐
│       prompt_templates       │
│──────────────────────────────│
│ PK  id            INTEGER    │
│     name          VARCHAR    │
│     template_text TEXT       │
│     version       INTEGER    │
│     test_inputs   TEXT(JSON) │
│     created_at    DATETIME   │
└──────────────────────────────┘
```

---

## Table Definitions

### `knowledge_sources`

Stores uploaded or manually-created knowledge sources used to ground AI responses.

| Column       | Type          | Constraints              | Description                                 |
|--------------|---------------|--------------------------|---------------------------------------------|
| `id`         | INTEGER       | PK, autoincrement        | Unique row identifier                       |
| `name`       | VARCHAR(256)  | NOT NULL                 | Human-readable display name                 |
| `content`    | TEXT          | NOT NULL                 | Full plain-text content of the source       |
| `tags`       | VARCHAR(512)  | nullable                 | Comma-separated tag labels                  |
| `created_at` | DATETIME      | default = UTC now        | Timestamp of creation                       |

**Relationships:**
- One `KnowledgeSource` → many `Conversation` (via `conversations.source_id`)

---

### `conversations`

Central fact table. Records every prompt/response pair along with session context.

| Column       | Type         | Constraints               | Description                                       |
|--------------|--------------|---------------------------|---------------------------------------------------|
| `id`         | INTEGER      | PK, autoincrement         | Unique conversation ID                            |
| `session_id` | VARCHAR(64)  | NOT NULL, indexed         | Groups related turns in the same session          |
| `prompt`     | TEXT         | NOT NULL                  | Raw user message                                  |
| `response`   | TEXT         | NOT NULL                  | AI-generated response text                        |
| `latency_ms` | FLOAT        | nullable                  | End-to-end response time in milliseconds          |
| `source_id`  | INTEGER      | FK → knowledge_sources.id | NULL = free chat, non-null = RAG-grounded chat    |
| `model_name` | VARCHAR(64)  | default = `mock-llm-v1`   | Name of the LLM used (e.g. `llama-3.3-70b-versatile`) |
| `created_at` | DATETIME     | default = UTC now         | Timestamp of the conversation turn                |

**Relationships:**
- Many `Conversation` → one `KnowledgeSource` (nullable FK)
- One `Conversation` → one `Evaluation` (uselist=False)
- One `Conversation` → many `Feedback`

---

### `evaluations`

Stores automated quality scores for every conversation. One row per conversation (1:1).

| Column               | Type     | Constraints               | Description                                         |
|----------------------|----------|---------------------------|-----------------------------------------------------|
| `id`                 | INTEGER  | PK, autoincrement         | Unique evaluation ID                                |
| `conversation_id`    | INTEGER  | FK, NOT NULL, UNIQUE      | Links to `conversations.id`                         |
| `relevance_score`    | FLOAT    | default = 0.0             | 0–1 score: how relevant the response is to the prompt |
| `groundedness_score` | FLOAT    | default = 0.0             | 0–1 score: how grounded the response is in the context |
| `hallucination_risk` | BOOLEAN  | default = False           | True if the response appears ungrounded             |
| `coherence_score`    | FLOAT    | default = 0.0             | 0–1 score: logical and linguistic coherence         |
| `detail_scores`      | TEXT     | nullable                  | JSON blob for extended scoring breakdown            |
| `evaluated_at`       | DATETIME | default = UTC now         | Timestamp when evaluation was computed              |

**Scoring Logic (EvaluationService):**
- **Relevance** — keyword overlap between prompt words and response words
- **Groundedness** — if context provided: keyword overlap between context and response; else 0.5
- **Coherence** — average sentence length normalised to 0–1
- **Hallucination Risk** — flagged when `groundedness < 0.3` AND `coherence < 0.5`

---

### `feedbacks`

Human reviewer feedback for a conversation. One conversation can have multiple feedback entries (e.g. from different reviewers).

| Column             | Type         | Constraints                   | Description                                            |
|--------------------|--------------|-------------------------------|--------------------------------------------------------|
| `id`               | INTEGER      | PK, autoincrement             | Unique feedback ID                                     |
| `conversation_id`  | INTEGER      | FK, NOT NULL                  | Links to `conversations.id`                            |
| `thumbs_up`        | BOOLEAN      | nullable                      | `True` = positive, `False` = negative, `NULL` = neutral |
| `reviewer_name`    | VARCHAR(128) | default = `anonymous`         | Name of the human reviewer                             |
| `reviewer_status`  | VARCHAR(32)  | default = `pending`           | One of: `pending`, `approved`, `flagged`               |
| `comments`         | TEXT         | nullable                      | Free-text reviewer notes                               |
| `created_at`       | DATETIME     | default = UTC now             | Timestamp of feedback submission                       |

---

### `prompt_templates`

Stores versioned prompt templates for the Prompt Testing Lab feature.

| Column          | Type         | Constraints           | Description                                          |
|-----------------|--------------|-----------------------|------------------------------------------------------|
| `id`            | INTEGER      | PK, autoincrement     | Unique template ID                                   |
| `name`          | VARCHAR(256) | NOT NULL              | Display name for the template                        |
| `template_text` | TEXT         | NOT NULL              | Prompt text; use `{input}` as the user-input token   |
| `version`       | INTEGER      | default = 1           | Incremented manually for tracking                    |
| `test_inputs`   | TEXT         | nullable              | JSON-encoded list of test strings                    |
| `created_at`    | DATETIME     | default = UTC now     | Timestamp of creation                                |

---

## Indexes

| Table           | Column       | Type    | Purpose                                    |
|-----------------|--------------|---------|--------------------------------------------|
| `conversations` | `session_id` | B-Tree  | Fast session-based conversation filtering  |

All primary keys are implicitly indexed by SQLite.

---

## Notes

- **No migrations tool** — Schema is created fresh on first run. For schema changes in production, recreate the database or write manual `ALTER TABLE` scripts.
- **SQLite limitations** — Not suitable for high-concurrency production workloads. Swap `DATABASE_URL` for a PostgreSQL URI to scale out.
- **JSON columns** — `detail_scores` (evaluations) and `test_inputs` (prompt_templates) are stored as JSON strings in a TEXT column. They are deserialised in the Pydantic layer.
- **Timestamps** — All `created_at` fields use UTC timezone via `datetime.now(timezone.utc)`.
