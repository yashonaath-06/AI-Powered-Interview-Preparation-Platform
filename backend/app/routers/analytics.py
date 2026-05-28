"""
/api/analytics — performance metrics, charts data, session comparisons.

Endpoints
---------
GET  /summary            high-level stat cards
GET  /trend              chronological score history (charts)
GET  /by-type            scores grouped by interview type
GET  /dimensions         radar-chart: latest vs my average across the 4 dims
GET  /weaknesses         most common low-score notes across all answers
POST /compare            side-by-side comparison of any two of MY sessions
"""
from __future__ import annotations

import json
from collections import Counter

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.interview import Answer, InterviewSession
from app.models.user import User

router = APIRouter()


# ---------------------------------------------------------------------------
# /summary  — already there, but we extend it with best & latest score
# ---------------------------------------------------------------------------

@router.get("/summary", summary="High-level stats for the dashboard")
def my_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    base = select(InterviewSession).where(InterviewSession.user_id == current_user.id)

    total = db.scalar(
        select(func.count(InterviewSession.id)).where(InterviewSession.user_id == current_user.id)
    )
    completed_q = base.where(InterviewSession.status == "completed")
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
    best_score = db.scalar(
        select(func.max(InterviewSession.overall_score)).where(
            InterviewSession.user_id == current_user.id,
            InterviewSession.overall_score.is_not(None),
        )
    )
    latest = db.scalar(
        completed_q.order_by(desc(InterviewSession.ended_at)).limit(1)
    )

    # Detect a simple growth trend: avg of first half vs avg of second half
    completed_scores = list(db.scalars(
        select(InterviewSession.overall_score)
        .where(
            InterviewSession.user_id == current_user.id,
            InterviewSession.status == "completed",
            InterviewSession.overall_score.is_not(None),
        )
        .order_by(InterviewSession.started_at)
    ).all())

    growth_pct: float | None = None
    if len(completed_scores) >= 4:
        half = len(completed_scores) // 2
        first_avg = sum(completed_scores[:half]) / half
        second_avg = sum(completed_scores[half:]) / (len(completed_scores) - half)
        if first_avg > 0:
            growth_pct = round((second_avg - first_avg) / first_avg * 100, 1)

    return {
        "total_sessions": int(total or 0),
        "completed_sessions": int(completed or 0),
        "average_score": round(float(avg_score), 2) if avg_score is not None else None,
        "best_score": round(float(best_score), 2) if best_score is not None else None,
        "latest_score": (
            round(float(latest.overall_score), 2)
            if latest and latest.overall_score is not None else None
        ),
        "growth_pct": growth_pct,
    }


# ---------------------------------------------------------------------------
# /trend  — chronological data for the line chart
# ---------------------------------------------------------------------------

