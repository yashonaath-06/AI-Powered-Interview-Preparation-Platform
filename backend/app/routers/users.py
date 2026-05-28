"""/api/users — profile read & update."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.user import UserPublic, UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserPublic, summary="Get my profile")
def get_my_profile(current_user: User = Depends(get_current_user)) -> UserPublic:
    return UserPublic.model_validate(current_user)


@router.patch("/me", response_model=UserPublic, summary="Update my profile")
def update_my_profile(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserPublic:
    if payload.full_name is not None:
        current_user.full_name = payload.full_name.strip()

    db.commit()
    db.refresh(current_user)
    return UserPublic.model_validate(current_user)
