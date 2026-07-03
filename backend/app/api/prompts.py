"""Prompt Testing / Versioning API routes."""

from __future__ import annotations

import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import PromptTemplate
from app.schemas.schemas import (
    PromptTemplateCreate,
    PromptTemplateResponse,
    PromptTestRun,
    PromptTestResult,
    EvaluationResponse,
)
from app.services.mock_llm import MockLLM
from app.services.evaluation import EvaluationService

router = APIRouter(prefix="/api/prompts", tags=["Prompt Testing"])

_llm = MockLLM()
_evaluator = EvaluationService()


@router.post("/", response_model=PromptTemplateResponse, status_code=201)
def create_prompt_template(
    payload: PromptTemplateCreate, db: Session = Depends(get_db)
):
    """Create a new prompt template."""
    test_inputs_json = (
        json.dumps(payload.test_inputs) if payload.test_inputs else None
    )

    # Auto-increment version if a template with same name exists
    existing = (
        db.query(PromptTemplate)
        .filter(PromptTemplate.name == payload.name)
        .order_by(PromptTemplate.version.desc())
        .first()
    )
    version = (existing.version + 1) if existing else 1

    template = PromptTemplate(
        name=payload.name,
        template_text=payload.template_text,
        version=version,
        test_inputs=test_inputs_json,
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.get("/", response_model=list[PromptTemplateResponse])
def list_prompt_templates(db: Session = Depends(get_db)):
    """List all prompt templates."""
    return (
        db.query(PromptTemplate)
        .order_by(PromptTemplate.created_at.desc())
        .all()
    )


@router.post("/test", response_model=list[PromptTestResult])
def run_prompt_test(payload: PromptTestRun, db: Session = Depends(get_db)):
    """
    Run a prompt template against multiple test inputs.

    The template_text should contain ``{input}`` as a placeholder that gets
    replaced with each test input.
    """
    template = (
        db.query(PromptTemplate)
        .filter(PromptTemplate.id == payload.template_id)
        .first()
    )
    if not template:
        raise HTTPException(status_code=404, detail="Prompt template not found")

    results: list[PromptTestResult] = []
    for test_input in payload.test_inputs:
        # Replace {input} placeholder
        prompt_text = template.template_text.replace("{input}", test_input)

        # Generate and evaluate
        response_text, latency_ms = _llm.generate(prompt_text)
        eval_scores = _evaluator.evaluate(prompt_text, response_text)

        # Build a lightweight evaluation response (no DB persistence for tests)
        eval_resp = EvaluationResponse(
            id=0,
            conversation_id=0,
            relevance_score=eval_scores["relevance_score"],
            groundedness_score=eval_scores["groundedness_score"],
            hallucination_risk=eval_scores["hallucination_risk"],
            coherence_score=eval_scores["coherence_score"],
            evaluated_at=template.created_at,  # placeholder
        )

        results.append(
            PromptTestResult(
                input_text=test_input,
                output_text=response_text,
                latency_ms=latency_ms,
                evaluation=eval_resp,
            )
        )

    return results


@router.delete("/{template_id}", status_code=204)
def delete_prompt_template(template_id: int, db: Session = Depends(get_db)):
    """Delete a prompt template."""
    template = (
        db.query(PromptTemplate)
        .filter(PromptTemplate.id == template_id)
        .first()
    )
    if not template:
        raise HTTPException(status_code=404, detail="Prompt template not found")
    db.delete(template)
    db.commit()
