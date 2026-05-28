"""Interview sessions and individual answers."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    company: Mapped[str | None] = mapped_column(String(100), nullable=True)
    role: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # technical | hr | behavioral | mixed
    interview_type: Mapped[str] = mapped_column(String(30))

    # in_progress | completed | abandoned
    status: Mapped[str] = mapped_column(String(20), default="in_progress", index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    overall_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    # JSON of {technical, communication, confidence, engagement, ...}
    scores_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    # JSON list of question IDs in the order they will be asked
    planned_question_ids: Mapped[str | None] = mapped_column(Text, nullable=True)
    num_questions: Mapped[int] = mapped_column(Integer, default=5)

    user: Mapped["User"] = relationship("User", back_populates="sessions")  # noqa: F821
    answers: Mapped[list["Answer"]] = relationship(
        "Answer", back_populates="session", cascade="all, delete-orphan"
    )


class Answer(Base):
    __tablename__ = "answers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("interview_sessions.id"), index=True
    )
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), index=True)

    transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)

    # All scores stored as JSON for flexibility
    nlp_scores: Mapped[str | None] = mapped_column(Text, nullable=True)
    vision_scores: Mapped[str | None] = mapped_column(Text, nullable=True)
    combined_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    session: Mapped["InterviewSession"] = relationship(
        "InterviewSession", back_populates="answers"
    )
