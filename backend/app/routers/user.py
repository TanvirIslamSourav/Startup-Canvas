"""HTTP routes for ``/users``."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserCreate, UserListResponse, UserRead, UserUpdate
from app.services import user as user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "",
    response_model=UserListResponse,
    summary="List users",
)
def list_users(
    db: Session = Depends(get_db),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> UserListResponse:
    items, total = user_service.list_users(db, limit=limit, offset=offset)
    return UserListResponse(items=items, total=total, limit=limit, offset=offset)


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a user",
)
def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    user = user_service.create_user(db, payload)
    return UserRead.model_validate(user)


@router.get("/{user_id}", response_model=UserRead, summary="Get one user")
def get_user(user_id: UUID, db: Session = Depends(get_db)) -> UserRead:
    user = user_service.get_user(db, user_id)
    return UserRead.model_validate(user)


@router.patch("/{user_id}", response_model=UserRead, summary="Update a user")
def update_user(
    user_id: UUID, payload: UserUpdate, db: Session = Depends(get_db)
) -> UserRead:
    user = user_service.update_user(db, user_id, payload)
    return UserRead.model_validate(user)
