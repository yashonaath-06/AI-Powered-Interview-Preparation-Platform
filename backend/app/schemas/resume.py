"""Schemas for resume upload / analysis."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ResumeOut(BaseModel):
    id: int
    filename: str
    target_role: str | None
    match_score: float | None
    parsed_skills: list[str] | None = None
    ai_feedback: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
