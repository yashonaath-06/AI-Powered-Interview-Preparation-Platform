"""
/api/interviews — full interview lifecycle (Phases 7-10).

Endpoints
---------
POST   /api/interviews                    start a new session
GET    /api/interviews                    list my sessions
GET    /api/interviews/{id}               session + progress
GET    /api/interviews/{id}/next          current/next question
POST   /api/interviews/{id}/answer        submit answer (text)
POST   /api/interviews/{id}/answer/audio  submit spoken answer (Phase 8)
POST   /api/interviews/{id}/vision/frame  per-frame webcam analysis (Phase 10)
POST   /api/interviews/{id}/vision/aggregate  aggregate frame metrics (Phase 10)
POST   /api/interviews/{id}/complete      finalize + score
GET    /api/interviews/{id}/report        full report (after complete)
"""
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.interview import InterviewSession
from app.models.user import User
from app.schemas.interview import (
    AudioAnswerResponse,
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
from app.schemas.vision import FrameMetricsOut, VisionSummaryIn
from app.services import interview_engine, speech_service, vision_service

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
        vision_summary=payload.vision_summary,
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


# ---------- submit audio answer (Phase 8) ----------------------------------

@router.post(
    "/{session_id}/answer/audio",
    response_model=AudioAnswerResponse,
    summary="Submit a SPOKEN answer — transcribed by Whisper, then scored",
)
async def submit_audio_answer(
    session_id: int,
    audio: UploadFile = File(..., description="Audio blob (webm/ogg/wav/mp3)"),
    vision_summary: str | None = Form(default=None, description="Optional JSON string of aggregated vision metrics"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not speech_service.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Speech-to-text is not enabled on this server. Install "
                "requirements-ml.txt to enable Whisper transcription, or "
                "submit a text answer instead via /answer."
            ),
        )

    raw = await audio.read()
    if not raw:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty audio upload.",
        )

    if len(raw) > 15 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Audio file is too large (limit: 15 MB).",
        )

    # Parse optional vision summary
    import json
    parsed_vision: dict | None = None
    if vision_summary:
        try:
            parsed_vision = json.loads(vision_summary)
        except json.JSONDecodeError:
            parsed_vision = None

    # ---- 1. Transcribe ----
    ext = "webm"
    if audio.filename and "." in audio.filename:
        ext = audio.filename.rsplit(".", 1)[1].lower()
    try:
        result = speech_service.transcribe_bytes(raw, file_extension=ext)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not transcribe audio: {exc}",
        )

    if not result.transcript.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Whisper produced an empty transcript — your microphone may "
                "have been muted, or the answer was inaudible. Please try again."
            ),
        )

    # ---- 2. Run the same scoring pipeline as text answers ----
    answer, next_q = interview_engine.submit_answer(
        db,
        user=current_user,
        session_id=session_id,
        answer_text=result.transcript,
        duration_seconds=result.duration_seconds,
        vision_summary=parsed_vision,
    )

    p = interview_engine.get_session_with_progress(
        db, user=current_user, session_id=session_id
    )
    import json
    return AudioAnswerResponse(
        answer_id=answer.id,
        scores=json.loads(answer.nlp_scores or "{}"),
        next_question=QuestionOut.model_validate(next_q) if next_q else None,
        answered_count=p["answered_count"],
        total_questions=p["total_questions"],
        finished=next_q is None,
        transcript=result.transcript,
        detected_language=result.language,
        audio_duration_seconds=result.duration_seconds,
    )


# ---------- vision (Phase 10) -----------------------------------------------

@router.post(
    "/{session_id}/vision/frame",
    response_model=FrameMetricsOut,
    summary="Analyze a single webcam frame with MediaPipe FaceMesh",
)
async def analyze_vision_frame(
    session_id: int,
    image: UploadFile = File(..., description="JPEG or PNG webcam frame"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not vision_service.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Computer-vision is not enabled on this server. Install "
                "requirements-ml.txt (mediapipe + opencv + Pillow) to enable "
                "webcam analysis."
            ),
        )

    # Verify ownership of the session
    sess = db.get(InterviewSession, session_id)
    if sess is None or sess.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")

    raw = await image.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Empty frame upload.")
    if len(raw) > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Frame too large (limit 5 MB).")

    try:
        metrics = vision_service.analyze_frame(raw)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return FrameMetricsOut.model_validate(metrics.to_dict())


@router.post(
    "/{session_id}/vision/aggregate",
    response_model=VisionSummaryIn,
    summary="Aggregate a list of per-frame metrics into a session summary",
)
def aggregate_vision_metrics(
    session_id: int,
    frames: list[FrameMetricsOut],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Pure utility: takes the per-frame metrics the frontend has been
    receiving and returns the aggregate the answer endpoint expects."""
    sess = db.get(InterviewSession, session_id)
    if sess is None or sess.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")

    summary = vision_service.aggregate_frames([f.model_dump() for f in frames])
    return VisionSummaryIn(**summary)

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
