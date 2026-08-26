# Development Guide

> Local setup, debugging, scripts, and day‑to‑day workflow.

---

## 1. First time setup

```bash
git clone <your-fork-url> startup-canvas
cd startup-canvas
cp .env.example .env

# Option A — full Docker stack
docker compose up --build

# Option B — local
make install
make backend   # terminal 1
make frontend  # terminal 2
```

Frontend: <http://localhost:5173> · Backend Swagger: <http://localhost:8000/docs>

## 2. Scripts

| Command (from repo root) | What it does                                |
| ------------------------ | ------------------------------------------- |
| `make install`           | Install backend + frontend deps             |
| `make dev`               | `docker compose up --build`                 |
| `make backend`           | Run backend on :8000 with reload            |
| `make frontend`          | Run frontend on :5173 with HMR              |
| `make test`              | Run backend pytest + frontend vitest        |
| `make lint`              | Run ruff + eslint                           |
| `make build`             | Build frontend for production               |
| `make docker-up`         | Same as `make dev`                          |
| `make docker-down`       | `docker compose down -v`                    |
| `make clean`             | Remove caches and build artifacts           |

## 3. Backend layout

```
backend/
├── app/
│   ├── main.py             # FastAPI app factory
│   ├── core/               # config, logging, security, exceptions
│   ├── db/                 # session, base, dependencies
│   ├── models/             # SQLAlchemy ORM models
│   ├── schemas/            # Pydantic v2 schemas
│   ├── crud/               # repository functions
│   ├── services/           # business logic
│   ├── routers/            # FastAPI routers
│   ├── ai/                 # provider interface + mock
│   ├── seeds/              # demo data
│   └── utils/              # helpers
├── alembic/                # migrations
├── tests/                  # pytest suite
├── data/                   # ai json, uploads (gitignored)
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
└── alembic.ini
```

## 4. Adding a new module (vertical slice)

1. **Model** — `app/models/<module>.py` extending `Base, TimestampMixin`.
2. **Schema** — `app/schemas/<module>.py` with `*Create`, `*Update`, `*Read`.
3. **Repository** — `app/crud/<module>.py` pure DB functions.
4. **Service** — `app/services/<module>.py` business rules.
5. **Router** — `app/routers/<module>.py` thin wrapper.
6. **Tests** — `tests/test_<module>.py` happy path + 1 validation error.
7. **Migration** — `alembic revision --autogenerate -m "add_<module>"`.
8. **Frontend** — `frontend/src/features/<module>/` with list + form + tests.
9. **Route** — register in `App.tsx` and sidebar.
10. **Docs** — add to `docs/API.md` and `docs/DATABASE.md`.

## 5. Debugging

- **Backend** — VS Code launch config in `.vscode/launch.json` runs `uvicorn` with debugpy on port 5678.
- **Frontend** — Browser DevTools; React Query Devtools in dev only.
- **Database** — `psql` against `localhost:5432` (user `startup`, db `startup_canvas`).

## 6. Coding style

- Python: `ruff` + `black` (line length 100). Type hints required on public functions.
- TypeScript: `eslint` + `prettier`. `strict: true` in tsconfig.
- Commits: Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`).

## 7. Pre‑commit (optional but recommended)

`pre-commit` runs ruff, eslint, and a markdown linter on staged files. Install with:

```bash
pip install pre-commit
pre-commit install
```