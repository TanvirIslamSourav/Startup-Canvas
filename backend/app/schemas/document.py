"""Pydantic v2 schemas for the Documents module."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.document import DOCUMENT_KINDS

_TXT = Field(default=None, max_length=10_000)


class DocumentBase(BaseModel):
    kind: str = "attachment"
    title: str = Field(min_length=1, max_length=200)
    file_path: str | None = Field(default=None, max_length=512)
    mime_type: str | None = Field(default=None, max_length=120)
    size_bytes: int | None = Field(default=None, ge=0)
    notes: str | None = _TXT

    @field_validator("kind")
    @classmethod
    def _check_kind(cls, value: str) -> str:
        if value not in DOCUMENT_KINDS:
            raise ValueError(
                f"kind must be one of {sorted(DOCUMENT_KINDS)} (got {value!r})"
            )
        return value


class DocumentCreate(DocumentBase):
    """Payload for ``POST``."""

    model_config = ConfigDict(extra="forbid")


class DocumentUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: str | None = None
    title: str | None = Field(default=None, min_length=1, max_length=200)
    file_path: str | None = Field(default=None, max_length=512)
    mime_type: str | None = Field(default=None, max_length=120)
    size_bytes: int | None = Field(default=None, ge=0)
    notes: str | None = _TXT

    @field_validator("kind")
    @classmethod
    def _check_kind(cls, value: str | None) -> str | None:
        if value is not None and value not in DOCUMENT_KINDS:
            raise ValueError(
                f"kind must be one of {sorted(DOCUMENT_KINDS)} (got {value!r})"
            )
        return value


class DocumentRead(DocumentBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    idea_id: UUID
    created_at: datetime
    updated_at: datetime


class DocumentListResponse(BaseModel):
    items: list[DocumentRead]
    total: int = Field(ge=0)
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)