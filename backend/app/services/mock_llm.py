"""
Mock LLM Service
================
Simulates an LLM by generating rule-based responses.  When a knowledge-source
context is provided the response incorporates snippets from it; otherwise a
generic, keyword-driven answer is produced.

No real API keys are required – this is intentionally a deterministic mock
so that the evaluation / governance layers have meaningful text to score.
"""

from __future__ import annotations

import random
import re
import time
from typing import Optional


# ── Canned templates for variety ──────────────────────────────────────────

_GREETING_RESPONSES = [
    "Hello! I'm the AI Conversation Studio assistant. How can I help you today?",
    "Hi there! Welcome to the AI Conversation Studio. What would you like to explore?",
    "Hey! Great to see you. I'm ready to help with any questions you have.",
]

_EXPLANATION_PREFIXES = [
    "Great question! Let me explain: ",
    "That's an interesting topic. Here's what I know: ",
    "Sure, I'd be happy to explain. ",
]

_GENERIC_RESPONSES = [
    "Based on my knowledge, {topic} is a complex subject with many facets. "
    "Key considerations include scalability, security, and maintainability. "
    "I recommend starting with a thorough requirements analysis.",
    "The concept of {topic} involves several important aspects. "
    "In practice, organizations typically approach this through a combination "
    "of best practices and iterative improvement.",
    "{topic} is an evolving field. Current best practices suggest focusing "
    "on automation, monitoring, and continuous feedback loops to ensure quality.",
]

_UNCERTAINTY_PHRASES = [
    "I think this might be related to {topic}, but I'm not entirely sure.",
    "Perhaps {topic} could be relevant here, though there may be other factors.",
    "It's possible that {topic} plays a role, but maybe you should verify this.",
]

_CONTEXT_RESPONSE_TEMPLATES = [
    "Based on the available documentation, {snippet}. "
    "This is directly supported by the knowledge base sources.",
    "According to our knowledge base: {snippet}. "
    "This information has been verified against the stored documents.",
    "The documentation indicates that {snippet}. "
    "I'd recommend reviewing the full source for additional details.",
]


class MockLLM:
    """Generates mock LLM responses with simulated latency."""

    def generate(
        self, prompt: str, context: Optional[str] = None
    ) -> tuple[str, float]:
        """
        Generate a response for *prompt*, optionally grounded in *context*.

        Returns
        -------
        tuple[str, float]
            (response_text, latency_ms)
        """
        start = time.perf_counter()

        # Simulate model "thinking" time (200-800 ms)
        time.sleep(random.uniform(0.2, 0.8))

        prompt_lower = prompt.lower().strip()

        if context:
            response = self._context_response(prompt_lower, context)
        else:
            response = self._keyword_response(prompt_lower)

        latency_ms = (time.perf_counter() - start) * 1000
        return response, round(latency_ms, 2)

    # ── private helpers ───────────────────────────────────────────────

    @staticmethod
    def _extract_topic(prompt: str) -> str:
        """Pull a rough topic from the prompt for template insertion."""
        stop_words = {
            "what", "is", "the", "a", "an", "how", "does", "do", "can",
            "you", "me", "about", "explain", "tell", "please", "hi",
            "hello", "hey", "describe", "define", "why", "when", "where",
            "who", "which", "will", "would", "should", "could", "i",
            "my", "your", "it", "this", "that", "of", "in", "to", "for",
            "and", "or", "with", "on", "at", "by", "from", "are", "was",
        }
        words = re.findall(r"[a-z]+", prompt)
        meaningful = [w for w in words if w not in stop_words]
        return " ".join(meaningful[:5]) if meaningful else "this topic"

    def _keyword_response(self, prompt: str) -> str:
        topic = self._extract_topic(prompt)

        # Greetings
        if any(g in prompt for g in ("hello", "hi ", "hey", "greetings")):
            return random.choice(_GREETING_RESPONSES)

        # Explanation requests
        if any(w in prompt for w in ("explain", "describe", "define", "what is")):
            prefix = random.choice(_EXPLANATION_PREFIXES)
            body = random.choice(_GENERIC_RESPONSES).format(topic=topic)
            return prefix + body

        # Deliberately uncertain ~20 % of the time (to trigger hallucination flags)
        if random.random() < 0.20:
            return random.choice(_UNCERTAINTY_PHRASES).format(topic=topic)

        return random.choice(_GENERIC_RESPONSES).format(topic=topic)

    def _context_response(self, prompt: str, context: str) -> str:
        """Pick relevant sentences from *context* and wrap in a template."""
        sentences = [s.strip() for s in context.split(".") if len(s.strip()) > 20]
        if not sentences:
            # Fall back to keyword response if context has no usable sentences
            return self._keyword_response(prompt)

        prompt_words = set(re.findall(r"[a-z]+", prompt))

        # Score each sentence by keyword overlap
        scored = []
        for sent in sentences:
            sent_words = set(re.findall(r"[a-z]+", sent.lower()))
            overlap = len(prompt_words & sent_words)
            scored.append((overlap, sent))
        scored.sort(key=lambda x: x[0], reverse=True)

        # Take top-2 sentences
        top = [s for _, s in scored[:2]]
        snippet = ". ".join(top)

        return random.choice(_CONTEXT_RESPONSE_TEMPLATES).format(snippet=snippet)