@router.get("/trend", summary="Chronological score history (for line chart)")
def my_trend(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = list(db.scalars(
        select(InterviewSession)
        .where(
            InterviewSession.user_id == current_user.id,
            InterviewSession.status == "completed",
            InterviewSession.overall_score.is_not(None),
        )
        .order_by(InterviewSession.started_at)
    ).all())

    points = []
    for s in rows:
        summary = json.loads(s.scores_json) if s.scores_json else {}
        points.append({
            "session_id": s.id,
            "label": s.started_at.strftime("%b %d"),
            "started_at": s.started_at.isoformat(),
            "company": s.company,
            "role": s.role,
            "interview_type": s.interview_type,
            "overall": s.overall_score,
            "technical": summary.get("technical"),
            "communication": summary.get("communication"),
            "confidence": summary.get("confidence"),
            "engagement": summary.get("engagement"),
        })

    return {"points": points, "count": len(points)}


# ---------------------------------------------------------------------------
# /by-type  — bar chart: avg score per interview type
# ---------------------------------------------------------------------------

@router.get("/by-type", summary="Average score grouped by interview type")
def by_type(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = list(db.execute(
        select(
            InterviewSession.interview_type,
            func.count(InterviewSession.id),
            func.avg(InterviewSession.overall_score),
        )
        .where(
            InterviewSession.user_id == current_user.id,
            InterviewSession.status == "completed",
            InterviewSession.overall_score.is_not(None),
        )
        .group_by(InterviewSession.interview_type)
    ).all())

    return {
        "items": [
            {
                "type": r[0],
                "count": int(r[1]),
                "average": round(float(r[2]), 2) if r[2] is not None else None,
            }
            for r in rows
        ]
    }


# ---------------------------------------------------------------------------
# /dimensions  — radar chart data: latest vs my average across 4 dims
# ---------------------------------------------------------------------------

@router.get("/dimensions", summary="Radar-chart data: latest vs my average")
def my_dimensions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = list(db.scalars(
        select(InterviewSession)
        .where(
            InterviewSession.user_id == current_user.id,
            InterviewSession.status == "completed",
            InterviewSession.scores_json.is_not(None),
        )
        .order_by(desc(InterviewSession.ended_at))
    ).all())

    if not rows:
        return {"latest": None, "average": None}

    latest_summary = json.loads(rows[0].scores_json or "{}")
    keys = ("technical", "communication", "confidence", "engagement")

    # average across all completed sessions
    averages: dict[str, float] = {}
    for k in keys:
        vals = []
        for r in rows:
            d = json.loads(r.scores_json or "{}")
            v = d.get(k)
            if isinstance(v, (int, float)):
                vals.append(float(v))
        averages[k] = round(sum(vals) / len(vals), 2) if vals else 0.0

    return {
        "latest": {k: latest_summary.get(k, 0) for k in keys},
        "average": averages,
        "session_count": len(rows),
    }


# ---------------------------------------------------------------------------
# /weaknesses  — most common low-score notes across all my answers
# ---------------------------------------------------------------------------

@router.get("/weaknesses", summary="Top recurring weaknesses across my answers")
def my_weaknesses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    answer_rows = list(db.scalars(
        select(Answer)
        .join(InterviewSession, Answer.session_id == InterviewSession.id)
        .where(InterviewSession.user_id == current_user.id)
    ).all())

    counter: Counter = Counter()
    total_scored = 0
    for a in answer_rows:
        if not a.nlp_scores:
            continue
        total_scored += 1
        try:
            blob = json.loads(a.nlp_scores)
        except json.JSONDecodeError:
            continue
        for note in blob.get("notes", []) or []:
            # Normalise common phrasing into thematic buckets
            normalized = _bucketize(note)
            if normalized:
                counter[normalized] += 1

    top = counter.most_common(5)
    return {
        "top_weaknesses": [{"theme": t, "count": c} for t, c in top],
        "answers_analyzed": total_scored,
    }


def _bucketize(note: str) -> str | None:
    n = (note or "").lower()
    if "filler" in n:
        return "Frequent filler words (um, like, you know)"
    if "short" in n or "more detail" in n:
        return "Answers too brief — needs more elaboration"
    if "long" in n:
        return "Answers too long — be more concise"
    if "covered" in n and "concept" in n:
        return "Missing key technical concepts"
    if "off-topic" in n or "semantically distant" in n:
        return "Off-topic answers"
    if "face was visible" in n:
        return "Face left the camera frame"
    if "eye contact" in n:
        return "Poor eye contact with the camera"
    if "head turned" in n:
        return "Head turning away from camera"
    if "looking down" in n:
        return "Looking down too much"
    return None


# ---------------------------------------------------------------------------
# /compare  — side-by-side compare of any 2 of my sessions
# ---------------------------------------------------------------------------

@router.post("/compare", summary="Compare two of my completed sessions")
def compare(
    payload: dict = Body(..., example={"session_a": 1, "session_b": 2}),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    a_id = int(payload.get("session_a") or 0)
    b_id = int(payload.get("session_b") or 0)
    if not a_id or not b_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide two session ids: { session_a, session_b }.",
        )

    rows = {
        s.id: s for s in db.scalars(
            select(InterviewSession).where(
                InterviewSession.id.in_([a_id, b_id]),
                InterviewSession.user_id == current_user.id,
            )
        ).all()
    }
    if a_id not in rows or b_id not in rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or both sessions not found in your history.",
        )

    def _payload(s: InterviewSession) -> dict:
        summary = json.loads(s.scores_json) if s.scores_json else {}
        return {
            "session_id": s.id,
            "company": s.company,
            "role": s.role,
            "interview_type": s.interview_type,
            "started_at": s.started_at.isoformat(),
            "ended_at": s.ended_at.isoformat() if s.ended_at else None,
            "overall_score": s.overall_score,
            "scores": {
                k: summary.get(k)
                for k in ("technical", "communication", "confidence", "engagement")
            },
            "ai_feedback": s.ai_feedback,
        }

    return {"a": _payload(rows[a_id]), "b": _payload(rows[b_id])}
