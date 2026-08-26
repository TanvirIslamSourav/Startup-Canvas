"""CRUD for the append-only ``Activity`` log.

Only ``append`` and ``list_for_idea`` are exposed — there is intentionally
no ``update`` or ``delete`` for activity rows. The log is the source of
truth for "what happened" and must remain immutable.
"""
from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.activity import Activity


def append(
    db: Session,
    *,
    idea_id: UUID,
    event_type: str,
    event_data: dict | None = None,
    actor_id: UUID | None = None,
) -> Activity:
    row = Activity(
        idea_id=idea_id,
        actor_id=actor_id,
        event_type=event_type,
        event_data=event_data or {},
        created_at=datetime.now(UTC),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get(db: Session, activity_id: UUID) -> Activity | None:
    return db.get(Activity, activity_id)


def list_for_idea(
    db: Session,
    idea_id: UUID,
    *,
    limit: int,
    offset: int,
    event_type: str | None = None,
) -> tuple[Sequence[Activity], int]:
    stmt = select(Activity).where(Activity.idea_id == idea_id)
    count_stmt = select(func.count()).select_from(Activity).where(
        Activity.idea_id == idea_id
    )
    if event_type is not None:
        stmt = stmt.where(Activity.event_type == event_type)
        count_stmt = count_stmt.where(Activity.event_type == event_type)
    stmt = stmt.order_by(Activity.created_at.desc())
    items = db.execute(stmt.limit(limit).offset(offset)).scalars().all()
    total = int(db.execute(count_stmt).scalar_one())
    return items, total
