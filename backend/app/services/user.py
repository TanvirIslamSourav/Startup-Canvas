"""Business-logic layer for users."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.crud import user as user_crud
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def get_user(db: Session, user_id: UUID) -> User:
    user = user_crud.get(db, user_id)
    if user is None:
        raise NotFoundError(f"User {user_id} not found")
    return user


def list_users(
    db: Session, *, limit: int, offset: int
) -> tuple[list[User], int]:
    items, total = user_crud.list_users(db, limit=limit, offset=offset)
    return list(items), total


def create_user(db: Session, payload: UserCreate) -> User:
    if user_crud.get_by_email(db, payload.email) is not None:
        raise ConflictError(f"Email {payload.email!r} already exists")
    return user_crud.create(
        db, email=payload.email, display_name=payload.display_name
    )


def update_user(db: Session, user_id: UUID, payload: UserUpdate) -> User:
    user = get_user(db, user_id)
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(user, field, value)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
