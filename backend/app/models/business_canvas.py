"""ORM model for the Business Model Canvas (1:1 with idea)."""
from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.db.types import UUIDType


class BusinessCanvas(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "business_canvas"

    idea_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(),
        ForeignKey("ideas.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    key_partners: Mapped[str | None] = mapped_column(Text)
    key_activities: Mapped[str | None] = mapped_column(Text)
    key_resources: Mapped[str | None] = mapped_column(Text)
    value_propositions: Mapped[str | None] = mapped_column(Text)
    customer_relationships: Mapped[str | None] = mapped_column(Text)
    channels: Mapped[str | None] = mapped_column(Text)
    customer_segments: Mapped[str | None] = mapped_column(Text)
    cost_structure: Mapped[str | None] = mapped_column(Text)
    revenue_streams: Mapped[str | None] = mapped_column(Text)
