"""
Database engine + session factory + Base class for SQLAlchemy models.

Why this file exists:
  • Every model (User, Question, Session, ...) inherits from `Base`.
  • Every API request gets a fresh DB session via `get_db()`.
  • `init_db()` creates all tables on startup (good enough until we
    add Alembic migrations in Phase 5).
"""
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


# SQLite needs an extra connect arg; Postgres doesn't.
connect_args = (
    {"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {}
)

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    """Base class every ORM model inherits from."""


def init_db() -> None:
    """Create tables that don't exist yet."""
    # Importing models here ensures they are registered on `Base.metadata`
    # before `create_all` runs. Models are added in Phase 5.
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
