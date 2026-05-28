"""
/api/interviews — full interview lifecycle (Phase 7).

Endpoints
---------
POST   /api/interviews                    start a new session
GET    /api/interviews                    list my sessions
GET    /api/interviews/{id}               session + progress
GET    /api/interviews/{id}/next          current/next question
POST   /api/interviews/{id}/answer        submit answer (text)
POST   /api/interviews/{id}/complete      finalize + score
GET    /api/interviews/{id}/report        full report (after complete)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.interview import InterviewSession
from app.models.user import User
from app.schemas.interview import (
    QuestionOut,
    ReportItem,
    SessionProgress,
    SessionReport,
    SessionSummary,
    StartInterviewRequest,
    StartInterviewResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
)
from app.services import interview_engine

router = APIRouter()


# ---------- list ------------------------------------------------------------

@router.get("", response_model=list[SessionSummary], summary="List my interview sessions")
def list_my_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = db.scalars(
        select(InterviewSession)
        .where(InterviewSession.user_id == current_user.id)
        .order_by(desc(InterviewSession.started_at))
    ).all()
    return [SessionSummary.model_validate(r) for r in rows]


# ---------- start -----------------------------------------------------------

@router.post(
    "",
    response_model=StartInterviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a new interview session",
)
def start_interview(
    payload: StartInterviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session, first_q = interview_engine.start_session(
        db,
        user=current_user,
        company=payload.company,
        role=payload.role,
        interview_type=payload.interview_type,
        num_questions=payload.num_questions,
    )
    return StartInterviewResponse(
        session_id=session.id,
        company=session.company,
        role=session.role,
        interview_type=session.interview_type,
        total_questions=session.num_questions,
        current_index=0,
        question=QuestionOut.model_validate(first_q),
    )


# ---------- progress --------------------------------------------------------

@router.get(
    "/{session_id}",
    response_model=SessionProgress,
    summary="Get session details + progress",
)
def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    p = interview_engine.get_session_with_progress(
        db, user=current_user, session_id=session_id
    )
    return SessionProgress(
        session=SessionSummary.model_validate(p["session"]),
        answered_count=p["answered_count"],
        total_questions=p["total_questions"],
        current_question=(
            QuestionOut.model_validate(p["current_question"])
            if p["current_question"] else None
        ),
    )


@router.get(
    "/{session_id}/next",
    response_model=QuestionOut,
    summary="Fetch the current/next question",
)
def get_next_question(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    p = interview_engine.get_session_with_progress(
        db, user=current_user, session_id=session_id
    )
    if p["current_question"] is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No more questions remain. Call /complete to finalize the session.",
        )
    return QuestionOut.model_validate(p["current_question"])


# ---------- submit answer ---------------------------------------------------

@router.post(
    "/{session_id}/answer",
    response_model=SubmitAnswerResponse,
    summary="Submit an answer for the current question",
)
def submit_answer(
    session_id: int,
    payload: SubmitAnswerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    answer, next_q = interview_engine.submit_answer(
        db,
        user=current_user,
        session_id=session_id,
        answer_text=payload.answer_text,
        duration_seconds=payload.duration_seconds,
    )

    # Determine progress
    p = interview_engine.get_session_with_progress(
        db, user=current_user, session_id=session_id
    )
    finished = next_q is None
    import json
    return SubmitAnswerResponse(
        answer_id=answer.id,
        scores=json.loads(answer.nlp_scores or "{}"),
        next_question=QuestionOut.model_validate(next_q) if next_q else None,
        answered_count=p["answered_count"],
        total_questions=p["total_questions"],
        finished=finished,
    )


# ---------- complete --------------------------------------------------------

@router.post(
    "/{session_id}/complete",
    response_model=SessionSummary,
    summary="Finalize an interview session and compute final scores",
)
def complete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = interview_engine.complete_session(
        db, user=current_user, session_id=session_id
    )
    return SessionSummary.model_validate(session)


# ---------- report ----------------------------------------------------------

@router.get(
    "/{session_id}/report",
    response_model=SessionReport,
    summary="Full report for a completed session",
)
def get_report(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = interview_engine.get_full_report(
        db, user=current_user, session_id=session_id
    )
    return SessionReport(
        session=SessionSummary.model_validate(data["session"]),
        summary=data["summary"],
        ai_feedback=data["ai_feedback"],
        items=[ReportItem(**i) for i in data["items"]],
    )
