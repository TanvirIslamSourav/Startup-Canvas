"""ORM model for the Lean Canvas (1:1 with idea)."""
from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.db.types import UUIDType


class LeanCanvas(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "lean_canvas"

    idea_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(),
        ForeignKey("ideas.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    problem: Mapped[str | None] = mapped_column(Text)
    solution: Mapped[str | None] = mapped_column(Text)
    key_metrics: Mapped[str | None] = mapped_column(Text)
    unique_value_prop: Mapped[str | None] = mapped_column(Text)
    unfair_advantage: Mapped[str | None] = mapped_column(Text)
    channels: Mapped[str | None] = mapped_column(Text)
    customer_segments: Mapped[str | None] = mapped_column(Text)
    cost_structure: Mapped[str | None] = mapped_column(Text)
    revenue_streams: Mapped[str | None] = mapped_column(Text)
