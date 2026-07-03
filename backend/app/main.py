"""
AI Conversation Studio – FastAPI Application
=============================================
Main entry point for the backend API server.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import APP_TITLE, APP_VERSION, APP_DESCRIPTION
from app.core.database import init_db

# Import routers
from app.api.knowledge import router as knowledge_router
from app.api.chat import router as chat_router
from app.api.evaluation import router as evaluation_router
from app.api.feedback import router as feedback_router
from app.api.prompts import router as prompts_router
from app.api.governance import router as governance_router
from app.api.analytics import router as analytics_router
from app.api.seed import router as seed_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    init_db()
    yield


app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    lifespan=lifespan,
)

# ── CORS (allow everything for dev) ──────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register routers ─────────────────────────────────────────────────────

app.include_router(knowledge_router)
app.include_router(chat_router)
app.include_router(evaluation_router)
app.include_router(feedback_router)
app.include_router(prompts_router)
app.include_router(governance_router)
app.include_router(analytics_router)
app.include_router(seed_router)


# ── Root health endpoint ─────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    return {
        "status": "running",
        "app": "AI Conversation Studio",
        "version": APP_VERSION,
        "docs": "/docs",
    }
