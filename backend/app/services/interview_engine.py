"""
Interview session state machine.

Public API used by the /api/interviews routes:

    start_session(...)     → create session, plan questions, return (session, first_question)
    submit_answer(...)     → store + score answer, return (next_question | None)
    complete_session(...)  → aggregate scores, write final feedback, mark done
    get_progress(...)      → quick {answered, total, current_question, ...} snapshot
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from fastapi import HTTPException, status
from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.interview import Answer, InterviewSession
from app.models.question import Question
from app.models.user import User
from app.services import llm_service, question_service, scoring_service
from app.services.scoring_service import score_answer


# ---------------------------------------------------------------------------
# Start
# ---------------------------------------------------------------------------

def start_session(
    db: Session,
    *,
    user: User,
    company: str | None,
    role: str | None,
    interview_type: str,
    num_questions: int,
) -> tuple[InterviewSession, Question]:
    questions = question_service.generate_questions_for_session(
        db,
        company=company,
        role=role,
        interview_type=interview_type,
        num_questions=num_questions,
    )
    if not questions:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Could not generate any questions. The question bank seems empty. "
                "Try restarting the backend so it can re-seed the bank."
            ),
        )

    session = InterviewSession(
        user_id=user.id,
        company=company,
        role=role,
        interview_type=interview_type,
        status="in_progress",
        num_questions=len(questions),
        planned_question_ids=json.dumps([q.id for q in questions]),
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    logger.info(
        f"Started session #{session.id} for user #{user.id} "
        f"({interview_type}, {len(questions)} questions, company={company!r}, role={role!r})"
    )
    return session, questions[0]


# ---------------------------------------------------------------------------
# Submit answer / next question
# ---------------------------------------------------------------------------

def submit_answer(
    db: Session,
    *,
    user: User,
    session_id: int,
    answer_text: str,
    duration_seconds: float | None = None,
) -> tuple[Answer, Question | None]:
    session = _load_owned_session(db, user=user, session_id=session_id)
    if session.status != "in_progress":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This session is already completed.",
        )

    planned: list[int] = json.loads(session.planned_question_ids or "[]")
    answered_count = db.scalar(
        select(Answer).where(Answer.session_id == session.id).order_by(Answer.id)
    )
    answered_ids = [a.question_id for a in db.scalars(
        select(Answer).where(Answer.session_id == session.id).order_by(Answer.id)
    ).all()]

    next_idx = len(answered_ids)
    if next_idx >= len(planned):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="All questions for this session have already been answered.",
        )

    current_question_id = planned[next_idx]
    question = db.get(Question, current_question_id)
    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The current question could not be found.",
        )

    # ---- Score the answer ------------------------------------------------
    expected_kw = _decode_keywords(question.expected_keywords)
    result = score_answer(
        answer_text,
        expected_keywords=expected_kw,
        sample_answer=question.sample_answer,
        question_text=question.text,
    )

    answer = Answer(
        session_id=session.id,
        question_id=question.id,
        transcript=answer_text,
        duration_seconds=duration_seconds,
        nlp_scores=json.dumps(result.to_dict()),
        combined_score=result.overall,
    )
    db.add(answer)
    db.commit()
    db.refresh(answer)

    # ---- Determine next question ----------------------------------------
    if next_idx + 1 >= len(planned):
        return answer, None

    next_q = db.get(Question, planned[next_idx + 1])
    return answer, next_q


# ---------------------------------------------------------------------------
# Complete
# ---------------------------------------------------------------------------

def complete_session(
    db: Session,
    *,
    user: User,
    session_id: int,
) -> InterviewSession:
    session = _load_owned_session(db, user=user, session_id=session_id)
    if session.status == "completed":
        return session

    answers = list(db.scalars(
        select(Answer).where(Answer.session_id == session.id).order_by(Answer.id)
    ).all())

    score_dicts = [json.loads(a.nlp_scores or "{}") for a in answers]
    summary = scoring_service.aggregate_session_scores(score_dicts)

    feedback = _generate_feedback(session, answers, summary)

    session.status = "completed"
    session.ended_at = datetime.now(timezone.utc)
    session.overall_score = summary["overall"]
    session.scores_json = json.dumps(summary)
    session.ai_feedback = feedback
    db.commit()
    db.refresh(session)
    logger.info(f"Completed session #{session.id} (score={session.overall_score}).")
    return session


# ---------------------------------------------------------------------------
# Progress / lookup helpers
# ---------------------------------------------------------------------------

def get_session_with_progress(
    db: Session,
    *,
    user: User,
    session_id: int,
) -> dict:
    session = _load_owned_session(db, user=user, session_id=session_id)
    planned: list[int] = json.loads(session.planned_question_ids or "[]")
    answers = list(db.scalars(
        select(Answer).where(Answer.session_id == session.id).order_by(Answer.id)
    ).all())

    answered_count = len(answers)
    current_q: Question | None = None
    if session.status == "in_progress" and answered_count < len(planned):
        current_q = db.get(Question, planned[answered_count])

    return {
        "session": session,
        "answered_count": answered_count,
        "total_questions": len(planned),
        "current_question": current_q,
        "answers": answers,
    }


def get_full_report(
    db: Session,
    *,
    user: User,
    session_id: int,
) -> dict:
    session = _load_owned_session(db, user=user, session_id=session_id)
    answers = list(db.scalars(
        select(Answer).where(Answer.session_id == session.id).order_by(Answer.id)
    ).all())

    qs_by_id = {
        q.id: q for q in db.scalars(
            select(Question).where(Question.id.in_([a.question_id for a in answers]))
        ).all()
    } if answers else {}

    items: list[dict] = []
    for a in answers:
        q = qs_by_id.get(a.question_id)
        items.append({
            "answer_id": a.id,
            "question": q.text if q else "",
            "category": q.category if q else "",
            "transcript": a.transcript or "",
            "scores": json.loads(a.nlp_scores or "{}"),
            "combined_score": a.combined_score,
        })

    return {
        "session": session,
        "summary": json.loads(session.scores_json) if session.scores_json else None,
        "ai_feedback": session.ai_feedback,
        "items": items,
    }


# ---------------------------------------------------------------------------
# Internal
# ---------------------------------------------------------------------------

def _load_owned_session(
    db: Session,
    *,
    user: User,
    session_id: int,
) -> InterviewSession:
    session = db.get(InterviewSession, session_id)
    if session is None or session.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview session not found.",
        )
    return session


def _decode_keywords(value: str | None) -> list[str] | None:
    if not value:
        return None
    try:
        out = json.loads(value)
        return out if isinstance(out, list) else None
    except json.JSONDecodeError:
        return None


def _generate_feedback(
    session: InterviewSession,
    answers: list[Answer],
    summary: dict,
) -> str:
    """
    Try LLM first, fall back to a templated paragraph.
    """
    if not answers:
        return "No answers were recorded for this session."

    # Compact JSON for the LLM
    payload = {
        "company": session.company,
        "role": session.role,
        "interview_type": session.interview_type,
        "summary": summary,
        "answer_notes": [
            {
                "scores": json.loads(a.nlp_scores or "{}"),
                "transcript_preview": (a.transcript or "")[:280],
            }
            for a in answers
        ],
    }

    if llm_service.is_available():
        text = llm_service.chat_text(
            system=(
                "You are an expert interview coach. Given a JSON summary of a "
                "candidate's mock interview, write a friendly, specific feedback "
                "report of 4-6 short paragraphs. Cover: (1) overall impression, "
                "(2) two concrete strengths, (3) two concrete weaknesses, "
                "(4) actionable study tips, (5) one motivating closing line. "
                "Avoid repeating the JSON; speak directly to the candidate as 'you'."
            ),
            user=json.dumps(payload),
        )
        if text:
            return text.strip()

    # ---- Templated fallback --------------------------------------------
    overall = summary.get("overall", 0)
    if overall >= 8:
        verdict = "an excellent performance"
    elif overall >= 6.5:
        verdict = "a solid performance with room to refine"
    elif overall >= 5:
        verdict = "a decent attempt that needs more practice"
    else:
        verdict = "a difficult round that needs significant practice"

    lines = [
        f"You completed a {session.interview_type} interview"
        f"{' for ' + session.role if session.role else ''}"
        f"{' at ' + session.company if session.company else ''}.",
        f"Overall this was {verdict} (score: {overall}/10).",
        f"Strongest dimension: communication = {summary.get('communication', 0)}/10. "
        f"Weakest dimension: technical = {summary.get('technical', 0)}/10.",
        "Tips: structure your answers with the STAR method, give concrete examples, "
        "minimise filler words like 'um' and 'like', and double-check that you "
        "address the specific keywords in each question.",
    ]
    return "\n\n".join(lines)
