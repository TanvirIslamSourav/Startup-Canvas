"""ORM model for the SWOT analysis (1:1 with idea)."""
from __future__ import annotations

import uuid

from sqlalchemy import CheckConstraint, ForeignKey, SmallInteger, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.db.types import UUIDType


class Swot(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "swot"
    __table_args__ = (
        CheckConstraint("score >= 0 AND score <= 100", name="ck_swot_score"),
    )

    idea_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(),
        ForeignKey("ideas.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    strengths: Mapped[str | None] = mapped_column(Text)
    weaknesses: Mapped[str | None] = mapped_column(Text)
    opportunities: Mapped[str | None] = mapped_column(Text)
    threats: Mapped[str | None] = mapped_column(Text)
    score: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    summary: Mapped[str | None] = mapped_column(Text)
