"""ORM model for the ``startup_projects`` container table."""
from __future__ import annotations

import uuid

from sqlalchemy import CheckConstraint, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.db.types import JSONBType, UUIDType

PROJECT_STATUSES: tuple[str, ...] = ("active", "paused", "completed")


class StartupProject(UUIDPKMixin, TimestampMixin, Base):
    """Top-level container that groups ideas."""

    __tablename__ = "startup_projects"
    __table_args__ = (
        CheckConstraint(
            "status IN ('active','paused','completed')",
            name="ck_startup_projects_status",
        ),
    )

    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    stage: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="idea",
        server_default="idea",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="active",
        server_default="active",
    )
    tags: Mapped[list[str]] = mapped_column(
        JSONBType(),
        nullable=False,
        default=list,
        server_default="[]",
    )
    metadata_json: Mapped[dict[str, object]] = mapped_column(
        "metadata",
        JSONBType(),
        nullable=False,
        default=dict,
        server_default="{}",
    )

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"<StartupProject id={self.id} name={self.name!r} stage={self.stage}>"