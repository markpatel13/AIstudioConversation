"""Evaluation API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Conversation, Evaluation, KnowledgeSource
from app.schemas.schemas import EvaluationResponse
from app.services.evaluation import EvaluationService

router = APIRouter(prefix="/api/evaluation", tags=["Evaluation"])

_evaluator = EvaluationService()


@router.get("/{conversation_id}", response_model=EvaluationResponse)
def get_evaluation(conversation_id: int, db: Session = Depends(get_db)):
    """Get the evaluation for a specific conversation."""
    evaluation = (
        db.query(Evaluation)
        .filter(Evaluation.conversation_id == conversation_id)
        .first()
    )
    if not evaluation:
        raise HTTPException(
            status_code=404, detail="Evaluation not found for this conversation"
        )
    return evaluation


@router.post("/re-evaluate/{conversation_id}", response_model=EvaluationResponse)
def re_evaluate(conversation_id: int, db: Session = Depends(get_db)):
    """Re-run evaluation for an existing conversation."""
    conv = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Get context if source was used
    context = None
    if conv.source_id:
        source = (
            db.query(KnowledgeSource)
            .filter(KnowledgeSource.id == conv.source_id)
            .first()
        )
        if source:
            context = source.content

    eval_scores = _evaluator.evaluate(conv.prompt, conv.response, context)

    # Update or create evaluation
    existing = (
        db.query(Evaluation)
        .filter(Evaluation.conversation_id == conversation_id)
        .first()
    )
    if existing:
        for key, value in eval_scores.items():
            setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        return existing
    else:
        evaluation = Evaluation(conversation_id=conversation_id, **eval_scores)
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        return evaluation
