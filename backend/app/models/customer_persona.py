"""ORM model for the ``customer_personas`` table."""
from __future__ import annotations

import uuid

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    SmallInteger,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.db.types import UUIDType


class CustomerPersona(UUIDPKMixin, TimestampMixin, Base):
    """A user persona attached to an idea."""

    __tablename__ = "customer_personas"
    __table_args__ = (
        CheckConstraint(
            "age IS NULL OR (age >= 0 AND age <= 150)",
            name="ck_personas_age",
        ),
    )

    idea_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(),
        ForeignKey("ideas.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    age: Mapped[int | None] = mapped_column(SmallInteger)
    occupation: Mapped[str | None] = mapped_column(String(120))
    goals: Mapped[str | None] = mapped_column(Text)
    pain_points: Mapped[str | None] = mapped_column(Text)
    needs: Mapped[str | None] = mapped_column(Text)
    behaviour: Mapped[str | None] = mapped_column(Text)
    avatar_url: Mapped[str | None] = mapped_column(String(512))

    def __repr__(self) -> str:  # pragma: no cover
        return f"<CustomerPersona id={self.id} name={self.name!r}>"