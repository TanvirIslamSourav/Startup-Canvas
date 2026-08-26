"""Pytest configuration: shared fixtures."""
from __future__ import annotations

import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool

# Use in-memory SQLite for tests so we never touch a real DB.
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("ENVIRONMENT", "test")

# Import after env override so the engine binds to SQLite.
# Reset engine to point at SQLite and create tables in an in-memory db.
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import session as session_module
from app.db.base import Base
from app.main import create_app

# StaticPool + a single shared connection so every Session sees the same
# in-memory database. Without it, each connection gets its own empty DB.
_test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    future=True,
)
_TestingSessionLocal = sessionmaker(
    bind=_test_engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    future=True,
)

session_module.engine = _test_engine
session_module.SessionLocal = _TestingSessionLocal


def _override_get_db() -> Generator:
    db = _TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def _create_tables() -> None:
    # Import models so they register with Base.metadata.
    import app.models  # noqa: F401
    Base.metadata.create_all(_test_engine)


@pytest.fixture(autouse=True)
def _clean_tables() -> Generator:
    """Truncate every table between tests so each test starts fresh."""
    yield
    # Use the ORM's metadata to issue DELETEs (preserves autoincrement/sequences).
    for table in reversed(Base.metadata.sorted_tables):
        with _test_engine.begin() as conn:
            conn.execute(table.delete())


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    app = create_app()
    app.dependency_overrides[session_module.get_db] = _override_get_db
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def db_session() -> Generator:
    """Plain DB session (no HTTP layer) for setup helpers."""
    db = _TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()