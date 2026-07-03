"""
Seed Data API – populates the database with realistic demo data.

Creates knowledge sources, conversations spread over the last 30 days,
evaluations, feedback, and prompt templates so the dashboard and audit
trail have rich content during a demo.
"""

from __future__ import annotations

import json
import random
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import (
    Conversation,
    Evaluation,
    Feedback,
    KnowledgeSource,
    PromptTemplate,
)

router = APIRouter(prefix="/api/seed", tags=["Seed Data"])


# ── Knowledge-source content ─────────────────────────────────────────────

_SOURCES = [
    {
        "name": "AI & Machine Learning Handbook",
        "tags": "ai-assistant,ml-bot",
        "content": (
            "Artificial intelligence is the simulation of human intelligence "
            "by computer systems. Machine learning is a subset of AI that enables "
            "systems to learn from data. Deep learning uses neural networks with "
            "many layers. Natural language processing allows computers to understand "
            "human language. Reinforcement learning trains agents via reward signals. "
            "Transfer learning reuses knowledge from one task on another. "
            "Transformers are the architecture behind modern LLMs like GPT and BERT."
        ),
    },
    {
        "name": "Cloud Computing Guide",
        "tags": "cloud-assistant",
        "content": (
            "Cloud computing delivers computing services over the internet. "
            "Infrastructure as a Service provides virtualized computing resources. "
            "Platform as a Service offers a development environment in the cloud. "
            "Software as a Service delivers applications over the internet. "
            "Containers and Kubernetes enable microservice architectures. "
            "Serverless computing eliminates server management overhead. "
            "Multi-cloud strategies reduce vendor lock-in risks."
        ),
    },
    {
        "name": "Cybersecurity Best Practices",
        "tags": "security-bot",
        "content": (
            "Cybersecurity protects systems and data from digital attacks. "
            "Zero trust architecture verifies every access request. "
            "Encryption converts data into unreadable code without a key. "
            "Multi-factor authentication adds layers of identity verification. "
            "Penetration testing simulates attacks to find vulnerabilities. "
            "Security incident response plans outline steps after a breach. "
            "Regular patching and updates close known security gaps."
        ),
    },
    {
        "name": "Data Science Fundamentals",
        "tags": "data-assistant,analytics-bot",
        "content": (
            "Data science extracts insights from structured and unstructured data. "
            "Exploratory data analysis reveals patterns and anomalies. "
            "Feature engineering creates meaningful variables for models. "
            "Cross-validation prevents overfitting during model evaluation. "
            "A/B testing compares two versions to determine which performs better. "
            "Data pipelines automate the flow from ingestion to analysis. "
            "Statistical significance determines whether results are meaningful."
        ),
    },
    {
        "name": "Software Engineering Practices",
        "tags": "dev-assistant,code-bot",
        "content": (
            "Software engineering applies systematic approaches to software development. "
            "Agile methodology emphasizes iterative development and collaboration. "
            "Continuous integration merges code changes frequently. "
            "Test-driven development writes tests before implementation code. "
            "Code reviews improve quality and share knowledge across teams. "
            "Microservices decompose applications into small, independent services. "
            "DevOps bridges development and operations for faster delivery."
        ),
    },
]

_PROMPTS = [
    "What is machine learning and how does it work?",
    "Explain the benefits of cloud computing",
    "How can we improve cybersecurity in our organization?",
    "What are the key steps in a data science project?",
    "Describe agile software development methodology",
    "What is deep learning and how is it different from ML?",
    "How does containerization work with Kubernetes?",
    "Explain zero trust security architecture",
    "What is feature engineering in data science?",
    "How does continuous integration improve software quality?",
    "Tell me about transfer learning",
    "What is serverless computing?",
    "How do penetration tests work?",
    "Explain A/B testing in data science",
    "What are microservices?",
    "How do transformers work in NLP?",
    "What is multi-cloud strategy?",
    "Explain encryption methods",
    "What is test-driven development?",
    "How do data pipelines work?",
    "What is reinforcement learning?",
    "Describe IaaS vs PaaS vs SaaS",
    "How does multi-factor authentication work?",
    "What is cross-validation?",
    "Explain DevOps practices",
    "Hello, can you help me?",
    "I'm not sure what AI is, can you explain?",
    "Maybe tell me about neural networks?",
    "I think cloud computing is important, right?",
    "Perhaps you could describe data engineering?",
]

_REVIEWER_NAMES = ["Alice Chen", "Bob Smith", "Carol Davis", "Dave Wilson", "admin"]

