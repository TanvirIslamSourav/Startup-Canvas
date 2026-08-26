# Contributing to Startup Canvas

Thanks for your interest in contributing! This document explains how to set up
the project locally, follow our coding standards, and submit a high-quality
pull request.

## Code of Conduct

By participating, you agree to abide by the
[Code of Conduct](CODE_OF_CONDUCT.md). Please read it before contributing.

## Project layout

| Folder      | Purpose                                                    |
| ----------- | ---------------------------------------------------------- |
| `frontend/` | React 19 + TypeScript + Vite single-page app               |
| `backend/`  | FastAPI + SQLAlchemy 2.0 + Alembic REST API                |
| `database/` | Optional SQL snapshots / fixtures                          |
| `docker/`   | Dockerfiles + nginx reverse-proxy config                   |
| `docs/`     | Architecture, API, deployment, development guides          |
| `assets/`   | Brand / logo assets                                       |

See [`docs/FOLDER_STRUCTURE.md`](docs/FOLDER_STRUCTURE.md) for the annotated
tree, and [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the system
diagram.

## Local development

### One-command (Docker)

```bash
cp .env.example .env
docker compose up --build
```

- Frontend: <http://localhost:8080>
- Backend Swagger: <http://localhost:8000/docs>
- Health: <http://localhost:8000/api/v1/health>

### Manual (no Docker)

```bash
# Backend
cd backend
python -m venv .venv && . .venv/Scripts/Activate.ps1
pip install -r requirements.txt -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

## Quality gates

All of these must pass before a pull request is merged:

```bash
# Backend
cd backend
python -m compileall -q app
python -m ruff check app
pytest -q

# Frontend
cd ../frontend
npm run typecheck   # tsc --noEmit
npm run lint        # eslint --max-warnings=0
npm test            # vitest run
npm run build       # tsc -b && vite build
```

CI runs the same gates on every push and pull request — see
[`.github/workflows/ci.yml`](.github/workflows/ci.yml).

## Coding standards

### Backend (Python)

- **Type-hint everything.** Use PEP 604 unions (`X | None`) instead of
  `Optional[X]`.
- **Pydantic v2 schemas** for every request/response body.
- **Repository → service → router** layering. Routers stay thin; business
  logic lives in `app/services/`.
- **Async SQLAlchemy 2.0** only — no legacy `Query` API.
- Sort imports with `ruff` (already configured).
- Add or update **pytest** coverage for every behavioural change.

### Frontend (TypeScript / React)

- **Strict TypeScript**, `any` is allowed only at API boundaries with a
  comment justifying it.
- **React 19 functional components** with hooks. No class components.
- Use the existing UI primitives in `src/components/ui/` (Radix wrappers).
- Use **`@/` path alias** for cross-folder imports.
- State management: **TanStack Query** for server state, **Zustand** for
  client state, **React Hook Form + Zod** for forms.
- i18n: every user-facing string must have a key in **both** `en.json` and
  `bn.json`.
- Add or update **Vitest + React Testing Library** tests for components.

## Commit conventions

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add competitor comparison view
fix: handle empty audience in roadmapToForm
chore(ci): cache pip in GitHub Actions
docs(api): document /api/v1/ai/advise
refactor(frontend): split SettingsPage into tabs
test(backend): cover milestone completion update
```

`feat` and `fix` types trigger a release-please PR.

## Pull request process

1. **Fork & branch.** Branch from `main` as `feat/<short-topic>` or
   `fix/<short-topic>`.
2. **Keep PRs small and focused** — one feature / fix per PR.
3. **Run the gates locally** before pushing.
4. **Write a clear PR description** using the
   [template](.github/PULL_REQUEST_TEMPLATE.md). Include screenshots for
   any UI change.
5. **Link related issues** with `Closes #123` / `Refs #456`.
6. Wait for **at least one approving review** and a green CI run before
   merging.

## Reporting bugs & requesting features

Please use the issue templates:

- [Bug report](.github/ISSUE_TEMPLATE/bug_report.yml)
- [Feature request](.github/ISSUE_TEMPLATE/feature_request.yml)

## Security issues

Please **do not** open a public issue for security problems. Follow the
process in [`SECURITY.md`](SECURITY.md).

## License

By contributing you agree that your contributions will be licensed under the
[MIT License](LICENSE).