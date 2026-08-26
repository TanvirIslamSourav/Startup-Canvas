"""Pydantic v2 schemas for the Lean Canvas module."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

_TXT = Field(default=None, max_length=10_000)


class LeanCanvasBase(BaseModel):
    problem: str | None = _TXT
    solution: str | None = _TXT
    key_metrics: str | None = _TXT
    unique_value_prop: str | None = _TXT
    unfair_advantage: str | None = _TXT
    channels: str | None = _TXT
    customer_segments: str | None = _TXT
    cost_structure: str | None = _TXT
    revenue_streams: str | None = _TXT


class LeanCanvasUpdate(LeanCanvasBase):
    model_config = ConfigDict(extra="forbid")


class LeanCanvasRead(LeanCanvasBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    idea_id: UUID
    created_at: datetime
    updated_at: datetime