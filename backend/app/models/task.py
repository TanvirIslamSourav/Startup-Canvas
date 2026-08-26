"""ORM model for the ``tasks`` table."""
from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    SmallInteger,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.db.types import UUIDType

TASK_PRIORITIES: tuple[str, ...] = ("low", "medium", "high", "urgent")
TASK_STATUSES: tuple[str, ...] = (
    "todo",
    "in_progress",
    "blocked",
    "done",
)


class Task(UUIDPKMixin, TimestampMixin, Base):
    """A task attached to an idea."""

    __tablename__ = "tasks"
    __table_args__ = (
        CheckConstraint(
            "priority IN ('low','medium','high','urgent')",
            name="ck_tasks_priority",
        ),
        CheckConstraint(
            "status IN ('todo','in_progress','blocked','done')",
            name="ck_tasks_status",
        ),
        CheckConstraint(
            "progress >= 0 AND progress <= 100",
            name="ck_tasks_progress",
        ),
        Index("ix_tasks_idea_status", "idea_id", "status"),
        Index("ix_tasks_due_date", "due_date"),
    )

    idea_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(),
        ForeignKey("ideas.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(
        String(16), nullable=False, default="medium", server_default="medium"
    )
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="todo", server_default="todo"
    )
    progress: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, server_default="0"
    )
    due_date: Mapped[date | None] = mapped_column(Date)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Task id={self.id} title={self.title!r}>"