"""Security helpers (placeholder for future auth)."""
from __future__ import annotations

from app.core.config import get_settings


def generate_request_id() -> str:
    """Return a short opaque request id (placeholder)."""
    import uuid

    return uuid.uuid4().hex[:12]


def is_production() -> bool:
    return get_settings().environment == "production"