"""
API Client
==========
Wraps all backend REST API calls for the Streamlit frontend.
Handles errors gracefully – returns empty data rather than crashing the UI.
"""

from __future__ import annotations

import os
from typing import Any, Optional

import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


class APIClient:
    """Typed wrapper around the AI Conversation Studio backend API."""

    def __init__(self, base_url: str = BACKEND_URL):
        self.base_url = base_url.rstrip("/")
        self.timeout = 30

    # ── helpers ────────────────────────────────────────────────────────

    def _get(self, path: str, params: dict | None = None) -> Any:
        try:
            resp = requests.get(
                f"{self.base_url}{path}", params=params, timeout=self.timeout
            )
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.ConnectionError:
            st.error("⚠️ Cannot connect to the backend. Is it running?")
            return None
        except Exception as exc:
            st.error(f"API error: {exc}")
            return None

    def _post(self, path: str, json_data: dict | None = None) -> Any:
        try:
            resp = requests.post(
                f"{self.base_url}{path}", json=json_data, timeout=self.timeout
            )
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.ConnectionError:
            st.error("⚠️ Cannot connect to the backend. Is it running?")
            return None
        except Exception as exc:
            st.error(f"API error: {exc}")
            return None

    def _delete(self, path: str) -> bool:
        try:
            resp = requests.delete(
                f"{self.base_url}{path}", timeout=self.timeout
            )
            resp.raise_for_status()
            return True
        except Exception as exc:
            st.error(f"API error: {exc}")
            return False

    def _patch(self, path: str, json_data: dict | None = None) -> Any:
        try:
            resp = requests.patch(
                f"{self.base_url}{path}", json=json_data, timeout=self.timeout
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            st.error(f"API error: {exc}")
            return None

    # ── Knowledge ─────────────────────────────────────────────────────

    def create_knowledge_source(
        self, name: str, content: str, tags: str | None = None
    ) -> dict | None:
        return self._post(
            "/api/knowledge/",
            {"name": name, "content": content, "tags": tags},
        )

    def list_knowledge_sources(self) -> list[dict]:
        return self._get("/api/knowledge/") or []

    def delete_knowledge_source(self, source_id: int) -> bool:
        return self._delete(f"/api/knowledge/{source_id}")

    def upload_knowledge_file(
        self,
        name: str,
        file_bytes: bytes,
        filename: str,
        tags: str = "",
    ) -> dict | None:
        """Upload a local file as a knowledge source via multipart POST."""
        try:
            resp = requests.post(
                f"{self.base_url}/api/knowledge/upload",
                data={"name": name, "tags": tags},
                files={"file": (filename, file_bytes)},
                timeout=60,
            )
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to the backend. Is it running?")
            return None
        except Exception as exc:
            st.error(f"Upload error: {exc}")
            return None

    # ── Chat ──────────────────────────────────────────────────────────

    def send_message(
        self,
        prompt: str,
        session_id: str | None = None,
        source_id: int | None = None,
    ) -> dict | None:
        payload: dict[str, Any] = {"prompt": prompt}
        if session_id:
            payload["session_id"] = session_id
        if source_id:
            payload["source_id"] = source_id
        return self._post("/api/chat/", payload)

    def get_chat_history(self, session_id: str | None = None) -> list[dict]:
        params = {}
        if session_id:
            params["session_id"] = session_id
        return self._get("/api/chat/history", params=params) or []

    # ── Feedback ──────────────────────────────────────────────────────

    def submit_feedback(
        self,
        conversation_id: int,
        thumbs_up: bool | None = None,
        reviewer_name: str = "anonymous",
        comments: str | None = None,
        reviewer_status: str = "pending",
    ) -> dict | None:
        return self._post(
            "/api/feedback/",
            {
                "conversation_id": conversation_id,
                "thumbs_up": thumbs_up,
                "reviewer_name": reviewer_name,
                "comments": comments,
                "reviewer_status": reviewer_status,
            },
        )

    def get_feedback(self, conversation_id: int | None = None) -> list[dict]:
        if conversation_id:
            return self._get(f"/api/feedback/{conversation_id}") or []
        return self._get("/api/feedback/") or []

    # ── Prompts ───────────────────────────────────────────────────────

    def create_prompt_template(
        self, name: str, template_text: str, test_inputs: list[str] | None = None
    ) -> dict | None:
        return self._post(
            "/api/prompts/",
            {
                "name": name,
                "template_text": template_text,
                "test_inputs": test_inputs,
            },
        )

    def list_prompt_templates(self) -> list[dict]:
        return self._get("/api/prompts/") or []

    def run_prompt_test(
        self, template_id: int, test_inputs: list[str]
    ) -> list[dict]:
        return (
            self._post(
                "/api/prompts/test",
                {"template_id": template_id, "test_inputs": test_inputs},
            )
            or []
        )

    def delete_prompt_template(self, template_id: int) -> bool:
        return self._delete(f"/api/prompts/{template_id}")

    # ── Governance ────────────────────────────────────────────────────

    def get_audit_trail(
        self,
        hallucination_risk: bool | None = None,
        reviewer_status: str | None = None,
    ) -> list[dict]:
        params: dict[str, Any] = {}
        if hallucination_risk is not None:
            params["hallucination_risk"] = hallucination_risk
        if reviewer_status:
            params["reviewer_status"] = reviewer_status
        return self._get("/api/governance/audit", params=params) or []

    def update_review(
        self,
        conversation_id: int,
        reviewer_status: str,
        reviewer_name: str = "admin",
    ) -> dict | None:
        return self._patch(
            f"/api/governance/review/{conversation_id}",
            {"reviewer_status": reviewer_status, "reviewer_name": reviewer_name},
        )

    # ── Analytics ─────────────────────────────────────────────────────

    def get_analytics_summary(self) -> dict | None:
        return self._get("/api/analytics/summary")

    # ── Seed ──────────────────────────────────────────────────────────

    def seed_database(self) -> dict | None:
        return self._post("/api/seed/")


@st.cache_resource
def get_client() -> APIClient:
    """Return a singleton API client instance."""
    return APIClient()
