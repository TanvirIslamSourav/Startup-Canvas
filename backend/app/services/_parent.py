"""Helpers for service modules that hang off an ``Idea`` parent."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.crud import idea as idea_crud


def ensure_idea_exists(db: Session, idea_id: UUID) -> None:
    """Raise ``NotFoundError`` if the parent idea does not exist."""
    if idea_crud.get(db, idea_id) is None:
        raise NotFoundError(
            message=f"Idea {idea_id} not found",
            details={"resource": "idea", "id": str(idea_id)},
        )