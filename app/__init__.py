"""Compatibility package for running the backend from the repository root.

This extends the `app` package search path so imports like `app.main` resolve
to the FastAPI application under `backend/app` when Uvicorn is started from
the repo root.
"""

from __future__ import annotations

from pathlib import Path
from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)

backend_app_path = Path(__file__).resolve().parent.parent / "backend" / "app"
if backend_app_path.exists():
    backend_app_str = str(backend_app_path)
    if backend_app_str not in __path__:
        __path__.append(backend_app_str)