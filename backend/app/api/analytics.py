"""Analytics API routes – aggregate dashboard data."""

from __future__ import annotations

from sqlalchemy import func, case, cast, Date
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends

from app.core.database import get_db
from app.models.models import Conversation, Evaluation, Feedback, KnowledgeSource
from app.schemas.schemas import (
    AnalyticsSummary,
    DayCount,
    SourceUsage,
    QualityTrend,
    FeedbackTrend,
)

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
def get_analytics_summary(db: Session = Depends(get_db)):
    """Return aggregate analytics for the dashboard."""

    # ── Total conversations ───────────────────────────────────────────
    total_conversations = db.query(func.count(Conversation.id)).scalar() or 0

    # ── Average scores ────────────────────────────────────────────────
    avg_relevance = (
        db.query(func.avg(Evaluation.relevance_score)).scalar() or 0.0
    )
    avg_groundedness = (
        db.query(func.avg(Evaluation.groundedness_score)).scalar() or 0.0
    )

    # ── Hallucination rate ────────────────────────────────────────────
    total_evals = db.query(func.count(Evaluation.id)).scalar() or 0
    hallucination_count = (
        db.query(func.count(Evaluation.id))
        .filter(Evaluation.hallucination_risk == True)  # noqa: E712
        .scalar()
        or 0
    )
    hallucination_rate = (
        (hallucination_count / total_evals * 100) if total_evals else 0.0
    )

    # ── Positive feedback rate ────────────────────────────────────────
    total_feedback = db.query(func.count(Feedback.id)).scalar() or 0
    positive_feedback = (
        db.query(func.count(Feedback.id))
        .filter(Feedback.thumbs_up == True)  # noqa: E712
        .scalar()
        or 0
    )
    positive_feedback_rate = (
        (positive_feedback / total_feedback * 100) if total_feedback else 0.0
    )

    # ── Conversations by day ──────────────────────────────────────────
    day_counts_raw = (
        db.query(
            func.date(Conversation.created_at).label("date"),
            func.count(Conversation.id).label("count"),
        )
        .group_by(func.date(Conversation.created_at))
        .order_by(func.date(Conversation.created_at))
        .all()
    )
    conversations_by_day = [
        DayCount(date=str(row.date), count=row.count) for row in day_counts_raw
    ]

    # ── Top knowledge sources ─────────────────────────────────────────
    source_usage_raw = (
        db.query(
            KnowledgeSource.name,
            func.count(Conversation.id).label("usage_count"),
        )
        .join(Conversation, Conversation.source_id == KnowledgeSource.id)
        .group_by(KnowledgeSource.name)
        .order_by(func.count(Conversation.id).desc())
        .limit(10)
        .all()
    )
    top_sources = [
        SourceUsage(source_name=row.name, usage_count=row.usage_count)
        for row in source_usage_raw
    ]

    # ── Quality trend ─────────────────────────────────────────────────
    quality_raw = (
        db.query(
            func.date(Conversation.created_at).label("date"),
            func.avg(Evaluation.relevance_score).label("avg_rel"),
            func.avg(Evaluation.groundedness_score).label("avg_grd"),
        )
        .join(Evaluation, Evaluation.conversation_id == Conversation.id)
        .group_by(func.date(Conversation.created_at))
        .order_by(func.date(Conversation.created_at))
        .all()
    )
    quality_trend = [
        QualityTrend(
            date=str(row.date),
            avg_relevance=round(row.avg_rel or 0, 3),
            avg_groundedness=round(row.avg_grd or 0, 3),
        )
        for row in quality_raw
    ]

    # ── Feedback over time ────────────────────────────────────────────
    feedback_raw = (
        db.query(
            func.date(Feedback.created_at).label("date"),
            func.sum(case((Feedback.thumbs_up == True, 1), else_=0)).label(  # noqa: E712
                "positive"
            ),
            func.sum(case((Feedback.thumbs_up == False, 1), else_=0)).label(  # noqa: E712
                "negative"
            ),
        )
        .group_by(func.date(Feedback.created_at))
        .order_by(func.date(Feedback.created_at))
        .all()
    )
    feedback_over_time = [
        FeedbackTrend(
            date=str(row.date),
            positive_count=int(row.positive or 0),
            negative_count=int(row.negative or 0),
        )
        for row in feedback_raw
    ]

    return AnalyticsSummary(
        total_conversations=total_conversations,
        avg_relevance=round(avg_relevance, 3),
        avg_groundedness=round(avg_groundedness, 3),
        hallucination_rate=round(hallucination_rate, 1),
        positive_feedback_rate=round(positive_feedback_rate, 1),
        conversations_by_day=conversations_by_day,
        top_sources=top_sources,
        quality_trend=quality_trend,
        feedback_over_time=feedback_over_time,
    )
