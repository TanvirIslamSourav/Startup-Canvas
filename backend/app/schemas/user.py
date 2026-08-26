"""Pydantic v2 schemas for the User module."""
from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

_EMAIL = Annotated[EmailStr, Field(max_length=255)]


class UserCreate(BaseModel):
    email: _EMAIL
    display_name: str | None = Field(default=None, max_length=120)
    locale: str = Field(default="en", max_length=8)
    theme: str = Field(default="system", max_length=16)


class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    display_name: str | None = Field(default=None, max_length=120)
    locale: str | None = Field(default=None, max_length=8)
    theme: str | None = Field(default=None, max_length=16)
    is_active: bool | None = None


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    display_name: str | None
    locale: str
    theme: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserListResponse(BaseModel):
    items: list[UserRead]
    total: int = Field(ge=0)
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)
