"""
/api/questions — public read endpoints for the question bank.

Phase 4 baseline: list / filter is implemented; admin CRUD lives in Phase 12.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.models.question import Question
from app.schemas.question import QuestionOut

router = APIRouter()


@router.get("", response_model=list[QuestionOut], summary="List questions")
def list_questions(
    category: str | None = Query(default=None),
    company: str | None = Query(default=None),
    role: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[QuestionOut]:
    stmt = select(Question)
    if category:
        stmt = stmt.where(Question.category == category)
    if company:
        stmt = stmt.where(Question.company == company)
    if role:
        stmt = stmt.where(Question.role == role)
    stmt = stmt.limit(limit)

    return [
        QuestionOut.model_validate(
            {
                "id": q.id,
                "text": q.text,
                "category": q.category,
                "difficulty": q.difficulty,
                "company": q.company,
                "role": q.role,
                "expected_keywords": None,  # Phase 7 will JSON-decode this
                "sample_answer": q.sample_answer,
                "created_at": q.created_at,
            }
        )
        for q in db.scalars(stmt).all()
    ]
