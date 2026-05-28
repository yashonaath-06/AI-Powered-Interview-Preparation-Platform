"""Schemas for the question bank (admin CRUD + public reads)."""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class QuestionBase(BaseModel):
    text: str = Field(min_length=5)
    category: Literal["technical", "hr", "behavioral"]
    difficulty: Literal["easy", "medium", "hard"] = "medium"
    company: str | None = Field(default=None, max_length=100)
    role: str | None = Field(default=None, max_length=100)
    expected_keywords: list[str] | None = None
    sample_answer: str | None = None


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(BaseModel):
    text: str | None = None
    difficulty: Literal["easy", "medium", "hard"] | None = None
    company: str | None = None
    role: str | None = None
    expected_keywords: list[str] | None = None
    sample_answer: str | None = None


class QuestionOut(QuestionBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
