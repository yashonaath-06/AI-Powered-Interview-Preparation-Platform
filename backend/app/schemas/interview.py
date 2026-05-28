"""Schemas for the interview engine."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


InterviewType = Literal["technical", "hr", "behavioral", "mixed"]


# ---- Inputs ---------------------------------------------------------------

class StartInterviewRequest(BaseModel):
    company: str | None = Field(default=None, max_length=100)
    role: str | None = Field(default=None, max_length=100)
    interview_type: InterviewType = "mixed"
    num_questions: int = Field(default=5, ge=1, le=15)


class SubmitAnswerRequest(BaseModel):
    answer_text: str = Field(min_length=1)
    duration_seconds: float | None = Field(default=None, ge=0)


# ---- Outputs --------------------------------------------------------------

class QuestionOut(BaseModel):
    id: int
    text: str
    category: str
    difficulty: str

    model_config = ConfigDict(from_attributes=True)


class StartInterviewResponse(BaseModel):
    session_id: int
    company: str | None
    role: str | None
    interview_type: str
    total_questions: int
    current_index: int  # 0-based
    question: QuestionOut


class SubmitAnswerResponse(BaseModel):
    answer_id: int
    scores: dict[str, Any]
    next_question: QuestionOut | None
    answered_count: int
    total_questions: int
    finished: bool


class SessionSummary(BaseModel):
    id: int
    company: str | None
    role: str | None
    interview_type: str
    status: str
    started_at: datetime
    ended_at: datetime | None
    overall_score: float | None

    model_config = ConfigDict(from_attributes=True)


class SessionProgress(BaseModel):
    session: SessionSummary
    answered_count: int
    total_questions: int
    current_question: QuestionOut | None


class ReportItem(BaseModel):
    answer_id: int
    question: str
    category: str
    transcript: str
    scores: dict[str, Any]
    combined_score: float | None


class SessionReport(BaseModel):
    session: SessionSummary
    summary: dict[str, Any] | None
    ai_feedback: str | None
    items: list[ReportItem]


class QuestionMeta(BaseModel):
    companies: list[str]
    roles: list[str]
    counts: dict[str, int]
