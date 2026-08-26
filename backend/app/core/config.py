"""Application settings loaded from environment."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized configuration.

    All values are loaded from environment variables (or `.env` file).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # General
    environment: Literal["development", "test", "production"] = "development"
    log_level: Literal["debug", "info", "warning", "error"] = "info"
    api_prefix: str = "/api/v1"
    # Stored as raw string and split below so a comma-separated
    # ``CORS_ORIGINS=...`` env var works on both pydantic-settings v2.6 and v3.
    cors_origins_raw: str = Field(
        default="http://localhost:5173,http://localhost:8080",
        alias="CORS_ORIGINS",
    )

    # Database
    database_url: str = (
        "postgresql+psycopg://startup:startup@localhost:5432/startup_canvas"
    )

    # Security (used in future auth)
    secret_key: str = "change-me-in-production"

    # AI advisor
    startup_advisor_provider: Literal["mock", "openai", "gemini", "claude", "groq", "ollama"] = "mock"
    # Default to <repo>/backend/data/ai so the app works whether started from
    # the repo root or from inside backend/.  ``parents[1]`` of ``app/core/`` is
    # the ``backend`` directory.
    ai_data_dir: str = str(
        Path(__file__).resolve().parents[1] / "data" / "ai"
    )

    # CORS / host
    cors_allow_credentials: bool = True

    @property
    def cors_origins(self) -> list[str]:
        """Comma-separated string split into a list."""
        return [item.strip() for item in self.cors_origins_raw.split(",") if item.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cached settings accessor."""
    return Settings()