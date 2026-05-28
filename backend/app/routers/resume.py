"""
/api/resume — upload + AI feedback.  Filled in Phase 13.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.resume import Resume
from app.models.user import User
from app.schemas.resume import ResumeOut

router = APIRouter()


@router.get("", response_model=list[ResumeOut], summary="List my resumes")
def list_my_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ResumeOut]:
    rows = db.scalars(
        select(Resume)
        .where(Resume.user_id == current_user.id)
        .order_by(desc(Resume.created_at))
    ).all()
    return [
        ResumeOut.model_validate(
            {
                "id": r.id,
                "filename": r.filename,
                "target_role": r.target_role,
                "match_score": r.match_score,
                "parsed_skills": None,  # Phase 13 will JSON-decode
                "ai_feedback": r.ai_feedback,
                "created_at": r.created_at,
            }
        )
        for r in rows
    ]


@router.post(
    "/analyze",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    summary="Upload + analyze resume (Phase 13)",
)
def analyze_resume(current_user: User = Depends(get_current_user)):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Resume analyzer is implemented in Phase 13.",
    )
