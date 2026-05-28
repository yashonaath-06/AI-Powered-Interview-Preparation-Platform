"""
Security utilities — password hashing & JWT creation/verification.

Why bcrypt?  It is the industry-standard slow hashing function. Even if
someone steals our database, brute-forcing a bcrypt-hashed password takes
years per password instead of milliseconds.

Why JWT?    Stateless authentication. The server signs a token containing
the user's id; the client sends it back on every request inside the
`Authorization: Bearer <token>` header.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings


# bcrypt with default cost (12)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------- Passwords ----------------------------------------------------
def hash_password(plain_password: str) -> str:
    """Hash a plain password — call this on signup / password-change."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True if the plain password matches the stored hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ---------- JWT ----------------------------------------------------------
def create_access_token(
    subject: str | int,
    extra_claims: dict[str, Any] | None = None,
    expires_minutes: int | None = None,
) -> str:
    """
    Produce a signed JWT.  `subject` is usually the user id.
    Extra claims are merged into the payload (e.g. role).
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes or settings.access_token_expire_minutes
    )
    payload: dict[str, Any] = {"sub": str(subject), "exp": expire}
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    """Verify a JWT and return its payload. Raises JWTError on failure."""
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])


__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_access_token",
    "JWTError",
]
