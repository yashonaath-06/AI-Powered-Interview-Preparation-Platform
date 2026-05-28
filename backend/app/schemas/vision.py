"""Schemas for the /vision endpoints."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class FrameMetricsOut(BaseModel):
    face_detected: bool
    face_count: int
    head_yaw_deg: float | None = None
    head_pitch_deg: float | None = None
    head_roll_deg: float | None = None
    gaze_x: float | None = None
    gaze_y: float | None = None
    eye_contact: bool | None = None
    smile_score: float | None = None
    notes: list[str] = []

    model_config = ConfigDict(from_attributes=True)


class VisionSummaryIn(BaseModel):
    """Aggregated vision metrics for an answer (sent by the frontend)."""

    face_present_pct: float | None = None
    eye_contact_pct: float | None = None
    avg_head_yaw: float | None = None
    avg_head_pitch: float | None = None
    avg_smile: float | None = None
    engagement_score: float | None = None
    confidence_boost: float | None = None
    sample_count: int = 0
    notes: list[str] = []
