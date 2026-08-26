# Startup Canvas / স্টার্টআপ ক্যানভাস

> **বাংলা:** আপনার স্টার্টআপ আইডিয়াকে পরিকল্পনা থেকে বাস্তবে নিয়ে যান।
> **English:** Turn your startup ideas into successful products.

[![CI](https://img.shields.io/github/actions/workflow/status/<owner>/startup-canvas/ci.yml?branch=main&logo=githubactions&label=CI)](.github/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![React 19](https://img.shields.io/badge/React-19-149eca?logo=react)](frontend/package.json)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](backend/requirements.txt)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-strict-3178c6?logo=typescript)](frontend/tsconfig.json)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ed?logo=docker)](docker-compose.yml)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

A full‑stack, production‑ready workspace for validating, planning, and tracking startup ideas. Built with **React 19 + TypeScript + Vite** on the frontend and **FastAPI + PostgreSQL + SQLAlchemy 2.0** on the backend, fully Dockerized, bilingual (Bangla/English), and architected so a local AI advisor can be swapped in later without touching business logic.

---

## Table of Contents

- [Highlights](#highlights)
- [Tech Stack](#tech-stack)
- [Repository Structure](#repository-structure)
- [Quick Start](#quick-start)
- [Development Workflow](#development-workflow)
- [Quality Gates](#quality-gates)
- [Documentation](#documentation)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [Releasing](#releasing)
- [License](#license)

---

## Highlights

- 17 core modules (Idea Manager, Lean Canvas, Business Model Canvas, SWOT, Competitor Analysis, Customer Persona, Roadmap, Task Manager, Milestones, Progress Tracker, Documents, Notes, Analytics, Settings, About, Landing Page, Dashboard).
- Full CRUD with **validation, search, filter, pagination, sorting** on every module.
- Bilingual UI (বাংলা / English) with persisted preference via `react-i18next`.
- Light / Dark / System themes with persisted preference.
- Repository + Service layer on the backend, clean separation of concerns.
- Swappable **AI advisor provider** (`MockStartupAdvisorProvider` is implemented; `GeminiProvider`, `OpenAIProvider`, etc. are stub interfaces ready to drop in).
- Strict TypeScript, Pydantic v2 schemas, Alembic migrations, repositories tested with Pytest, components tested with Vitest.
- WCAG AA targets: keyboard navigation, ARIA, focus rings, semantic HTML, `prefers-reduced-motion` respected.
- Fully Dockerized with `docker compose up` for one‑command local startup.

---

## Tech Stack

| Layer    | Technologies                                                                                  |
| -------- | --------------------------------------------------------------------------------------------- |
| Frontend | React 19, TypeScript, Vite, Tailwind CSS, shadcn/ui, React Router, TanStack Query, Zustand, React Hook Form, Zod, Framer Motion, Recharts, Lucide Icons, react-i18next |
| Backend  | FastAPI, Python 3.12, PostgreSQL 16, SQLAlchemy 2.0, Alembic, Pydantic v2, Uvicorn          |
| Tests    | Pytest, HTTPX, Vitest, React Testing Library, ESLint, ruff, mypy                              |
| Deploy   | Docker, Docker Compose, nginx                                                                 |

**No external APIs.** No OpenAI / Gemini / Claude / Groq / Ollama / Firebase / Supabase / MongoDB. Everything is local.

---

## Repository Structure

```
.
├── frontend/          # React 19 + Vite + TypeScript application
├── backend/           # FastAPI + SQLAlchemy + Alembic application
├── database/          # Optional SQL snapshots / fixtures
├── docker/            # Dockerfiles for backend and frontend
├── docs/              # Architecture, API, deployment, development guides
├── assets/            # Static design assets (logos, illustrations)
├── docker-compose.yml # One-command local stack
├── .env.example       # Copy to .env and adjust
└── README.md
```

See [`docs/FOLDER_STRUCTURE.md`](docs/FOLDER_STRUCTURE.md) for the full annotated layout.

---

## Quick Start

### Prerequisites

- **Node.js** ≥ 20
- **Python** ≥ 3.11
- **Docker Desktop** (recommended) **or** a local PostgreSQL 16 instance
- **Git**

### Option A — Docker (recommended)

```bash
# 1. clone & enter
git clone <your-fork-url> startup-canvas
cd startup-canvas

# 2. configure
cp .env.example .env

# 3. run
docker compose up --build
```

Then open:

- Frontend: <http://localhost:8080>
- Backend Swagger: <http://localhost:8000/docs>
- Health: <http://localhost:8000/api/v1/health>

### Option B — Local (no Docker)

```bash
# Backend
cd backend
python -m venv .venv
. .venv/Scripts/activate    # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Frontend runs at <http://localhost:5173>.

---

## Development Workflow

This project follows an **AI‑Driven Development Life Cycle** (12 phases), tracked in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) and executed one phase at a time. Each phase ends with:

- ✓ Backend build (`python -m compileall app`)
- ✓ Frontend build (`npm run build`)
- ✓ TypeScript (`tsc --noEmit`)
- ✓ Pytest (`pytest`)
- ✓ Vitest (`npm run test`)
- ✓ Docker (`docker compose config`)

No TODO comments, no placeholder code, no skipped tests.

---

## Quality Gates

| Gate                  | Command (from repo root)          |
| --------------------- | --------------------------------- |
| Backend syntax        | `python -m compileall backend/app`|
| Backend tests        | `cd backend && pytest`            |
| Backend lint          | `cd backend && ruff check app`    |
| Frontend typecheck    | `cd frontend && npx tsc --noEmit` |
| Frontend lint         | `cd frontend && npm run lint`     |
| Frontend tests        | `cd frontend && npm run test`     |
| Frontend build        | `cd frontend && npm run build`    |
| Docker compose config | `docker compose config`           |

---

## Documentation

| Doc                                                    | Purpose                                          |
| ------------------------------------------------------ | ------------------------------------------------ |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)         | System architecture, folder layout, ADLC phases  |
| [`docs/DATABASE.md`](docs/DATABASE.md)                 | PostgreSQL schema, ERD, indexes, migrations      |
| [`docs/API.md`](docs/API.md)                           | REST API reference (auto‑mirrored from Swagger)  |
| [`docs/FRONTEND.md`](docs/FRONTEND.md)                 | Component tree, state shape, routing, theming    |
| [`docs/STATE.md`](docs/STATE.md)                       | Server state vs. client state decision matrix    |
| [`docs/I18N.md`](docs/I18N.md)                         | Translation workflow                             |
| [`docs/AI_PROVIDER.md`](docs/AI_PROVIDER.md)           | How to swap `MockStartupAdvisorProvider`         |
| [`docs/ACCESSIBILITY.md`](docs/ACCESSIBILITY.md)       | WCAG AA checklist                                |
| [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md)             | Production deployment guide                      |
| [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md)           | Local dev setup, debugging, scripts              |
| [`docs/FOLDER_STRUCTURE.md`](docs/FOLDER_STRUCTURE.md) | Annotated folder tree                            |

---

## Roadmap

- ✅ Phase 0 — Scaffold
- ✅ Phase 5 — Architecture & folder skeleton
- 🚧 Phase 6 — Backend skeleton (FastAPI + SQLAlchemy + Alembic)
- 🚧 Phase 7 — Frontend skeleton (Vite + TS + Tailwind + shadcn/providers)
- 🚧 Phase 10 — Dockerization
- 🚧 Phase 11 — Documentation
- ⏳ Phase 12 — Production readiness audit
- ⏳ Remaining modules (Lean Canvas, BMC, SWOT, …) shipped one per sprint

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full ADLC board.

---

## Contributing

We welcome issues and pull requests!

- Read [`CONTRIBUTING.md`](CONTRIBUTING.md) for the workflow, coding
  standards, and quality gates.
- Please follow our [Code of Conduct](CODE_OF_CONDUCT.md).
- Report security issues per [`SECURITY.md`](SECURITY.md) — **do not** open a
  public issue for them.
- Use the issue templates under [`.github/ISSUE_TEMPLATE/`](.github/ISSUE_TEMPLATE/).

The first command maintainers will ask you to run is:

```bash
cd backend && ruff check app && pytest -q
cd ../frontend && npm run typecheck && npm run lint && npm test && npm run build
```

If all of those pass locally, the CI on your PR will too.

---

## Releasing

Releases are cut from `main` with [release-please](https://github.com/googleapis/release-please)
(recommended). Each merge of a Conventional Commit triggers a release-please PR
that bumps the version and updates the changelog. Merging that PR creates a
GitHub release and a tag; the Docker images are then published from
[`docker-compose.yml`](docker-compose.yml).

If you cut a release by hand:

```bash
git tag -s vX.Y.Z -m "vX.Y.Z"
git push origin vX.Y.Z
gh release create vX.Y.Z --generate-notes
```

---

## License

[MIT](LICENSE) © 2026 Startup Canvas contributors.
