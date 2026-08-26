"""ORM model for the ``competitors`` table."""
from __future__ import annotations

import uuid

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.db.types import JSONBType, UUIDType


class Competitor(UUIDPKMixin, TimestampMixin, Base):
    """A competitor analysis row attached to an idea."""

    __tablename__ = "competitors"
    __table_args__ = (
        CheckConstraint(
            "pricing IS NULL OR pricing >= 0",
            name="ck_competitors_pricing",
        ),
        Index("ix_competitors_idea", "idea_id"),
    )

    idea_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(),
        ForeignKey("ideas.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    website_url: Mapped[str | None] = mapped_column(String(255))
    pricing: Mapped[float | None] = mapped_column(Numeric(12, 2))
    pricing_currency: Mapped[str] = mapped_column(
        String(8), nullable=False, default="USD", server_default="USD"
    )
    strengths: Mapped[str | None] = mapped_column(Text)
    weaknesses: Mapped[str | None] = mapped_column(Text)
    features: Mapped[list[dict]] = mapped_column(
        JSONBType(),
        nullable=False,
        default=list,
        server_default="[]",
    )
    market_position: Mapped[str | None] = mapped_column(String(64))
    notes: Mapped[str | None] = mapped_column(Text)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Competitor id={self.id} name={self.name!r}>"