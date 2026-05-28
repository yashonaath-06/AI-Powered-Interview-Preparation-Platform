"""
Auth business-logic — kept in a service layer (not in the router) so it can
be reused by tests and the (future) admin panel.
"""
from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import LoginRequest, SignupRequest


def signup(db: Session, payload: SignupRequest) -> tuple[User, str]:
    """Create a new user. Returns (user, jwt). Raises 409 on duplicate email."""
    from app.config import settings

    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    # Auto-promote whitelisted emails (configured via ADMIN_EMAILS env).
    role = "admin" if payload.email.lower() in settings.admin_emails_list else "user"

    user = User(
        email=payload.email,
        full_name=payload.full_name.strip(),
        hashed_password=hash_password(payload.password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=user.id, extra_claims={"role": user.role})
    return user, token


def login(db: Session, payload: LoginRequest) -> tuple[User, str]:
    """Authenticate a user. Returns (user, jwt) or 401."""
    user = db.scalar(select(User).where(User.email == payload.email))
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    token = create_access_token(subject=user.id, extra_claims={"role": user.role})
    return user, token
