"""
Groq LLM Service
================
Real LLM integration using the Groq API.  Falls back to MockLLM when
GROQ_API_KEY is not set or the call fails.
"""

from __future__ import annotations

import os
import time
from typing import Optional

from app.services.mock_llm import MockLLM

_GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
_GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

_mock = MockLLM()


def _build_system_prompt(context: Optional[str]) -> str:
    if context:
        return (
            "You are a helpful AI assistant. Answer the user's question using the "
            "following knowledge base context. Be concise and accurate.\n\n"
            f"Context:\n{context}"
        )
    return (
        "You are a helpful, friendly, and concise AI assistant. "
        "Answer the user's questions clearly and accurately."
    )


class GroqLLM:
    """Calls the Groq Chat Completions API; falls back to MockLLM on error."""

    def __init__(self) -> None:
        self._key = _GROQ_API_KEY
        self._model = _GROQ_MODEL

    def generate(
        self, prompt: str, context: Optional[str] = None
    ) -> tuple[str, float]:
        """
        Generate a response.  Returns (response_text, latency_ms).
        """
        if not self._key:
            # No API key configured – fall back to mock
            return _mock.generate(prompt, context)

        import requests  # local import to avoid hard dependency at module load

        start = time.perf_counter()
        try:
            messages = [
                {"role": "system", "content": _build_system_prompt(context)},
                {"role": "user", "content": prompt},
            ]
            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self._key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self._model,
                    "messages": messages,
                    "max_tokens": 1024,
                    "temperature": 0.7,
                },
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            text = data["choices"][0]["message"]["content"].strip()
            latency_ms = (time.perf_counter() - start) * 1000
            return text, round(latency_ms, 2)

        except Exception as exc:
            # If Groq call fails, fall back to mock and log the error
            print(f"[GroqLLM] Error: {exc} – falling back to MockLLM")
            return _mock.generate(prompt, context)

    @property
    def model_name(self) -> str:
        if self._key:
            return self._model
        return "mock-llm-v1"
