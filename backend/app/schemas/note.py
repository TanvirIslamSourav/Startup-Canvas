"""Pydantic v2 schemas for the Notes module."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class NoteBase(BaseModel):
    body: str = Field(min_length=1, max_length=20_000)
    pinned: bool = False


class NoteCreate(NoteBase):
    """Payload for ``POST``."""

    model_config = ConfigDict(extra="forbid")


class NoteUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    body: str | None = Field(default=None, min_length=1, max_length=20_000)
    pinned: bool | None = None


class NoteRead(NoteBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    idea_id: UUID
    created_at: datetime
    updated_at: datetime


class NoteListResponse(BaseModel):
    items: list[NoteRead]
    total: int = Field(ge=0)
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)