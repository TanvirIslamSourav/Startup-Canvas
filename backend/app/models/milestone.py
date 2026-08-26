"""ORM model for the ``milestones`` table."""
from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    SmallInteger,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.db.types import UUIDType


class Milestone(UUIDPKMixin, TimestampMixin, Base):
    """A milestone attached to an idea."""

    __tablename__ = "milestones"
    __table_args__ = (
        CheckConstraint(
            "completion >= 0 AND completion <= 100",
            name="ck_milestones_completion",
        ),
    )

    idea_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(),
        ForeignKey("ideas.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    target_date: Mapped[date | None] = mapped_column(Date)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completion: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, server_default="0"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Milestone id={self.id} title={self.title!r}>"