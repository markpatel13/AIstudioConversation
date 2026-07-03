from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class KnowledgeSource(Base):
    __tablename__ = "knowledge_sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(String(512), nullable=True)  # comma-separated assistant names
    created_at = Column(DateTime, default=_utcnow)

    conversations = relationship("Conversation", back_populates="source")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), nullable=False, index=True)
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    latency_ms = Column(Float, nullable=True)
    source_id = Column(Integer, ForeignKey("knowledge_sources.id"), nullable=True)
    model_name = Column(String(64), default="mock-llm-v1")
    created_at = Column(DateTime, default=_utcnow)

    source = relationship("KnowledgeSource", back_populates="conversations")
    evaluation = relationship(
        "Evaluation", back_populates="conversation", uselist=False
    )
    feedbacks = relationship("Feedback", back_populates="conversation")


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(
        Integer, ForeignKey("conversations.id"), nullable=False, unique=True
    )
    relevance_score = Column(Float, default=0.0)
    groundedness_score = Column(Float, default=0.0)
    hallucination_risk = Column(Boolean, default=False)
    coherence_score = Column(Float, default=0.0)
    detail_scores = Column(Text, nullable=True)  # JSON string
    evaluated_at = Column(DateTime, default=_utcnow)

    conversation = relationship("Conversation", back_populates="evaluation")


class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(
        Integer, ForeignKey("conversations.id"), nullable=False
    )
    thumbs_up = Column(Boolean, nullable=True)
    reviewer_name = Column(String(128), default="anonymous")
    reviewer_status = Column(String(32), default="pending")  # pending|approved|flagged
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_utcnow)

    conversation = relationship("Conversation", back_populates="feedbacks")


class PromptTemplate(Base):
    __tablename__ = "prompt_templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), nullable=False)
    template_text = Column(Text, nullable=False)
    version = Column(Integer, default=1)
    test_inputs = Column(Text, nullable=True)  # JSON list of strings
    created_at = Column(DateTime, default=_utcnow)
