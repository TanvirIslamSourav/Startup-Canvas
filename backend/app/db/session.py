"""Engine, session factory, and FastAPI dependencies."""
from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

_settings = get_settings()

# Pool tuning is only valid for non-SQLite engines.
_is_sqlite = _settings.database_url.startswith("sqlite")
_engine_kwargs: dict = {"pool_pre_ping": True, "future": True}
if not _is_sqlite:
    _engine_kwargs.update(pool_size=5, max_overflow=10)
else:
    _engine_kwargs["connect_args"] = {"check_same_thread": False}

engine: Engine = create_engine(_settings.database_url, **_engine_kwargs)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    future=True,
)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a session and ensuring close."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()