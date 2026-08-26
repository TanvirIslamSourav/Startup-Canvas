"""Business-logic layer for the append-only Activity log.

Only ``append`` (called by other services to record events) and ``list``
are exposed. By design there is no ``update`` or ``delete`` API.
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.crud import activity as activity_crud
from app.models.activity import Activity
from app.services._parent import ensure_idea_exists


def list_for_idea(
    db: Session,
    idea_id: UUID,
    *,
    limit: int,
    offset: int,
    event_type: str | None = None,
) -> tuple[Sequence[Activity], int]:
    ensure_idea_exists(db, idea_id)
    return activity_crud.list_for_idea(
        db, idea_id, limit=limit, offset=offset, event_type=event_type
    )


def get(db: Session, idea_id: UUID, activity_id: UUID) -> Activity:
    ensure_idea_exists(db, idea_id)
    row = activity_crud.get(db, activity_id)
    if row is None or row.idea_id != idea_id:
        from app.core.exceptions import NotFoundError

        raise NotFoundError(
            message=f"Activity {activity_id} not found for idea {idea_id}",
            details={"resource": "activity", "id": str(activity_id)},
        )
    return row


def record(
    db: Session,
    *,
    idea_id: UUID,
    event_type: str,
    event_data: dict[str, Any] | None = None,
    actor_id: UUID | None = None,
) -> Activity:
    """Internal helper used by other services to emit a domain event."""
    return activity_crud.append(
        db,
        idea_id=idea_id,
        event_type=event_type,
        event_data=event_data,
        actor_id=actor_id,
    )