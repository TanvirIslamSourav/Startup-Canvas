# Architecture — Startup Canvas

> ব্যবস্থাপনা নকশা — স্টার্টআপ ক্যানভাস

This document is the **single source of truth** for how the system is organized. Every later document links back here.

---

## 1. Goals & non‑goals

**Goals**

- Single‑user workspace for capturing and validating startup ideas locally.
- 17 product modules, each a full vertical slice (model ↔ schema ↔ repo ↔ service ↔ router ↔ UI ↔ tests).
- Bilingual UI (বাংলা / English) with persisted language.
- Light / Dark / System theme with persisted preference.
- Accessibility target: **WCAG 2.1 AA**.
- AI‑ready: a `StartupAdvisorProvider` interface with a working `MockStartupAdvisorProvider` that reads local JSON. Other providers can be swapped in without touching business logic.
- Fully Dockerized; one command brings the whole stack up.
- Strict typing end‑to‑end (TypeScript + Pydantic + mypy).

**Non‑goals**

- Multi‑tenant auth, billing, or RBAC. (Single user. A future `users` table exists for forward‑compatibility, but no auth flow is wired in v1.)
- Real‑time collaboration. (Not in scope.)
- External API integration. (Forbidden by spec.)

---

## 2. AI‑Driven Development Life Cycle (ADLC)

We execute phases in order. Each phase ends with **all** quality gates green before the next phase starts.

| #  | Phase                          | Output                                           | Gate                                                |
| -- | ------------------------------ | ------------------------------------------------ | --------------------------------------------------- |
| 0  | Scaffold                       | Repo skeleton, Dockerfiles, env, README          | `docker compose config` parses                      |
| 1  | Idea discovery                 | Vision, users, goals, stories (this doc)         | Reviewer sign‑off                                   |
| 2  | Market research                | Competitor matrix, feature gaps                  | Filed in `docs/MARKET.md`                           |
| 3  | Requirements engineering       | FR / NFR / user flows / success criteria         | Filed in `docs/REQUIREMENTS.md`                     |
| 4  | UX research & design           | IA, wireframes, design tokens                    | Filed in `docs/UX.md`                               |
| 5  | System architecture            | Folder structure, DB schema, API contracts       | **This document set**                               |
| 6  | Backend development            | FastAPI app, models, services, routers, tests    | `pytest`, `ruff`, `python -m compileall`            |
| 7  | Frontend development           | Vite app, pages, components, providers, i18n     | `tsc --noEmit`, `vitest`, `npm run build`           |
| 8  | Integration                    | Frontend ↔ backend wiring, error/loading/empty    | Manual smoke + integration tests                    |
| 9  | Quality assurance              | Pytest, Vitest, ESLint, TypeScript check, lint   | All gates green                                     |
| 10 | Dockerization                  | Compose, nginx, env                              | `docker compose config` + image builds              |
| 11 | Documentation                  | README, API.md, deployment.md                    | Docs reviewed                                       |
| 12 | Production readiness           | Perf, a11y audit, security review, responsive    | Lighthouse ≥ 90, axe 0 critical                     |

Phase 0 and Phase 5 are the only phases shipped so far. The rest execute one at a time.

---

