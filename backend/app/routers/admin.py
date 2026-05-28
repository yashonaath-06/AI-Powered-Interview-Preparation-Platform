"""
/api/admin — admin-only endpoints (Phase 12).

All routes require role=admin. The Phase-6 dependency `require_admin` does
this gating. To grant yourself admin access:

    1. Set ADMIN_EMAILS=you@example.com in .env, then sign up; OR
    2. Run `python -m app.cli make-admin you@example.com` for an
       existing user.

Endpoints
---------
Users
    GET    /users                 paginated, searchable
    PATCH  /users/{id}/role       toggle user|admin (cannot demote yourself)
    DELETE /users/{id}            delete user + cascade their data

Question bank
    POST   /questions             create question
    PATCH  /questions/{id}        update question
    DELETE /questions/{id}        delete question

Activity / stats
    GET    /sessions              recent sessions across ALL users
    GET    /stats                 platform-wide counters and aggregates
"""
from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, func, or_, select
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_admin
from app.models.interview import Answer, InterviewSession
from app.models.question import Question
from app.models.user import User
from app.schemas.question import QuestionCreate, QuestionOut, QuestionUpdate
from app.schemas.user import UserPublic

router = APIRouter()


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

@router.get("/users", summary="List users (paginated + searchable)")
def list_users(
    q: str | None = Query(default=None, description="Search by email or name"),
    role: str | None = Query(default=None, description="Filter by role"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    stmt = select(User)
    if q:
        like = f"%{q.lower()}%"
        stmt = stmt.where(or_(
            func.lower(User.email).like(like),
            func.lower(User.full_name).like(like),
        ))
    if role:
        stmt = stmt.where(User.role == role)

    total = int(db.scalar(select(func.count()).select_from(stmt.subquery())) or 0)
    rows = list(db.scalars(
        stmt.order_by(desc(User.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all())

    return {
        "items": [UserPublic.model_validate(u).model_dump() for u in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.patch(
    "/users/{user_id}/role",
    response_model=UserPublic,
    summary="Promote / demote a user (admin only). Cannot demote yourself.",
)
def update_user_role(
    user_id: int,
    body: dict,
    db: Session = Depends(get_db),
    me: User = Depends(require_admin),
):
    new_role = (body.get("role") or "").strip().lower()
    if new_role not in ("user", "admin"):
        raise HTTPException(status_code=400, detail="role must be 'user' or 'admin'")
    if user_id == me.id and new_role != "admin":
        raise HTTPException(status_code=400, detail="You cannot demote yourself.")

    target = db.get(User, user_id)
    if target is None:
        raise HTTPException(status_code=404, detail="User not found")

    target.role = new_role
    db.commit()
    db.refresh(target)
    return UserPublic.model_validate(target)


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user (cascades to their sessions and resumes).",
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    me: User = Depends(require_admin),
):
    if user_id == me.id:
        raise HTTPException(status_code=400, detail="You cannot delete yourself.")
    target = db.get(User, user_id)
    if target is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(target)
    db.commit()
    return None


# ---------------------------------------------------------------------------
# Question bank CRUD
# ---------------------------------------------------------------------------

@router.post(
    "/questions",
    response_model=QuestionOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a question (admin only)",
)
def create_question(
    payload: QuestionCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    q = Question(
        text=payload.text,
        category=payload.category,
        difficulty=payload.difficulty,
        company=payload.company,
        role=payload.role,
        expected_keywords=(
            json.dumps(payload.expected_keywords)
            if payload.expected_keywords else None
        ),
        sample_answer=payload.sample_answer,
    )
    db.add(q)
    db.commit()
    db.refresh(q)

    return _question_out(q)


@router.patch(
    "/questions/{question_id}",
    response_model=QuestionOut,
    summary="Update a question",
)
def update_question(
    question_id: int,
    payload: QuestionUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    q = db.get(Question, question_id)
    if q is None:
        raise HTTPException(status_code=404, detail="Question not found")

    data = payload.model_dump(exclude_unset=True)
    if "expected_keywords" in data:
        kw = data.pop("expected_keywords")
        q.expected_keywords = json.dumps(kw) if kw else None
    for k, v in data.items():
        setattr(q, k, v)

    db.commit()
    db.refresh(q)
    return _question_out(q)


@router.delete(
    "/questions/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a question",
)
def delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    q = db.get(Question, question_id)
    if q is None:
        raise HTTPException(status_code=404, detail="Question not found")
    db.delete(q)
    db.commit()


# ---------------------------------------------------------------------------
# Activity & platform stats
# ---------------------------------------------------------------------------

@router.get("/sessions", summary="Recent sessions across all users")
def recent_sessions(
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    rows = list(db.execute(
        select(
            InterviewSession,
            User.email,
            User.full_name,
        )
        .join(User, InterviewSession.user_id == User.id)
        .order_by(desc(InterviewSession.started_at))
        .limit(limit)
    ).all())

    return {
        "items": [
            {
                "session_id": s.id,
                "user_id": s.user_id,
                "user_email": email,
                "user_name": name,
                "company": s.company,
                "role": s.role,
                "interview_type": s.interview_type,
                "status": s.status,
                "started_at": s.started_at.isoformat(),
                "ended_at": s.ended_at.isoformat() if s.ended_at else None,
                "overall_score": s.overall_score,
            }
            for s, email, name in rows
        ]
    }


@router.get("/stats", summary="Platform-wide stats (admin)")
def platform_stats(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    user_count    = int(db.scalar(select(func.count(User.id))) or 0)
    admin_count   = int(db.scalar(select(func.count(User.id)).where(User.role == "admin")) or 0)
    question_count = int(db.scalar(select(func.count(Question.id))) or 0)
    session_count = int(db.scalar(select(func.count(InterviewSession.id))) or 0)
    completed     = int(db.scalar(select(func.count(InterviewSession.id)).where(
        InterviewSession.status == "completed"
    )) or 0)
    answer_count  = int(db.scalar(select(func.count(Answer.id))) or 0)
    platform_avg  = db.scalar(select(func.avg(InterviewSession.overall_score)).where(
        InterviewSession.overall_score.is_not(None)
    ))

    completion_rate = round(completed / session_count * 100, 1) if session_count else 0.0

    # Top 5 most popular companies among completed sessions
    top_companies = list(db.execute(
        select(
            InterviewSession.company,
            func.count(InterviewSession.id),
        )
        .where(InterviewSession.company.is_not(None))
        .group_by(InterviewSession.company)
        .order_by(desc(func.count(InterviewSession.id)))
        .limit(5)
    ).all())

    # Top 5 newest signups
    newest_users = list(db.scalars(
        select(User).order_by(desc(User.created_at)).limit(5)
    ).all())

    return {
        "user_count": user_count,
        "admin_count": admin_count,
        "question_count": question_count,
        "session_count": session_count,
        "completed_session_count": completed,
        "completion_rate_pct": completion_rate,
        "answer_count": answer_count,
        "platform_average_score": (
            round(float(platform_avg), 2) if platform_avg is not None else None
        ),
        "top_companies": [
            {"company": c, "count": int(n)} for c, n in top_companies
        ],
        "newest_users": [
            {
                "id": u.id,
                "email": u.email,
                "full_name": u.full_name,
                "role": u.role,
                "created_at": u.created_at.isoformat(),
            }
            for u in newest_users
        ],
    }


# ---------------------------------------------------------------------------
# Internal
# ---------------------------------------------------------------------------

def _question_out(q: Question) -> QuestionOut:
    kw = None
    if q.expected_keywords:
        try:
            kw = json.loads(q.expected_keywords)
        except Exception:  # noqa: BLE001
            kw = None
    return QuestionOut.model_validate({
        "id": q.id,
        "text": q.text,
        "category": q.category,
        "difficulty": q.difficulty,
        "company": q.company,
        "role": q.role,
        "expected_keywords": kw,
        "sample_answer": q.sample_answer,
        "created_at": q.created_at,
    })
