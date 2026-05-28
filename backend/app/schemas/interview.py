"""Schemas for the interview engine. (filled out across phases)"""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


InterviewType = Literal["technical", "hr", "behavioral", "mixed"]


class StartInterviewRequest(BaseModel):
    company: str | None = Field(default=None, max_length=100)
    role: str | None = Field(default=None, max_length=100)
    interview_type: InterviewType = "mixed"
    num_questions: int = Field(default=5, ge=1, le=20)


class QuestionOut(BaseModel):
    id: int
    text: str
    category: str
    difficulty: str

    model_config = ConfigDict(from_attributes=True)


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
