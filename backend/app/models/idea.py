"""ORM model for the ``ideas`` table."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    SmallInteger,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.db.types import JSONBType, UUIDType

# Allowed status values (kept in code so Alembic emits a CHECK constraint
# identical to the one documented in docs/DATABASE.md).
IDEA_STATUSES: tuple[str, ...] = (
    "draft",
    "validating",
    "planned",
    "in_progress",
    "on_hold",
    "completed",
    "archived",
)


class Idea(UUIDPKMixin, TimestampMixin, Base):
    """A startup idea under a ``startup_project``."""

    __tablename__ = "ideas"
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft','validating','planned','in_progress',"
            "'on_hold','completed','archived')",
            name="ck_ideas_status",
        ),
        CheckConstraint("priority >= 0 AND priority <= 5", name="ck_ideas_priority"),
        CheckConstraint("score >= 0 AND score <= 100", name="ck_ideas_score"),
        Index("ix_ideas_project_status", "project_id", "status"),
        Index("ix_ideas_category", "category"),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(),
        ForeignKey("startup_projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    problem: Mapped[str | None] = mapped_column(Text)
    solution: Mapped[str | None] = mapped_column(Text)
    audience: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(64))
    tags: Mapped[list[str]] = mapped_column(
        JSONBType(),
        nullable=False,
        default=list,
        server_default="[]",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="draft",
        server_default="draft",
    )
    priority: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=0,
        server_default="0",
    )
    score: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=0,
        server_default="0",
    )
    is_archived: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"<Idea id={self.id} title={self.title!r} status={self.status}>"