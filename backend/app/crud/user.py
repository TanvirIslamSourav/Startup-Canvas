"""CRUD repository for ``User`` rows."""
from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.user import User


def get(db: Session, user_id: UUID) -> User | None:
    return db.get(User, user_id)


def get_by_email(db: Session, email: str) -> User | None:
    stmt = select(User).where(User.email == email.lower())
    return db.execute(stmt).scalar_one_or_none()


def list_users(
    db: Session, *, limit: int, offset: int
) -> tuple[Sequence[User], int]:
    stmt = select(User).order_by(User.created_at.desc())
    items = db.execute(stmt.limit(limit).offset(offset)).scalars().all()
    total = int(db.execute(select(func.count()).select_from(User)).scalar_one())
    return items, total


def create(db: Session, *, email: str, display_name: str | None) -> User:
    user = User(email=email.lower(), display_name=display_name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_or_create_default(db: Session) -> User:
    """Return the seeded default user, creating it if necessary."""
    default = get_by_email(db, "sourav@startup.local")
    if default is not None:
        return default
    return create(db, email="sourav@startup.local", display_name="Sourav")
