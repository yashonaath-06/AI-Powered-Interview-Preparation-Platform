"""
/api/resume — upload + AI analysis (Phase 13).

Endpoints
---------
GET    /                  list my resumes (most recent first)
GET    /{id}              full analysis details
POST   /analyze           upload PDF + optional target_role -> analysis
DELETE /{id}              remove a resume
"""
from __future__ import annotations

import json

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.resume import Resume
from app.models.user import User
from app.schemas.resume import ResumeAnalysisOut, ResumeOut
from app.services import resume_service

router = APIRouter()

MAX_PDF_BYTES = 8 * 1024 * 1024  # 8 MB


def _to_resume_out(r: Resume) -> ResumeOut:
    return ResumeOut.model_validate({
        "id": r.id,
        "filename": r.filename,
        "target_role": r.target_role,
        "match_score": r.match_score,
        "parsed_skills": json.loads(r.parsed_skills) if r.parsed_skills else None,
        "ai_feedback": r.ai_feedback,
        "created_at": r.created_at,
    })


@router.get("", response_model=list[ResumeOut], summary="List my resumes")
def list_my_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = list(db.scalars(
        select(Resume)
        .where(Resume.user_id == current_user.id)
        .order_by(desc(Resume.created_at))
    ).all())
    return [_to_resume_out(r) for r in rows]


@router.get("/{resume_id}", response_model=ResumeAnalysisOut, summary="Full analysis details")
def get_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    r = db.get(Resume, resume_id)
    if r is None or r.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    parsed = json.loads(r.parsed_skills) if r.parsed_skills else {}
    return ResumeAnalysisOut.model_validate({
        "id": r.id,
        "filename": r.filename,
        "target_role": r.target_role,
        "match_score": r.match_score,
        "ai_feedback": r.ai_feedback,
        "raw_text_preview": (r.raw_text or "")[:1500],
        "parsed_skills": parsed.get("parsed_skills") or [],
        "matched_skills": parsed.get("matched_skills") or [],
        "missing_skills": parsed.get("missing_skills") or [],
        "skill_categories": parsed.get("skill_categories") or {},
        "detected_sections": parsed.get("detected_sections") or [],
        "word_count": parsed.get("word_count"),
        "semantic_score": parsed.get("semantic_score"),
        "notes": parsed.get("notes") or [],
        "created_at": r.created_at,
    })


@router.post(
    "/analyze",
    response_model=ResumeAnalysisOut,
    status_code=status.HTTP_201_CREATED,
    summary="Upload + analyze a PDF resume",
)
async def analyze_resume(
    resume: UploadFile = File(..., description="PDF resume (max 8 MB)"),
    target_role: str | None = Form(default=None, description="e.g. 'Software Engineer'"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not resume_service.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Resume analyzer is not available — pypdf is not installed.",
        )

    if not (resume.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only .pdf files are supported.")

    raw = await resume.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Empty file upload.")
    if len(raw) > MAX_PDF_BYTES:
        raise HTTPException(status_code=413, detail="PDF is too large (limit: 8 MB).")

    try:
        analysis = resume_service.analyze_resume(raw, target_role=target_role)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    # Persist
    record = Resume(
        user_id=current_user.id,
        filename=resume.filename or "resume.pdf",
        raw_text=analysis.raw_text[:20000],  # cap to keep DB lean
        parsed_skills=json.dumps({
            "parsed_skills":     analysis.parsed_skills,
            "matched_skills":    analysis.matched_skills,
            "missing_skills":    analysis.missing_skills,
            "skill_categories":  analysis.skill_categories,
            "detected_sections": analysis.detected_sections,
            "word_count":        analysis.word_count,
            "semantic_score":    analysis.semantic_score,
            "notes":             analysis.notes,
        }),
        target_role=target_role,
        match_score=analysis.match_score,
        ai_feedback=analysis.ai_feedback,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return ResumeAnalysisOut.model_validate({
        "id": record.id,
        "filename": record.filename,
        "target_role": record.target_role,
        "match_score": record.match_score,
        "ai_feedback": record.ai_feedback,
        "raw_text_preview": analysis.raw_text[:1500],
        "parsed_skills":    analysis.parsed_skills,
        "matched_skills":   analysis.matched_skills,
        "missing_skills":   analysis.missing_skills,
        "skill_categories": analysis.skill_categories,
        "detected_sections": analysis.detected_sections,
        "word_count":       analysis.word_count,
        "semantic_score":   analysis.semantic_score,
        "notes":            analysis.notes,
        "created_at":       record.created_at,
    })


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    r = db.get(Resume, resume_id)
    if r is None or r.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    db.delete(r)
    db.commit()
