"""Governance / Audit Trail API routes."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Conversation, Evaluation, Feedback
from app.schemas.schemas import GovernanceRecord, ReviewUpdate

router = APIRouter(prefix="/api/governance", tags=["Governance"])


@router.get("/audit", response_model=list[GovernanceRecord])
def get_audit_trail(
    hallucination_risk: Optional[bool] = None,
    reviewer_status: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Return the full governance audit trail by joining conversations,
    evaluations, and feedback.
    """
    query = (
        db.query(Conversation, Evaluation, Feedback)
        .outerjoin(Evaluation, Evaluation.conversation_id == Conversation.id)
        .outerjoin(Feedback, Feedback.conversation_id == Conversation.id)
    )

    if hallucination_risk is not None:
        query = query.filter(Evaluation.hallucination_risk == hallucination_risk)

    if reviewer_status:
        query = query.filter(Feedback.reviewer_status == reviewer_status)

    if date_from:
        query = query.filter(Conversation.created_at >= date_from)

    if date_to:
        query = query.filter(Conversation.created_at <= date_to)

    rows = query.order_by(Conversation.created_at.desc()).limit(500).all()

    # Deduplicate by conversation_id (multiple feedbacks may exist)
    seen = set()
    records = []
    for conv, evaluation, feedback in rows:
        if conv.id in seen:
            continue
        seen.add(conv.id)
        records.append(
            GovernanceRecord(
                conversation_id=conv.id,
                prompt=conv.prompt,
                response=conv.response,
                created_at=conv.created_at,
                hallucination_risk=(
                    evaluation.hallucination_risk if evaluation else None
                ),
                reviewer_status=(
                    feedback.reviewer_status if feedback else None
                ),
                reviewer_name=(
                    feedback.reviewer_name if feedback else None
                ),
                relevance_score=(
                    evaluation.relevance_score if evaluation else None
                ),
                groundedness_score=(
                    evaluation.groundedness_score if evaluation else None
                ),
            )
        )

    return records


@router.patch("/review/{conversation_id}")
def update_review(
    conversation_id: int,
    payload: ReviewUpdate,
    db: Session = Depends(get_db),
):
    """Update the reviewer status for a conversation's feedback."""
    feedback = (
        db.query(Feedback)
        .filter(Feedback.conversation_id == conversation_id)
        .first()
    )
    if not feedback:
        # Create a new feedback entry with the review status
        feedback = Feedback(
            conversation_id=conversation_id,
            reviewer_status=payload.reviewer_status,
            reviewer_name=payload.reviewer_name or "admin",
        )
        db.add(feedback)
    else:
        feedback.reviewer_status = payload.reviewer_status
        feedback.reviewer_name = payload.reviewer_name or feedback.reviewer_name

    db.commit()
    db.refresh(feedback)
    return {"status": "updated", "conversation_id": conversation_id}
