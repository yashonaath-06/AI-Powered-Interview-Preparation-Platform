"""
================================================================
 main.py  —  FastAPI application entry-point.

 Loads settings, builds the app, mounts every router under /api/.
================================================================
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config import settings
from app.database import init_db
from app.routers import (
    admin,
    analytics,
    auth,
    health,
    interviews,
    questions,
    resume,
    users,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
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
    version="0.2.0",
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
app.include_router(health.router,     prefix="/api",            tags=["health"])
app.include_router(auth.router,       prefix="/api/auth",       tags=["auth"])
app.include_router(users.router,      prefix="/api/users",      tags=["users"])
app.include_router(interviews.router, prefix="/api/interviews", tags=["interviews"])
app.include_router(questions.router,  prefix="/api/questions",  tags=["questions"])
app.include_router(resume.router,     prefix="/api/resume",     tags=["resume"])
app.include_router(analytics.router,  prefix="/api/analytics",  tags=["analytics"])
app.include_router(admin.router,      prefix="/api/admin",      tags=["admin"])


# ---- Friendly root ---------------------------------------------
@app.get("/", tags=["root"])
def root():
    return {
        "name": "AI Interview Preparation Platform API",
        "version": app.version,
        "docs": "/docs",
        "health": "/api/health",
    }