## 3. High‑level architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                              Browser                                │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  React 19 + Vite + TS + Tailwind + shadcn/ui + RHF + Zod    │  │
│  │  TanStack Query (server state) · Zustand (UI state)          │  │
│  │  react-i18next (bn/en) · next-themes (light/dark/system)     │  │
│  └──────────────────────────────────────────────────────────────┘  │
└──────────────────────────────┬──────────────────────────────────────┘
                               │  HTTPS · /api/v1/*
                               ▼
┌────────────────────────────────────────────────────────────────────┐
│                        FastAPI (uvicorn)                            │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Routers → Services → Repositories → SQLAlchemy 2.0 ORM      │  │
│  │  Pydantic v2 schemas · JWT-ready auth stub · CORS middleware │  │
│  └──────────────────────────────────────────────────────────────┘  │
│   │                              │                                  │
│   │ StartupAdvisorProvider       │ Local JSON                       │
│   ▼                              ▼                                  │
│  MockStartupAdvisorProvider   backend/data/ai/                     │
└──────────────────────────────┬──────────────────────────────────────┘
                               │  SQL · psycopg 3
                               ▼
┌────────────────────────────────────────────────────────────────────┐
│                       PostgreSQL 16                                 │
│  13 tables · Alembic migrations · seed scripts                      │
└────────────────────────────────────────────────────────────────────┘
```

**Single‑process, single‑user, local‑first.** This is intentional: it keeps the design clean and lets every module be a vertical slice.

---

## 4. Repository layout

See [`FOLDER_STRUCTURE.md`](FOLDER_STRUCTURE.md) for the full annotated tree. Summary:

```
.
├── frontend/   # React 19 + Vite + TypeScript
├── backend/    # FastAPI + SQLAlchemy + Alembic
├── database/   # SQL snapshots / fixtures
├── docker/     # Dockerfiles, nginx.conf
├── docs/       # Architecture, API, deployment, etc.
└── assets/     # Static brand assets
```

---

## 5. Module map

Every product module is a **vertical slice** with: SQLAlchemy model → Pydantic schemas → repository → service → router → frontend page + dialog(s) + tests.

| Module                | Backend router             | Frontend route                       | AI advisor capability                |
| --------------------- | -------------------------- | ------------------------------------ | ------------------------------------ |
| Landing               | (static)                   | `/`                                  | —                                    |
| Dashboard             | `/dashboard/summary`       | `/dashboard`                         | —                                    |
| Idea Manager          | `/ideas`                   | `/ideas`                             | validation hints                     |
| Lean Canvas           | `/lean-canvas`             | `/ideas/:id/lean-canvas`             | section suggestions                  |
| Business Model Canvas | `/business-canvas`         | `/ideas/:id/business-canvas`         | section suggestions                  |
| SWOT                  | `/swot`                    | `/ideas/:id/swot`                    | SWOT suggestions                     |
| Competitor Analysis   | `/competitors`             | `/ideas/:id/competitors`             | competitor recommendations           |
| Customer Persona      | `/personas`                | `/ideas/:id/personas`                | persona enrichment                   |
| Roadmap               | `/roadmap`                 | `/ideas/:id/roadmap`                 | growth roadmap                       |
| Task Manager          | `/tasks`                   | `/ideas/:id/tasks`                   | next‑step suggestions                |
| Milestones            | `/milestones`              | `/ideas/:id/milestones`              | milestone breakdown                  |
| Progress Tracker      | `/progress`                | `/ideas/:id/progress`                | startup health commentary            |
| Documents             | `/documents`               | `/ideas/:id/documents`               | outline suggestions                  |
| Notes                 | `/notes`                   | `/ideas/:id/notes`                   | —                                    |
| Analytics             | `/analytics`               | `/analytics`                         | —                                    |
| Settings              | `/settings`                | `/settings`                          | —                                    |
| About                 | (static)                   | `/about`                             | —                                    |

---

## 6. Cross‑cutting concerns

- **Validation** — Pydantic v2 on the wire, Zod on the form. Both schemas are derived from a shared shape (see `docs/API.md` §"Schema mirroring").
- **Errors** — Backend raises `HTTPException` with a stable JSON shape; frontend has a single `apiErrorHandler` that maps to a toast and surfaces a retry where appropriate.
- **Logging** — Structured JSON logs (`loguru` on backend, `pino`-shaped logger on frontend).
- **Observability** — `/health` (liveness), `/ready` (DB‑aware), request id middleware.
- **Security** — CORS allowlist, secret‑key rotation via env, no secrets in repo. SQL‑injection‑proof via ORM. XSS‑proof via React + Tailwind.
- **Performance** — Pagination (default 20, max 100), index hints per module, eager loading where N+1 is a risk.
- **i18n** — All user‑visible strings go through `t('key')`. Translation files live in `frontend/src/i18n/locales/{bn,en}.json`.
- **Theming** — CSS variables in `frontend/src/theme/tokens.css`; theme provider toggles the `dark` class on `<html>`.
- **Accessibility** — Focus rings, skip‑link, semantic landmarks, keyboard‑navigable dialogs, `aria-live` for toasts, reduced‑motion honored via Framer Motion's `MotionConfig`.

---

## 7. State management

See [`STATE.md`](STATE.md) for the server/client split decision matrix.

- **Server state** lives on PostgreSQL and is exposed via TanStack Query (`useQuery` / `useMutation`). Cache keys are namespaced per module (`['ideas', filters]`).
- **UI state** (open dialogs, selected rows, theme/language) lives in Zustand stores.
- **Form state** lives in React Hook Form.
- **Persisted prefs** (theme, language) live in `localStorage` under `startup-canvas:*` keys.

---

## 8. AI advisor architecture

See [`AI_PROVIDER.md`](AI_PROVIDER.md) for the full design.

```
backend/app/ai/
├── __init__.py
├── provider.py            # StartupAdvisorProvider Protocol + DI helper
├── mock.py                # MockStartupAdvisorProvider (reads local JSON)
├── openai.py              # stub class raising NotConfiguredError
├── gemini.py              # stub class raising NotConfiguredError
├── claude.py              # stub class raising NotConfiguredError
├── groq.py                # stub class raising NotConfiguredError
└── ollama.py              # stub class raising NotConfiguredError
```

Routers depend only on `StartupAdvisorProvider`. Swapping providers is a single env‑var change (`STARTUP_ADVISOR_PROVIDER=mock|openai|...`).

---

## 9. Build, test, ship

- Local dev: `make dev` (Docker) or `make backend` + `make frontend`.
- CI (later): same quality gates as `make test lint build`.
- Release: tag → `docker compose -f docker-compose.prod.yml up -d` (to be added in Phase 12).

---

## 10. Open decisions

- **Auth**: deferred. The `users` table exists with a default seeded user so single‑user mode works out of the box. Adding real auth is a Phase 12 task.
- **File storage**: documents use a local filesystem path under `backend/data/uploads/`. S3‑compatible adapters are a Phase 12 stretch goal.
- **Search**: v1 uses `ILIKE` on indexed text columns. Full‑text search (Postgres `tsvector`) is a Phase 12 optimization.

---

## 11. Glossary

- **Canvas** — a structured planning artifact (Lean, BMC, SWOT, …).
- **Idea** — the top‑level entity. Every other module hangs off an idea via `idea_id`.
- **Slice** — the full vertical (DB → API → UI) for one feature.
- **Provider** — a swappable backend strategy, used today only by the AI advisor.