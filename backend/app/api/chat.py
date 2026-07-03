"""Chat API routes – conversation playground backend."""

from __future__ import annotations

import os
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Conversation, Evaluation, KnowledgeSource
from app.schemas.schemas import ChatRequest, ChatResponse, EvaluationResponse
from app.services.groq_llm import GroqLLM
from app.services.evaluation import EvaluationService

router = APIRouter(prefix="/api/chat", tags=["Chat"])

_llm = GroqLLM()
_evaluator = EvaluationService()


@router.post("/", response_model=ChatResponse, status_code=201)
def send_message(payload: ChatRequest, db: Session = Depends(get_db)):
    """
    Send a prompt to the LLM (Groq when key is set, MockLLM otherwise),
    log the conversation, auto-evaluate, and return the response with scores.
    """
    session_id = payload.session_id or str(uuid.uuid4())

    # Fetch context from knowledge source if provided
    context: Optional[str] = None
    if payload.source_id:
        source = (
            db.query(KnowledgeSource)
            .filter(KnowledgeSource.id == payload.source_id)
            .first()
        )
        if not source:
            raise HTTPException(status_code=404, detail="Knowledge source not found")
        context = source.content

    # Generate response via Groq (falls back to MockLLM if no key)
    response_text, latency_ms = _llm.generate(payload.prompt, context)

    # Persist conversation
    conversation = Conversation(
        session_id=session_id,
        prompt=payload.prompt,
        response=response_text,
        latency_ms=latency_ms,
        source_id=payload.source_id,
        model_name=_llm.model_name,
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    # Auto-evaluate
    eval_scores = _evaluator.evaluate(payload.prompt, response_text, context)
    evaluation = Evaluation(
        conversation_id=conversation.id,
        **eval_scores,
    )
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)

    # Build response
    return ChatResponse(
        id=conversation.id,
        session_id=conversation.session_id,
        prompt=conversation.prompt,
        response=conversation.response,
        latency_ms=conversation.latency_ms,
        source_id=conversation.source_id,
        model_name=conversation.model_name,
        created_at=conversation.created_at,
        evaluation=EvaluationResponse.model_validate(evaluation),
    )


@router.get("/history", response_model=list[ChatResponse])
def get_chat_history(
    session_id: Optional[str] = None, db: Session = Depends(get_db)
):
    """List conversations, optionally filtered by session_id."""
    query = db.query(Conversation).order_by(Conversation.created_at.desc())
    if session_id:
        query = query.filter(Conversation.session_id == session_id)
    conversations = query.limit(200).all()

    results = []
    for conv in conversations:
        eval_resp = None
        if conv.evaluation:
            eval_resp = EvaluationResponse.model_validate(conv.evaluation)
        results.append(
            ChatResponse(
                id=conv.id,
                session_id=conv.session_id,
                prompt=conv.prompt,
                response=conv.response,
                latency_ms=conv.latency_ms or 0,
                source_id=conv.source_id,
                model_name=conv.model_name,
                created_at=conv.created_at,
                evaluation=eval_resp,
            )
        )
    return results


@router.get("/{conversation_id}", response_model=ChatResponse)
def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """Get a single conversation with its evaluation."""
    conv = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    eval_resp = None
    if conv.evaluation:
        eval_resp = EvaluationResponse.model_validate(conv.evaluation)
    return ChatResponse(
        id=conv.id,
        session_id=conv.session_id,
        prompt=conv.prompt,
        response=conv.response,
        latency_ms=conv.latency_ms or 0,
        source_id=conv.source_id,
        model_name=conv.model_name,
        created_at=conv.created_at,
        evaluation=eval_resp,
    )
