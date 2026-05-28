"""Uploaded resumes + AI analysis results."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    filename: Mapped[str] = mapped_column(String(255))
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    parsed_skills: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON
    target_role: Mapped[str | None] = mapped_column(String(100), nullable=True)
    match_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    ai_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    user: Mapped["User"] = relationship("User", back_populates="resumes")  # noqa: F821
