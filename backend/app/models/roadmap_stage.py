"""ORM model for ordered roadmap stages nested under a roadmap."""
from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.db.types import UUIDType

if TYPE_CHECKING:
    from app.models.roadmap import Roadmap


class RoadmapStage(UUIDPKMixin, TimestampMixin, Base):
    """A single ordered stage inside a roadmap.

    ``position`` is a positive integer controlling ordering (lower =
    earlier). ``completion`` is a 0-100 percentage kept in sync by the
    service layer; stages with ``completion == 100`` are considered done.
    """

    __tablename__ = "roadmap_stages"
    __table_args__ = (
        CheckConstraint(
            "position >= 1", name="ck_roadmap_stages_position"
        ),
        CheckConstraint(
            "completion >= 0 AND completion <= 100",
            name="ck_roadmap_stages_completion",
        ),
    )

    roadmap_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(),
        ForeignKey("roadmaps.id", ondelete="CASCADE"),
        nullable=False,
    )
    position: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    target_date: Mapped[date | None] = mapped_column(Date)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completion: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, server_default="0"
    )

    roadmap: Mapped[Roadmap] = relationship(back_populates="stages")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<RoadmapStage id={self.id} pos={self.position} title={self.title!r}>"