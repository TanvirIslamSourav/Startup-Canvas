"""Pydantic v2 schemas for the Startup Project module."""
from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.startup_project import PROJECT_STATUSES

_NAME = Annotated[str, Field(min_length=1, max_length=160)]
_STAGE = Annotated[str, Field(min_length=1, max_length=32)]
_TAG = Annotated[str, Field(min_length=1, max_length=64)]


def _normalize_tags(value: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for raw in value:
        tag = raw.strip()
        if not tag or tag in seen:
            continue
        seen.add(tag)
        out.append(tag)
    return out


class StartupProjectBase(BaseModel):
    name: _NAME
    description: str | None = Field(default=None, max_length=10_000)
    stage: _STAGE = "idea"
    status: str = "active"
    tags: list[str] = Field(default_factory=list, max_length=50)
    metadata_json: dict[str, object] = Field(default_factory=dict)

    @field_validator("status")
    @classmethod
    def _validate_status(cls, value: str) -> str:
        if value not in PROJECT_STATUSES:
            raise ValueError(
                f"status must be one of {sorted(PROJECT_STATUSES)} (got {value!r})"
            )
        return value

    @field_validator("tags")
    @classmethod
    def _normalize_tags(cls, value: list[str]) -> list[str]:
        # Reuse module-level helper.
        from app.schemas.startup_project import _normalize_tags as norm
        return norm(value)


class StartupProjectCreate(StartupProjectBase):
    owner_id: UUID


class StartupProjectUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: _NAME | None = None
    description: str | None = Field(default=None, max_length=10_000)
    stage: _STAGE | None = None
    status: str | None = None
    tags: list[str] | None = Field(default=None, max_length=50)
    metadata_json: dict[str, object] | None = None

    @field_validator("status")
    @classmethod
    def _validate_status(cls, value: str | None) -> str | None:
        if value is not None and value not in PROJECT_STATUSES:
            raise ValueError(
                f"status must be one of {sorted(PROJECT_STATUSES)} (got {value!r})"
            )
        return value

    @field_validator("tags")
    @classmethod
    def _normalize_tags(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        from app.schemas.startup_project import _normalize_tags as norm
        return norm(value)


class StartupProjectRead(StartupProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    owner_id: UUID
    created_at: datetime
    updated_at: datetime


class StartupProjectListResponse(BaseModel):
    items: list[StartupProjectRead]
    total: int = Field(ge=0)
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)