_PROMPT_TEMPLATES = [
    {
        "name": "Knowledge Q&A",
        "template_text": "Based on our knowledge base, answer the following question: {input}",
        "test_inputs": [
            "What is machine learning?",
            "How does cloud computing work?",
            "What are cybersecurity best practices?",
        ],
    },
    {
        "name": "Summarizer",
        "template_text": "Provide a concise summary of the following topic: {input}",
        "test_inputs": [
            "artificial intelligence",
            "data science",
            "software engineering",
        ],
    },
    {
        "name": "Comparison",
        "template_text": "Compare and contrast the following concepts: {input}",
        "test_inputs": [
            "IaaS vs PaaS",
            "agile vs waterfall",
            "SQL vs NoSQL",
        ],
    },
]


def _random_past_datetime(days_back: int = 30) -> datetime:
    """Return a random datetime within the last *days_back* days."""
    offset = random.uniform(0, days_back * 24 * 3600)
    return datetime.now(timezone.utc) - timedelta(seconds=offset)


@router.post("/")
def seed_database(db: Session = Depends(get_db)):
    """Populate the database with realistic demo data."""

    # ── Knowledge sources ─────────────────────────────────────────────
    sources = []
    for src_data in _SOURCES:
        source = KnowledgeSource(
            name=src_data["name"],
            content=src_data["content"],
            tags=src_data["tags"],
            created_at=_random_past_datetime(60),
        )
        db.add(source)
        db.flush()
        sources.append(source)

    # ── Conversations, evaluations, feedback ──────────────────────────
    conversations_created = 0
    for prompt_text in _PROMPTS:
        source = random.choice(sources)
        dt = _random_past_datetime(30)

        # Mock response (simple rule-based for seed data)
        if any(g in prompt_text.lower() for g in ("hello", "hi", "hey")):
            response_text = (
                "Hello! I'm the AI Conversation Studio assistant. "
                "How can I help you today?"
            )
        elif any(w in prompt_text.lower() for w in ("i think", "maybe", "perhaps", "not sure")):
            response_text = (
                f"I think that's an interesting question about "
                f"{prompt_text.split()[-1] if prompt_text.split() else 'this topic'}. "
                "Perhaps there are multiple perspectives to consider, "
                "but I'm not entirely sure about all the details."
            )
        else:
            # Extract key sentences from source content
            sentences = [s.strip() for s in source.content.split(".") if s.strip()]
            picked = random.sample(sentences, min(2, len(sentences)))
            response_text = (
                "Based on the available documentation, "
                + ". ".join(picked)
                + ". This information is directly supported by the knowledge base."
            )

        conv = Conversation(
            session_id=f"seed-session-{random.randint(1, 5)}",
            prompt=prompt_text,
            response=response_text,
            latency_ms=round(random.uniform(200, 800), 2),
            source_id=source.id,
            model_name="mock-llm-v1",
            created_at=dt,
        )
        db.add(conv)
        db.flush()

        # Evaluation
        rel = round(random.uniform(0.3, 0.95), 3)
        grd = round(random.uniform(0.2, 0.90), 3)
        coh = round(random.uniform(0.5, 0.95), 3)
        hallucination = grd < 0.3 or any(
            p in response_text.lower()
            for p in ("i think", "maybe", "perhaps", "not sure")
        )

        ev = Evaluation(
            conversation_id=conv.id,
            relevance_score=rel,
            groundedness_score=grd,
            hallucination_risk=hallucination,
            coherence_score=coh,
            evaluated_at=dt + timedelta(seconds=1),
        )
        db.add(ev)

        # Feedback for ~70 % of conversations
        if random.random() < 0.70:
            fb = Feedback(
                conversation_id=conv.id,
                thumbs_up=random.choice([True, True, True, False]),  # 75 % positive
                reviewer_name=random.choice(_REVIEWER_NAMES),
                reviewer_status=random.choice(
                    ["approved", "approved", "approved", "flagged", "pending"]
                ),
                comments=random.choice(
                    [
                        "Good response, accurate information.",
                        "Could be more detailed.",
                        "Needs review for accuracy.",
                        "Excellent and well-grounded answer.",
                        None,
                    ]
                ),
                created_at=dt + timedelta(seconds=5),
            )
            db.add(fb)

        conversations_created += 1

    # ── Prompt templates ──────────────────────────────────────────────
    for tmpl_data in _PROMPT_TEMPLATES:
        tmpl = PromptTemplate(
            name=tmpl_data["name"],
            template_text=tmpl_data["template_text"],
            version=1,
            test_inputs=json.dumps(tmpl_data["test_inputs"]),
            created_at=_random_past_datetime(20),
        )
        db.add(tmpl)

    db.commit()

    return {
        "status": "seeded",
        "knowledge_sources": len(sources),
        "conversations": conversations_created,
        "prompt_templates": len(_PROMPT_TEMPLATES),
    }
