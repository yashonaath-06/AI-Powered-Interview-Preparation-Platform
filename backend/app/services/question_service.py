"""
Question generation / selection.

Strategy:
  1. If an LLM key is configured, ask the LLM for tailored questions.
  2. Otherwise, query the local question bank with sensible filters.
  3. Fall back to category-only filter if the (company, role) combo has no rows.

LLM-generated questions are persisted as Question rows so:
  • the rest of the engine just deals with question IDs,
  • the same question can be re-used / inspected later in admin tools.
"""
from __future__ import annotations

import json
import random
from typing import Iterable

from loguru import logger
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.question import Question
from app.services import llm_service


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_questions_for_session(
    db: Session,
    *,
    company: str | None,
    role: str | None,
    interview_type: str,    # technical | hr | behavioral | mixed
    num_questions: int,
) -> list[Question]:
    """Return N Question rows ordered for the session."""
    if interview_type == "mixed":
        cats = _mixed_distribution(num_questions)
    else:
        cats = [interview_type] * num_questions

    # Try LLM first (if configured)
    if llm_service.is_available():
        llm_qs = _generate_via_llm(
            company=company, role=role,
            categories=cats,
        )
        if llm_qs:
            persisted = _persist_questions(db, llm_qs, company=company, role=role)
            if len(persisted) == num_questions:
                return persisted
            # Fall through to bank for any short-fall
            cats = cats[len(persisted):]
            bank = _pick_from_bank(db, company=company, role=role, categories=cats)
            return persisted + bank

    return _pick_from_bank(db, company=company, role=role, categories=cats)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _mixed_distribution(n: int) -> list[str]:
    """Roughly: 50% technical, 30% hr, 20% behavioral."""
    tech = max(1, n // 2)
    hr = max(1, (n - tech) // 2)
    beh = n - tech - hr
    seq = ["technical"] * tech + ["hr"] * hr + ["behavioral"] * beh
    random.shuffle(seq)
    return seq


def _pick_from_bank(
    db: Session,
    *,
    company: str | None,
    role: str | None,
    categories: list[str],
) -> list[Question]:
    """Random sample from the bank matching the filters; degrades gracefully."""
    out: list[Question] = []
    used_ids: set[int] = set()

    for cat in categories:
        q = _sample_one(db, category=cat, company=company, role=role, exclude_ids=used_ids)
        if q is None and (company or role):
            q = _sample_one(db, category=cat, company=None, role=role, exclude_ids=used_ids)
        if q is None and role:
            q = _sample_one(db, category=cat, company=None, role=None, exclude_ids=used_ids)
        if q is not None:
            out.append(q)
            used_ids.add(q.id)
    return out


def _sample_one(
    db: Session,
    *,
    category: str,
    company: str | None,
    role: str | None,
    exclude_ids: set[int],
) -> Question | None:
    stmt = select(Question).where(Question.category == category)
    if company:
        stmt = stmt.where(or_(Question.company == company, Question.company.is_(None)))
    if role:
        stmt = stmt.where(or_(Question.role == role, Question.role.is_(None)))
    if exclude_ids:
        stmt = stmt.where(Question.id.notin_(exclude_ids))

    candidates = list(db.scalars(stmt).all())
    if not candidates:
        return None
    return random.choice(candidates)


# ---- LLM path -------------------------------------------------------------

def _generate_via_llm(
    *,
    company: str | None,
    role: str | None,
    categories: list[str],
) -> list[dict] | None:
    company_part = f" at {company}" if company else ""
    role_part = f" for the role of {role}" if role else ""

    breakdown = ", ".join(f"{categories.count(c)} {c}" for c in {"technical", "hr", "behavioral"} if c in categories)

    system = (
        "You are an expert interview coach. Given a target company, role, and a "
        "mix of question categories, you produce a realistic interview question "
        "set as STRICT JSON of the form: "
        '{"questions": [{"text": "...", "category": "technical|hr|behavioral", '
        '"difficulty": "easy|medium|hard", "expected_keywords": ["..."], '
        '"sample_answer": "..."}]}.'
        " Each question must be open-ended, sound natural when read aloud, and "
        "match the requested category. Avoid trivia. Provide 4-8 expected_keywords."
    )
    user = (
        f"Generate {len(categories)} interview questions{company_part}{role_part}. "
        f"Distribution: {breakdown}. Order them in the same sequence I requested: "
        f"{categories}."
    )

    obj = llm_service.chat_json(system=system, user=user, temperature=0.7)
    if not obj or "questions" not in obj:
        return None

    valid: list[dict] = []
    for q in obj["questions"]:
        if isinstance(q, dict) and isinstance(q.get("text"), str) and q["text"].strip():
            q.setdefault("difficulty", "medium")
            q.setdefault("category", categories[0] if categories else "hr")
            valid.append(q)
    logger.info(f"LLM produced {len(valid)} questions for the session.")
    return valid or None


def _persist_questions(
    db: Session,
    raw: Iterable[dict],
    *,
    company: str | None,
    role: str | None,
) -> list[Question]:
    rows: list[Question] = []
    for q in raw:
        kw = q.get("expected_keywords")
        row = Question(
            text=q["text"].strip(),
            category=q.get("category", "hr"),
            difficulty=q.get("difficulty", "medium"),
            company=company,
            role=role,
            expected_keywords=json.dumps(kw) if isinstance(kw, list) else None,
            sample_answer=q.get("sample_answer"),
        )
        db.add(row)
        rows.append(row)
    db.commit()
    for r in rows:
        db.refresh(r)
    return rows
