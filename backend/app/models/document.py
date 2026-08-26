"""ORM model for the ``documents`` table."""
from __future__ import annotations

import uuid

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.db.types import UUIDType

DOCUMENT_KINDS: tuple[str, ...] = (
    "business_plan",
    "pitch_deck",
    "note",
    "attachment",
)


class Document(UUIDPKMixin, TimestampMixin, Base):
    """A document reference attached to an idea."""

    __tablename__ = "documents"
    __table_args__ = (
        CheckConstraint(
            "kind IN ('business_plan','pitch_deck','note','attachment')",
            name="ck_documents_kind",
        ),
        CheckConstraint(
            "size_bytes IS NULL OR size_bytes >= 0",
            name="ck_documents_size",
        ),
    )

    idea_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(),
        ForeignKey("ideas.id", ondelete="CASCADE"),
        nullable=False,
    )
    kind: Mapped[str] = mapped_column(
        String(32), nullable=False, default="attachment", server_default="attachment"
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    file_path: Mapped[str | None] = mapped_column(String(512))
    mime_type: Mapped[str | None] = mapped_column(String(120))
    size_bytes: Mapped[int | None] = mapped_column(BigInteger)
    notes: Mapped[str | None] = mapped_column(Text)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Document id={self.id} title={self.title!r}>"