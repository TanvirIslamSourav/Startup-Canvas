"""``python -m app.seeds`` entry point.

1) Initializes a fresh SQLite file DB with every table.
2) Stamps the alembic head revision so future tooling thinks the schema is at head.
3) Loads demo data so the UI has something to show on first launch.
"""
from __future__ import annotations

from app.seeds import init_sqlite_local, run_demo_seed


def main() -> None:
    path = init_sqlite_local()
    print(f"[seeds] SQLite database ready at {path}")
    summary = run_demo_seed()
    print("[seeds] Demo data inserted:", summary)


if __name__ == "__main__":
    main()