"""
/api/admin — admin-only endpoints.

Phase 4 baseline: list users + simple platform stats.
Phase 12 expands this into a full admin dashboard backend.
"""
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_admin
from app.models.interview import InterviewSession
from app.models.question import Question
from app.models.user import User
from app.schemas.user import UserPublic

router = APIRouter()


@router.get("/users", response_model=list[UserPublic], summary="List all users (admin)")
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[UserPublic]:
    rows = db.scalars(select(User).order_by(User.created_at.desc())).all()
    return [UserPublic.model_validate(u) for u in rows]


@router.get("/stats", summary="Platform-wide stats (admin)")
def platform_stats(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return {
        "users": int(db.scalar(select(func.count(User.id))) or 0),
        "questions": int(db.scalar(select(func.count(Question.id))) or 0),
        "sessions": int(db.scalar(select(func.count(InterviewSession.id))) or 0),
    }
