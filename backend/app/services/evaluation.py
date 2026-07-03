"""
Evaluation Service
==================
Provides explainable, heuristic-based scoring for LLM responses.

Scores
------
- **relevance_score** (0-1): keyword overlap between prompt and response
- **groundedness_score** (0-1): how much the response overlaps with the
  knowledge-source context
- **hallucination_risk** (bool): True when groundedness < 0.3 or response
  contains uncertainty language
- **coherence_score** (0-1): structural quality (sentence count, length,
  punctuation)

All heuristics are deliberately simple and transparent so the "explainability"
requirement is satisfied without needing a black-box ML model.
"""

from __future__ import annotations

import json
import re
from typing import Optional


_UNCERTAINTY_PHRASES = [
    "i think",
    "maybe",
    "perhaps",
    "not sure",
    "might be",
    "possibly",
    "i believe",
    "it seems",
    "could be",
    "uncertain",
    "don't know",
    "not certain",
]


def _tokenize(text: str) -> set[str]:
    """Lower-case word tokeniser (alpha-only)."""
    return set(re.findall(r"[a-z]{2,}", text.lower()))


def _jaccard(set_a: set[str], set_b: set[str]) -> float:
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


class EvaluationService:
    """Heuristic evaluator for a single prompt/response pair."""

    def evaluate(
        self,
        prompt: str,
        response: str,
        context: Optional[str] = None,
    ) -> dict:
        """Return a dict of evaluation scores."""
        prompt_tokens = _tokenize(prompt)
        response_tokens = _tokenize(response)

        relevance = self._relevance(prompt_tokens, response_tokens)
        groundedness = self._groundedness(response_tokens, context)
        coherence = self._coherence(response)
        hallucination = self._hallucination_risk(response, groundedness)

        detail = {
            "prompt_token_count": len(prompt_tokens),
            "response_token_count": len(response_tokens),
            "overlap_tokens": len(prompt_tokens & response_tokens),
            "uncertainty_phrases_found": [
                p for p in _UNCERTAINTY_PHRASES if p in response.lower()
            ],
        }

        return {
            "relevance_score": round(relevance, 3),
            "groundedness_score": round(groundedness, 3),
            "hallucination_risk": hallucination,
            "coherence_score": round(coherence, 3),
            "detail_scores": json.dumps(detail),
        }

    # ── scoring helpers ───────────────────────────────────────────────

    @staticmethod
    def _relevance(prompt_tokens: set[str], response_tokens: set[str]) -> float:
        """Jaccard similarity between prompt and response tokens."""
        base = _jaccard(prompt_tokens, response_tokens)
        # Boost slightly if response is substantially longer (likely elaborates)
        length_ratio = min(len(response_tokens) / max(len(prompt_tokens), 1), 3.0)
        boost = min(length_ratio * 0.1, 0.2)
        return min(base + boost, 1.0)

    @staticmethod
    def _groundedness(response_tokens: set[str], context: Optional[str]) -> float:
        """Overlap between response and the knowledge-source context."""
        if context is None:
            return 0.5  # neutral when no context available
        context_tokens = _tokenize(context)
        return _jaccard(response_tokens, context_tokens)

    @staticmethod
    def _coherence(response: str) -> float:
        """Heuristic coherence based on structural signals."""
        score = 0.5  # baseline

        sentences = [s.strip() for s in re.split(r"[.!?]", response) if s.strip()]
        n_sentences = len(sentences)

        # Longer, multi-sentence responses are more coherent
        if n_sentences >= 2:
            score += 0.15
        if n_sentences >= 3:
            score += 0.10

        # Proper length
        word_count = len(response.split())
        if 10 <= word_count <= 200:
            score += 0.1
        elif word_count > 200:
            score += 0.05  # very long can be less coherent

        # Ends with punctuation
        if response.strip() and response.strip()[-1] in ".!?":
            score += 0.05

        # Starts with uppercase
        if response.strip() and response.strip()[0].isupper():
            score += 0.05

        return min(score, 1.0)

    @staticmethod
    def _hallucination_risk(response: str, groundedness: float) -> bool:
        """Flag hallucination if groundedness is low or uncertainty detected."""
        if groundedness < 0.3:
            return True
        response_lower = response.lower()
        uncertainty_count = sum(
            1 for p in _UNCERTAINTY_PHRASES if p in response_lower
        )
        return uncertainty_count >= 2
