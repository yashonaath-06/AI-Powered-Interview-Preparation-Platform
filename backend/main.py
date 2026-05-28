"""
================================================================
 main.py  —  Application entry-point for the FastAPI backend.

 What this file does:
   1. Loads settings from .env
   2. Creates the FastAPI app
   3. Configures CORS (so the frontend can call the backend)
   4. Mounts every router under /api/...
   5. Provides /health and / endpoints used by Docker & humans

 In later phases this file barely changes — we just add new
 routers to the `routers` list below.
================================================================
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config import settings
from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run once at startup and once at shutdown."""
    logger.info("🚀 Starting AI Interview Prep backend...")
    init_db()
    logger.info("✅ Database initialized.")
    yield
    logger.info("👋 Shutting down.")


app = FastAPI(
    title="AI Interview Preparation Platform — API",
    description=(
        "Backend API for the AI-Powered Interview Preparation Platform. "
        "Provides authentication, the interview engine, NLP / vision / "
        "speech analysis, resume parsing, and analytics."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# ---- CORS ------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---- Routers ---------------------------------------------------
# (Routers are added phase by phase. They live in app/routers/.)
from app.routers import health  # noqa: E402

app.include_router(health.router, prefix="/api", tags=["health"])


# ---- Friendly root ---------------------------------------------
@app.get("/", tags=["root"])
def root():
    return {
        "name": "AI Interview Preparation Platform API",
        "version": app.version,
        "docs": "/docs",
        "health": "/api/health",
    }
