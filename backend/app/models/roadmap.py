"""ORM model for the per-idea roadmap."""
from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, ForeignKey, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.db.types import UUIDType

if TYPE_CHECKING:
    from app.models.roadmap_stage import RoadmapStage


class Roadmap(UUIDPKMixin, TimestampMixin, Base):
    """A high-level roadmap attached to an idea.

    The roadmap holds ordered ``RoadmapStage`` rows. ``completion`` is
    server-computed from the average of its stages' completion values
    (0-100); the service layer is responsible for keeping it in sync.
    """

    __tablename__ = "roadmaps"
    __table_args__ = (
        CheckConstraint(
            "completion >= 0 AND completion <= 100",
            name="ck_roadmaps_completion",
        ),
    )

    idea_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(),
        ForeignKey("ideas.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)
    target_completion: Mapped[date | None] = mapped_column(Date)
    completion: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, server_default="0"
    )

    stages: Mapped[list[RoadmapStage]] = relationship(
        back_populates="roadmap",
        cascade="all, delete-orphan",
        order_by="RoadmapStage.position",
        passive_deletes=True,
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Roadmap id={self.id} title={self.title!r}>"
