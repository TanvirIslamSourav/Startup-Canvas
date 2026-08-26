"""SQLAlchemy declarative base and common mixins."""
from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.db.types import UUIDType


def utcnow() -> datetime:
    """Timezone-aware UTC now (Python 3.11+ has ``datetime.UTC`` but using a helper keeps things portable)."""
    return datetime.now(UTC)


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""

    pass


class UUIDPKMixin:
    """Adds a UUID primary key column.

    Uses the cross-dialect ``UUIDType`` so the same column works on both
    PostgreSQL (native ``UUID``) and SQLite (``CHAR(36)``).
    """

    id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(),
        primary_key=True,
        default=uuid.uuid4,
    )


class TimestampMixin:
    """Adds ``created_at`` / ``updated_at`` columns."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )