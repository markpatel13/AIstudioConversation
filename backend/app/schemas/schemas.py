from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, field_validator, Field


# ──────────────────────────── Knowledge Source ────────────────────────────


class KnowledgeSourceCreate(BaseModel):
    name: str
    content: str
    tags: Optional[str] = None


class KnowledgeSourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    content: str
    tags: Optional[str] = None
    created_at: datetime


# ──────────────────────────── Evaluation ──────────────────────────────────


class EvaluationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    conversation_id: int
    relevance_score: float
    groundedness_score: float
    hallucination_risk: bool
    coherence_score: float
    evaluated_at: datetime


# ──────────────────────────── Chat ────────────────────────────────────────


class ChatRequest(BaseModel):
    prompt: str
    session_id: Optional[str] = None
    source_id: Optional[int] = None


class ChatResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: str
    prompt: str
    response: str
    latency_ms: float
    source_id: Optional[int] = None
    model_name: str
    created_at: datetime
    evaluation: Optional[EvaluationResponse] = None


# ──────────────────────────── Feedback ────────────────────────────────────


class FeedbackCreate(BaseModel):
    conversation_id: int
    thumbs_up: Optional[bool] = None
    reviewer_name: Optional[str] = "anonymous"
    reviewer_status: Optional[str] = "pending"
    comments: Optional[str] = None


class FeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    conversation_id: int
    thumbs_up: Optional[bool] = None
    reviewer_name: Optional[str] = None
    reviewer_status: Optional[str] = None
    comments: Optional[str] = None
    created_at: datetime


# ──────────────────────────── Prompt Templates ────────────────────────────


class PromptTemplateCreate(BaseModel):
    name: str
    template_text: str
    test_inputs: Optional[list[str]] = None


class PromptTemplateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    template_text: str
    version: int
    test_inputs: Optional[list[str]] = None
    created_at: datetime

    @field_validator("test_inputs", mode="before")
    @classmethod
    def parse_test_inputs(cls, v: Any) -> Optional[list[str]]:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return None
        return v


class PromptTestRun(BaseModel):
    template_id: int
    test_inputs: list[str]


class PromptTestResult(BaseModel):
    input_text: str
    output_text: str
    latency_ms: float
    evaluation: Optional[EvaluationResponse] = None


# ──────────────────────────── Governance ──────────────────────────────────


class GovernanceRecord(BaseModel):
    conversation_id: int
    prompt: str
    response: str
    created_at: datetime
    hallucination_risk: Optional[bool] = None
    reviewer_status: Optional[str] = None
    reviewer_name: Optional[str] = None
    relevance_score: Optional[float] = None
    groundedness_score: Optional[float] = None


class ReviewUpdate(BaseModel):
    reviewer_status: str
    reviewer_name: Optional[str] = "admin"


# ──────────────────────────── Analytics ───────────────────────────────────


class DayCount(BaseModel):
    date: str
    count: int


class SourceUsage(BaseModel):
    source_name: str
    usage_count: int


class QualityTrend(BaseModel):
    date: str
    avg_relevance: float
    avg_groundedness: float


class FeedbackTrend(BaseModel):
    date: str
    positive_count: int
    negative_count: int


class AnalyticsSummary(BaseModel):
    total_conversations: int
    avg_relevance: float
    avg_groundedness: float
    hallucination_rate: float
    positive_feedback_rate: float
    conversations_by_day: list[DayCount]
    top_sources: list[SourceUsage]
    quality_trend: list[QualityTrend]
    feedback_over_time: list[FeedbackTrend]
