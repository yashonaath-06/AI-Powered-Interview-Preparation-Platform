"""
Seeds the question bank from `backend/app/data/question_bank.json`
into the database the first time the backend starts.

Idempotent: skips if questions are already present.
"""
from __future__ import annotations

import json
from pathlib import Path

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.question import Question

BANK_PATH = Path(__file__).parent / "data" / "question_bank.json"


def _kw_to_text(keywords: list[str] | None) -> str | None:
    return json.dumps(keywords) if keywords else None


def seed_question_bank() -> int:
    """Returns number of newly-inserted questions (0 if already seeded)."""
    db: Session = SessionLocal()
    try:
        existing_count = int(db.scalar(select(func.count(Question.id))) or 0)
        if existing_count > 0:
            logger.info(f"Question bank already seeded ({existing_count} rows). Skipping.")
            return 0

        if not BANK_PATH.exists():
            logger.warning(f"Question bank file not found at {BANK_PATH}; skipping.")
            return 0

        with BANK_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)

        rows = data.get("questions", [])
        for item in rows:
            db.add(
                Question(
                    text=item["text"],
                    category=item["category"],
                    difficulty=item.get("difficulty", "medium"),
                    company=item.get("company"),
                    role=item.get("role"),
                    expected_keywords=_kw_to_text(item.get("expected_keywords")),
                    sample_answer=item.get("sample_answer"),
                )
            )
        db.commit()
        logger.info(f"✅ Seeded {len(rows)} questions into the question bank.")
        return len(rows)
    finally:
        db.close()
