"""Cross-dialect column types.

The PostgreSQL ``JSONB`` and ``UUID`` types are mapped to portable
equivalents when running against SQLite (used in tests).
"""
from __future__ import annotations

import json
import uuid

from sqlalchemy import JSON, TypeDecorator
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID


class JSONBType(TypeDecorator):
    """JSONB on Postgres, portable JSON elsewhere (e.g. SQLite tests)."""

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):  # type: ignore[override]
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB())
        return dialect.type_descriptor(JSON())

    def process_bind_param(self, value, dialect):  # type: ignore[override]
        if dialect.name == "postgresql":
            return value
        # Store as plain JSON text; JSON column handles serialization.
        return value

    def process_result_value(self, value, dialect):  # type: ignore[override]
        if value is None:
            return None
        if isinstance(value, list | dict):
            return value
        if dialect.name != "postgresql" and isinstance(value, bytes | bytearray):
            value = value.decode("utf-8")
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return value


class UUIDType(TypeDecorator):
    """UUID native on Postgres, CHAR(36) elsewhere for broad test support."""

    impl = PG_UUID
    cache_ok = True

    def load_dialect_impl(self, dialect):  # type: ignore[override]
        from sqlalchemy import CHAR

        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):  # type: ignore[override]
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        if isinstance(value, uuid.UUID):
            return str(value)
        return str(uuid.UUID(str(value)))

    def process_result_value(self, value, dialect):  # type: ignore[override]
        if value is None or isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(value)