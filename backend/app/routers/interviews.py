"""
/api/interviews — interview lifecycle.

Phase 4 baseline: returns the user's session list and a "not implemented yet"
placeholder for starting interviews. Phase 7 fills in the real engine.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.interview import InterviewSession
from app.models.user import User
from app.schemas.interview import SessionSummary, StartInterviewRequest

router = APIRouter()


@router.get(
    "",
    response_model=list[SessionSummary],
    summary="List my interview sessions (most recent first)",
)
def list_my_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SessionSummary]:
    rows = db.scalars(
        select(InterviewSession)
        .where(InterviewSession.user_id == current_user.id)
        .order_by(desc(InterviewSession.started_at))
    ).all()
    return [SessionSummary.model_validate(r) for r in rows]


@router.post(
    "",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    summary="Start a new interview (Phase 7)",
)
def start_interview(
    _: StartInterviewRequest,
    current_user: User = Depends(get_current_user),
):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="The AI Interview Engine is implemented in Phase 7.",
    )
