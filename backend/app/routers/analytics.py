"""
/api/analytics — performance metrics and progress tracking.

Phase 4 baseline: returns aggregates from the InterviewSession table.
Phase 11 will add charts data, comparisons, and AI insights.
"""
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.interview import InterviewSession
from app.models.user import User

router = APIRouter()


@router.get("/summary", summary="High-level stats for the dashboard")
def my_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total = db.scalar(
        select(func.count(InterviewSession.id)).where(
            InterviewSession.user_id == current_user.id
        )
    )
    completed = db.scalar(
        select(func.count(InterviewSession.id)).where(
            InterviewSession.user_id == current_user.id,
            InterviewSession.status == "completed",
        )
    )
    avg_score = db.scalar(
        select(func.avg(InterviewSession.overall_score)).where(
            InterviewSession.user_id == current_user.id,
            InterviewSession.overall_score.is_not(None),
        )
    )

    return {
        "total_sessions": int(total or 0),
        "completed_sessions": int(completed or 0),
        "average_score": round(float(avg_score), 2) if avg_score is not None else None,
    }
