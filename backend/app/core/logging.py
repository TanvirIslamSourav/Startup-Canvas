"""Structured logging via loguru."""
from __future__ import annotations

import sys

from loguru import logger

from app.core.config import get_settings


def configure_logging() -> None:
    """Configure loguru for stdout JSON-friendly output."""
    settings = get_settings()
    logger.remove()
    logger.add(
        sys.stdout,
        level=settings.log_level.upper(),
        serialize=settings.environment == "production",
        backtrace=False,
        diagnose=False,
        enqueue=True,
    )


def get_logger():
    """Return the configured logger."""
    return logger