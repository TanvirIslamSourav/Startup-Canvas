"""Pydantic v2 schemas for the Business Model Canvas module."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

_TXT = Field(default=None, max_length=10_000)


class BusinessCanvasBase(BaseModel):
    key_partners: str | None = _TXT
    key_activities: str | None = _TXT
    key_resources: str | None = _TXT
    value_propositions: str | None = _TXT
    customer_relationships: str | None = _TXT
    channels: str | None = _TXT
    customer_segments: str | None = _TXT
    cost_structure: str | None = _TXT
    revenue_streams: str | None = _TXT


class BusinessCanvasUpdate(BusinessCanvasBase):
    model_config = ConfigDict(extra="forbid")


class BusinessCanvasRead(BusinessCanvasBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    idea_id: UUID
    created_at: datetime
    updated_at: datetime