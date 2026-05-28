"""Schemas for resume upload + analysis."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ResumeOut(BaseModel):
    id: int
    filename: str
    target_role: str | None
    match_score: float | None
    parsed_skills: dict[str, Any] | list[str] | None = None
    ai_feedback: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeAnalysisOut(BaseModel):
    id: int
    filename: str
    target_role: str | None
    match_score: float
    ai_feedback: str
    raw_text_preview: str

    parsed_skills: list[str]
    matched_skills: list[str]
    missing_skills: list[str]
    skill_categories: dict[str, list[str]]
    detected_sections: list[str]
    word_count: int | None = None
    semantic_score: float | None = None
    notes: list[str] = []

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
