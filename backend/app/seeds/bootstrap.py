"""Database bootstrap helpers (no alembic needed for SQLite local dev)."""
from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import Engine

from app.core.config import get_settings
from app.db.base import Base


def get_engine(database_url: str | None = None) -> Engine:
    """Build a SQLAlchemy engine for the given (or configured) URL."""
    url = database_url or get_settings().database_url
    kwargs: dict = {"pool_pre_ping": True, "future": True}
    if url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    else:
        kwargs.update(pool_size=5, max_overflow=10)
    return create_engine(url, **kwargs)


def create_all_tables(engine: Engine) -> None:
    """Create every table registered with ``Base.metadata``."""
    # Ensure all model modules are imported.
    import app.models  # noqa: F401

    Base.metadata.create_all(engine)


def stamp_alembic_head(engine: Engine, revision: str = "0004_canvas_swot_progress") -> None:
    """Insert a single row into ``alembic_version`` so Alembic considers
    the schema fully migrated.  This lets the local SQLite bootstrap coexist
    with the production Postgres migrations.
    """
    insp = inspect(engine)
    if "alembic_version" not in insp.get_table_names():
        from sqlalchemy import text

        with engine.begin() as conn:
            conn.execute(
                text(
                    "CREATE TABLE alembic_version ("
                    "    version_num VARCHAR(32) NOT NULL,"
                    "    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)"
                    ")"
                )
            )
    # Always upsert the head revision row.
    from sqlalchemy import text

    with engine.begin() as conn:
        conn.execute(text("DELETE FROM alembic_version"))
        conn.execute(text(f"INSERT INTO alembic_version (version_num) VALUES ('{revision}')"))


def init_sqlite_local(db_path: str | os.PathLike[str] = "./startup_canvas.db") -> Path:
    """Initialize a fresh SQLite file DB with all tables and the alembic stamp.

    Returns the resolved database file path.  Safe to call repeatedly —
    existing tables are left alone.
    """
    p = Path(db_path).resolve()
    p.parent.mkdir(parents=True, exist_ok=True)
    engine = get_engine(f"sqlite:///{p.as_posix()}")
    create_all_tables(engine)
    stamp_alembic_head(engine)
    return p


if __name__ == "__main__":  # pragma: no cover
    path = init_sqlite_local()
    print(f"SQLite database ready at {path}")