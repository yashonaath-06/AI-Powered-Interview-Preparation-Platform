"""
/api/questions — public reads + meta info for the interview setup form.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.models.question import Question
from app.schemas.interview import QuestionMeta
from app.schemas.question import QuestionOut

router = APIRouter()


@router.get("", response_model=list[QuestionOut], summary="List questions")
def list_questions(
    category: str | None = Query(default=None),
    company: str | None = Query(default=None),
    role: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
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
                "expected_keywords": None,
                "sample_answer": q.sample_answer,
                "created_at": q.created_at,
            }
        )
        for q in db.scalars(stmt).all()
    ]


@router.get(
    "/meta",
    response_model=QuestionMeta,
    summary="Distinct companies and roles to populate the setup form",
)
def question_meta(db: Session = Depends(get_db)) -> QuestionMeta:
    companies = sorted(
        c for c in db.scalars(
            select(distinct(Question.company)).where(Question.company.is_not(None))
        ).all()
        if c
    )
    roles = sorted(
        r for r in db.scalars(
            select(distinct(Question.role)).where(Question.role.is_not(None))
        ).all()
        if r
    )
    counts = {
        cat: int(
            db.scalar(select(func.count(Question.id)).where(Question.category == cat)) or 0
        )
        for cat in ("technical", "hr", "behavioral")
    }
    return QuestionMeta(companies=companies, roles=roles, counts=counts)
