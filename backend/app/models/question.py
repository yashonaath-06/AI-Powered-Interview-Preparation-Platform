"""Interview question bank."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    text: Mapped[str] = mapped_column(Text)

    # technical | hr | behavioral
    category: Mapped[str] = mapped_column(String(50), index=True)
    # easy | medium | hard
    difficulty: Mapped[str] = mapped_column(String(20), default="medium")

    company: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    role: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)

    # JSON-encoded list of strings; SQLAlchemy stores as TEXT for portability
    expected_keywords: Mapped[str | None] = mapped_column(Text, nullable=True)
    sample_answer: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
