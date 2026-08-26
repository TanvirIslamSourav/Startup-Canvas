"""ORM model for the ``notes`` table."""
from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.db.types import UUIDType


class Note(UUIDPKMixin, TimestampMixin, Base):
    """A free-form note attached to an idea."""

    __tablename__ = "notes"

    idea_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(),
        ForeignKey("ideas.id", ondelete="CASCADE"),
        nullable=False,
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)
    pinned: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Note id={self.id} pinned={self.pinned}>"