import os
from pathlib import Path

# Database
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{DATABASE_DIR / 'studio.db'}"
)

# App
APP_TITLE = "AI Conversation Studio API"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = (
    "Governance & Observability layer for enterprise AI assistants. "
    "Provides knowledge management, conversation testing, response evaluation, "
    "human feedback, governance audit trails, and analytics dashboards."
)
