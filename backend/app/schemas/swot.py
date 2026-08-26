"""Pydantic v2 schemas for the SWOT module."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

_TXT = Field(default=None, max_length=10_000)


class SwotBase(BaseModel):
    strengths: str | None = _TXT
    weaknesses: str | None = _TXT
    opportunities: str | None = _TXT
    threats: str | None = _TXT
    score: int = Field(default=0, ge=0, le=100)
    summary: str | None = _TXT


class SwotUpdate(SwotBase):
    model_config = ConfigDict(extra="forbid")


class SwotRead(SwotBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    idea_id: UUID
    created_at: datetime
    updated_at: datetime