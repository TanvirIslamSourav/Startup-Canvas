"""ORM model for the append-only activity log.

Each row records a meaningful domain event ("task.created",
"milestone.completed", etc.). The log is append-only by contract: no
UPDATE or DELETE is exposed through the service layer. The primary key
is a UUID for consistency with the rest of the schema; clients order
events by ``created_at``.
"""
from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UUIDPKMixin
from app.db.types import JSONBType, UUIDType

# Known event types. The DB column accepts any non-empty string up to 64
# chars; this list is the contract used by the service layer and the
# Pydantic schema for validation. New event types can be added without
# a schema migration.
ACTIVITY_EVENT_TYPES: tuple[str, ...] = (
    # Idea lifecycle
    "idea.created",
    "idea.updated",
    "idea.archived",
    "idea.deleted",
    # 1:1 canvases
    "lean_canvas.upserted",
    "business_canvas.upserted",
    "swot.upserted",
    "progress.upserted",
    "roadmap.upserted",
    # 1:N resources
    "competitor.created",
    "competitor.updated",
    "competitor.deleted",
    "persona.created",
    "persona.updated",
    "persona.deleted",
    "task.created",
    "task.status_changed",
    "task.updated",
    "task.deleted",
    "milestone.created",
    "milestone.completed",
    "milestone.updated",
    "milestone.deleted",
    "document.created",
    "document.updated",
    "document.deleted",
    "note.created",
    "note.updated",
    "note.deleted",
    "roadmap_stage.created",
    "roadmap_stage.completed",
    "roadmap_stage.updated",
    "roadmap_stage.deleted",
)


class Activity(UUIDPKMixin, Base):
    """Append-only activity log entry."""

    __tablename__ = "activities"

    idea_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(),
        ForeignKey("ideas.id", ondelete="CASCADE"),
        nullable=False,
    )
    actor_id: Mapped[uuid.UUID | None] = mapped_column(UUIDType(), nullable=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    event_data: Mapped[dict] = mapped_column(
        JSONBType(), nullable=False, default=dict
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Activity id={self.id} type={self.event_type}>"
