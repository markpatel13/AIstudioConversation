# API Documentation

**Base URL:** `http://localhost:8000`  
**Interactive Docs:** `http://localhost:8000/docs` (Swagger UI)  
**Alternative Docs:** `http://localhost:8000/redoc`

All request and response bodies use **JSON** unless noted otherwise (file upload uses `multipart/form-data`).

---

## Table of Contents

1. [Health](#1-health)
2. [Knowledge Base](#2-knowledge-base)
3. [Chat](#3-chat)
4. [Feedback](#4-feedback)
5. [Prompt Templates](#5-prompt-templates)
6. [Governance](#6-governance)
7. [Analytics](#7-analytics)
8. [Seed](#8-seed)
9. [Common Schemas](#9-common-schemas)
10. [Error Responses](#10-error-responses)

---

## 1. Health

### `GET /`

Check that the backend is running.

**Response `200 OK`**
```json
{
  "status": "running",
  "app": "AI Conversation Studio",
  "version": "1.0.0",
  "docs": "/docs"
}
```

---

## 2. Knowledge Base

### `POST /api/knowledge/`

Create a knowledge source from plain text.

**Request Body**
```json
{
  "name": "Company FAQ",
  "content": "Our return policy is 30 days...",
  "tags": "faq, support"
}
```

| Field     | Type   | Required | Description                      |
|-----------|--------|----------|----------------------------------|
| `name`    | string | Yes      | Display name for the source      |
| `content` | string | Yes      | Full text content                |
| `tags`    | string | No       | Comma-separated tag labels       |

**Response `201 Created`** → [KnowledgeSourceResponse](#knowledgesourceresponse)

---

### `POST /api/knowledge/upload`

Upload a local file as a knowledge source. Text is extracted automatically.

**Content-Type:** `multipart/form-data`

| Field  | Type        | Required | Description                                        |
|--------|-------------|----------|----------------------------------------------------|
| `name` | string      | Yes      | Display name for the source (form field)           |
| `tags` | string      | No       | Comma-separated tags (form field)                  |
| `file` | binary file | Yes      | Supported: `.txt`, `.md`, `.csv`, `.pdf`, `.docx`  |

**Response `201 Created`** → [KnowledgeSourceResponse](#knowledgesourceresponse)

**Error `422`** — If text extraction fails or the file is empty.

---

### `GET /api/knowledge/`

List all knowledge sources ordered by creation date (newest first).

**Response `200 OK`** → `Array<`[KnowledgeSourceResponse](#knowledgesourceresponse)`>`

---

### `GET /api/knowledge/{source_id}`

Get a single knowledge source by ID.

**Path Parameters**

| Parameter   | Type    | Description         |
|-------------|---------|---------------------|
| `source_id` | integer | Knowledge source ID |

**Response `200 OK`** → [KnowledgeSourceResponse](#knowledgesourceresponse)  
**Error `404`** — Source not found.

---

### `DELETE /api/knowledge/{source_id}`

Delete a knowledge source permanently.

**Response `204 No Content`**  
**Error `404`** — Source not found.

---

## 3. Chat

### `POST /api/chat/`

Send a prompt to the AI assistant. Uses Groq API when `GROQ_API_KEY` is set, falls back to MockLLM otherwise.

**Request Body**
```json
{
  "prompt": "What is our refund policy?",
  "session_id": "abc12345",
  "source_id": 3
}
```

| Field        | Type    | Required | Description                                             |
|--------------|---------|----------|---------------------------------------------------------|
| `prompt`     | string  | Yes      | User message / question                                 |
| `session_id` | string  | No       | Session identifier for grouping. Auto-generated if omitted. |
| `source_id`  | integer | No       | ID of knowledge source to use as context                |

**Response `201 Created`** → [ChatResponse](#chatresponse)

**Example Response**
```json
{
  "id": 42,
  "session_id": "abc12345",
  "prompt": "What is our refund policy?",
  "response": "Based on the documentation, our return policy is 30 days...",
  "latency_ms": 834.21,
  "source_id": 3,
  "model_name": "llama-3.3-70b-versatile",
  "created_at": "2026-07-03T04:30:00Z",
  "evaluation": {
    "id": 38,
    "conversation_id": 42,
    "relevance_score": 0.87,
    "groundedness_score": 0.92,
    "hallucination_risk": false,
    "coherence_score": 0.84,
    "evaluated_at": "2026-07-03T04:30:01Z"
  }
}
```

---

### `GET /api/chat/history`

List conversation history, optionally filtered by session.

**Query Parameters**

| Parameter    | Type   | Required | Description                       |
|--------------|--------|----------|-----------------------------------|
| `session_id` | string | No       | Filter to a specific session      |

**Response `200 OK`** → `Array<`[ChatResponse](#chatresponse)`>` (max 200 items, newest first)

---

### `GET /api/chat/{conversation_id}`

Get a single conversation with its evaluation.

**Response `200 OK`** → [ChatResponse](#chatresponse)  
**Error `404`** — Conversation not found.

---

## 4. Feedback

### `POST /api/feedback/`

Submit human feedback for a conversation.

**Request Body**
```json
{
  "conversation_id": 42,
  "thumbs_up": true,
  "reviewer_name": "alice",
  "reviewer_status": "approved",
  "comments": "Accurate and concise."
}
```

| Field             | Type    | Required | Description                                       |
|-------------------|---------|----------|---------------------------------------------------|
| `conversation_id` | integer | Yes      | ID of the conversation being rated                |
| `thumbs_up`       | boolean | No       | `true` = positive, `false` = negative, `null` = neutral |
| `reviewer_name`   | string  | No       | Name of the human reviewer (default: `anonymous`) |
| `reviewer_status` | string  | No       | One of: `pending`, `approved`, `flagged`          |
| `comments`        | string  | No       | Free-text review notes                            |

**Response `201 Created`** → [FeedbackResponse](#feedbackresponse)

---

### `GET /api/feedback/`

List all feedback entries (max 500, newest first).

**Response `200 OK`** → `Array<`[FeedbackResponse](#feedbackresponse)`>`

---

### `GET /api/feedback/{conversation_id}`

Get all feedback entries for a specific conversation.

**Response `200 OK`** → `Array<`[FeedbackResponse](#feedbackresponse)`>`

---

## 5. Prompt Templates

### `POST /api/prompts/`

Create a new prompt template.

**Request Body**
```json
{
  "name": "Refund Helper v1",
  "template_text": "You are a customer support agent. Answer: {input}",
  "test_inputs": ["How do I get a refund?", "What is your policy?"]
}
```

| Field           | Type            | Required | Description                            |
|-----------------|-----------------|----------|----------------------------------------|
| `name`          | string          | Yes      | Template display name                  |
| `template_text` | string          | Yes      | Prompt template (use `{input}` token)  |
| `test_inputs`   | array of string | No       | Initial test cases                     |

**Response `201 Created`** → [PromptTemplateResponse](#prompttemplateresponse)

---

### `GET /api/prompts/`

List all prompt templates.

**Response `200 OK`** → `Array<`[PromptTemplateResponse](#prompttemplateresponse)`>`

---

### `DELETE /api/prompts/{template_id}`

Delete a prompt template.

**Response `204 No Content`**

---

### `POST /api/prompts/test`

Run a batch test against a template.

**Request Body**
```json
{
  "template_id": 5,
  "test_inputs": ["What is your return policy?", "Can I exchange an item?"]
}
```

**Response `200 OK`** → `Array<PromptTestResult>`
```json
[
  {
    "input_text": "What is your return policy?",
    "output_text": "Our return policy is 30 days...",
    "latency_ms": 620.5,
    "evaluation": { ... }
  }
]
```

---

## 6. Governance

### `GET /api/governance/audit`

Return the full audit trail with optional filters.

**Query Parameters**

| Parameter          | Type    | Required | Description                                   |
|--------------------|---------|----------|-----------------------------------------------|
| `hallucination_risk` | boolean | No     | Filter by hallucination risk flag             |
| `reviewer_status`  | string  | No       | One of: `pending`, `approved`, `flagged`      |
| `date_from`        | string  | No       | ISO date string — conversations after this    |
| `date_to`          | string  | No       | ISO date string — conversations before this   |

**Response `200 OK`** → `Array<GovernanceRecord>` (max 500)

```json
[
  {
    "conversation_id": 12,
    "prompt": "What is ML?",
    "response": "Machine learning is...",
    "created_at": "2026-07-02T12:00:00Z",
    "hallucination_risk": false,
    "reviewer_status": "approved",
    "reviewer_name": "alice",
    "relevance_score": 0.91,
    "groundedness_score": 0.88
  }
]
```

---

### `PATCH /api/governance/review/{conversation_id}`

Update the reviewer status for a conversation.

**Request Body**
```json
{
  "reviewer_status": "flagged",
  "reviewer_name": "bob"
}
```

| Field             | Type   | Required | Values                          |
|-------------------|--------|----------|---------------------------------|
| `reviewer_status` | string | Yes      | `pending`, `approved`, `flagged` |
| `reviewer_name`   | string | No       | Name of the reviewer            |

**Response `200 OK`**
```json
{
  "status": "updated",
  "conversation_id": 12
}
```

---

## 7. Analytics

### `GET /api/analytics/summary`

Aggregate analytics for the dashboard.

**Response `200 OK`** → [AnalyticsSummary](#analyticssummary)

```json
{
  "total_conversations": 248,
  "avg_relevance": 0.783,
  "avg_groundedness": 0.821,
  "hallucination_rate": 12.5,
  "positive_feedback_rate": 76.4,
  "conversations_by_day": [
    { "date": "2026-07-01", "count": 34 }
  ],
  "top_sources": [
    { "source_name": "Company FAQ", "usage_count": 112 }
  ],
  "quality_trend": [
    { "date": "2026-07-01", "avg_relevance": 0.79, "avg_groundedness": 0.83 }
  ],
  "feedback_over_time": [
    { "date": "2026-07-01", "positive_count": 28, "negative_count": 6 }
  ]
}
```

---

## 8. Seed

### `POST /api/seed/`

Populate the database with demo conversations, evaluations, and feedback.

**Response `200 OK`**
```json
{
  "status": "seeded",
  "conversations": 50
}
```

---

## 9. Common Schemas

### KnowledgeSourceResponse
```json
{
  "id": 1,
  "name": "Company FAQ",
  "content": "Full text...",
  "tags": "faq, support",
  "created_at": "2026-07-03T04:00:00Z"
}
```

### ChatResponse
```json
{
  "id": 1,
  "session_id": "abc12345",
  "prompt": "...",
  "response": "...",
  "latency_ms": 620.0,
  "source_id": null,
  "model_name": "llama-3.3-70b-versatile",
  "created_at": "2026-07-03T04:00:00Z",
  "evaluation": { ... }
}
```

### EvaluationResponse
```json
{
  "id": 1,
  "conversation_id": 1,
  "relevance_score": 0.87,
  "groundedness_score": 0.92,
  "hallucination_risk": false,
  "coherence_score": 0.84,
  "evaluated_at": "2026-07-03T04:00:01Z"
}
```

### FeedbackResponse
```json
{
  "id": 1,
  "conversation_id": 1,
  "thumbs_up": true,
  "reviewer_name": "alice",
  "reviewer_status": "approved",
  "comments": "Accurate.",
  "created_at": "2026-07-03T04:00:00Z"
}
```

### PromptTemplateResponse
```json
{
  "id": 1,
  "name": "Refund Helper v1",
  "template_text": "You are a support agent. Answer: {input}",
  "version": 1,
  "test_inputs": ["How do I return an item?"],
  "created_at": "2026-07-03T04:00:00Z"
}
```

### AnalyticsSummary
See [Analytics](#7-analytics) section above.

---

## 10. Error Responses

All error responses follow the FastAPI default format:

```json
{
  "detail": "Knowledge source not found"
}
```

| Status | Meaning                                           |
|--------|---------------------------------------------------|
| `400`  | Bad request — invalid input                       |
| `404`  | Resource not found                                |
| `422`  | Validation error or unprocessable content (e.g. unreadable file) |
| `500`  | Internal server error                             |
