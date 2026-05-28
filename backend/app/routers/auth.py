"""
/api/auth — signup, login, "who am I"
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    SignupRequest,
    TokenResponse,
    UserResponse,
)
from app.services import auth_service

router = APIRouter()


@router.post(
    "/signup",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new account and receive a JWT",
)
def signup(payload: SignupRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user, token = auth_service.signup(db, payload)
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and receive a JWT",
)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user, token = auth_service.login(db, payload)
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Return the currently authenticated user",
)
def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)
