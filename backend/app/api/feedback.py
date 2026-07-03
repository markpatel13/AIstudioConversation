"""Feedback API routes."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Feedback, Conversation
from app.schemas.schemas import FeedbackCreate, FeedbackResponse

router = APIRouter(prefix="/api/feedback", tags=["Feedback"])


@router.post("/", response_model=FeedbackResponse, status_code=201)
def create_feedback(payload: FeedbackCreate, db: Session = Depends(get_db)):
    """Submit human feedback for a conversation."""
    # Verify conversation exists
    conv = (
        db.query(Conversation)
        .filter(Conversation.id == payload.conversation_id)
        .first()
    )
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    feedback = Feedback(
        conversation_id=payload.conversation_id,
        thumbs_up=payload.thumbs_up,
        reviewer_name=payload.reviewer_name or "anonymous",
        reviewer_status=payload.reviewer_status or "pending",
        comments=payload.comments,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


@router.get("/", response_model=list[FeedbackResponse])
def list_feedback(db: Session = Depends(get_db)):
    """List all feedback entries."""
    return db.query(Feedback).order_by(Feedback.created_at.desc()).limit(500).all()


@router.get("/{conversation_id}", response_model=list[FeedbackResponse])
def get_feedback_for_conversation(
    conversation_id: int, db: Session = Depends(get_db)
):
    """Get all feedback for a specific conversation."""
    return (
        db.query(Feedback)
        .filter(Feedback.conversation_id == conversation_id)
        .order_by(Feedback.created_at.desc())
        .all()
    )
