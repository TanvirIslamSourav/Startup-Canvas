"""ORM model for the per-idea progress tracker."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UUIDPKMixin
from app.db.types import UUIDType


class ProgressTracker(UUIDPKMixin, Base):
    __tablename__ = "progress_tracker"
    __table_args__ = (
        CheckConstraint(
            "overall_completion >= 0 AND overall_completion <= 100",
            name="ck_progress_overall",
        ),
        CheckConstraint(
            "health_score >= 0 AND health_score <= 100",
            name="ck_progress_health",
        ),
        CheckConstraint(
            "milestone_progress >= 0 AND milestone_progress <= 100",
            name="ck_progress_milestone",
        ),
        CheckConstraint(
            "task_completion >= 0 AND task_completion <= 100",
            name="ck_progress_task",
        ),
    )

    idea_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(),
        ForeignKey("ideas.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    overall_completion: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0
    )
    health_score: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    milestone_progress: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0
    )
    task_completion: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    last_computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False
    )
