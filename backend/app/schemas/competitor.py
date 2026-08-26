"""Pydantic v2 schemas for the Competitors module."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

_TXT = Field(default=None, max_length=10_000)


class CompetitorBase(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    website_url: str | None = Field(default=None, max_length=255)
    pricing: Decimal | None = Field(default=None, ge=0)
    pricing_currency: str = Field(default="USD", max_length=8)
    strengths: str | None = _TXT
    weaknesses: str | None = _TXT
    features: list[dict] = Field(default_factory=list, max_length=100)
    market_position: str | None = Field(default=None, max_length=64)
    notes: str | None = _TXT


class CompetitorCreate(CompetitorBase):
    """Payload for ``POST``."""

    model_config = ConfigDict(extra="forbid")


class CompetitorUpdate(BaseModel):
    """Payload for ``PATCH`` — all fields optional."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=160)
    website_url: str | None = Field(default=None, max_length=255)
    pricing: Decimal | None = Field(default=None, ge=0)
    pricing_currency: str | None = Field(default=None, max_length=8)
    strengths: str | None = _TXT
    weaknesses: str | None = _TXT
    features: list[dict] | None = Field(default=None, max_length=100)
    market_position: str | None = Field(default=None, max_length=64)
    notes: str | None = _TXT


class CompetitorRead(CompetitorBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    idea_id: UUID
    created_at: datetime
    updated_at: datetime


class CompetitorListResponse(BaseModel):
    items: list[CompetitorRead]
    total: int = Field(ge=0)
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)