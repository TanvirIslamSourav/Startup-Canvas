# Folder Structure

> Annotated tree of the Startup Canvas repository at Phase 0/5 baseline.

```
.
├── .editorconfig                 # Editor defaults (LF, 2 spaces, UTF‑8)
├── .env.example                  # Template for local environment
├── .gitignore                    # OS / IDE / build / secret ignores
├── Makefile                      # `make dev`, `make test`, `make lint`, …
├── README.md                     # Project landing page
├── docker-compose.yml            # Postgres + backend + frontend stack
│
├── docker/                       # Container build assets
│   ├── backend.Dockerfile        # FastAPI image (multi‑stage)
│   ├── frontend.Dockerfile       # Vite + nginx image (multi‑stage)
│   └── nginx.conf                # SPA fallback + /api proxy
│
├── docs/                         # Documentation (markdown)
│   ├── ARCHITECTURE.md           # Single source of truth
│   ├── DATABASE.md               # Schema + ERD + migrations
│   ├── API.md                    # REST reference
│   ├── FRONTEND.md               # Routing, providers, state
│   ├── STATE.md                  # Server vs client state matrix
│   ├── I18N.md                   # Translation workflow
│   ├── AI_PROVIDER.md            # Swappable advisor provider
│   ├── ACCESSIBILITY.md          # WCAG AA checklist
│   ├── DEPLOYMENT.md             # Production deploy guide
│   ├── DEVELOPMENT.md            # Local dev guide
│   └── FOLDER_STRUCTURE.md       # This file
│
├── assets/                       # Brand assets (logos, illustrations)
│
├── database/                     # Optional SQL snapshots / fixtures
│
├── backend/                      # FastAPI service
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py               # create_app(), CORS, routers, health
│   │   ├── core/                 # config.py, logging.py, security.py, exceptions.py
│   │   ├── db/                   # session.py, base.py
│   │   ├── models/               # *_model.py (one per module)
│   │   ├── schemas/              # *_schema.py (Pydantic v2)
│   │   ├── crud/                 # repository functions
│   │   ├── services/             # business logic
│   │   ├── routers/              # FastAPI APIRouters
│   │   ├── ai/                   # provider interface + mock
│   │   ├── seeds/                # demo data script
│   │   └── utils/                # pagination, slugify, etc.
│   ├── alembic/                  # migrations (env.py, versions/)
│   ├── tests/                    # pytest
│   ├── data/                     # local JSON + uploads (gitignored)
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── pyproject.toml
│   └── alembic.ini
│
└── frontend/                     # React 19 + Vite app
    ├── public/                   # static assets served at root
    ├── src/
    │   ├── main.tsx              # entry, mounts providers + router
    │   ├── App.tsx               # router definition
    │   ├── components/
    │   │   ├── ui/               # shadcn primitives (Button, Card, …)
    │   │   ├── layout/           # AppShell, Sidebar, TopBar, PageHeader
    │   │   └── common/           # DataTable, EmptyState, ConfirmDialog
    │   ├── pages/                # thin route components
    │   ├── layouts/              # AppLayout, AuthLayout
    │   ├── hooks/                # useDebounce, useMediaQuery, …
    │   ├── services/             # http client (axios/fetch)
    │   ├── store/                # zustand slices
    │   ├── utils/                # cn, formatters
    │   ├── types/                # api.ts mirrors
    │   ├── theme/                # tokens.css, theme.ts
    │   ├── providers/            # QueryProvider, ThemeProvider, …
    │   ├── i18n/                 # locales + index.ts
    │   ├── features/             # vertical slices (one folder per module)
    │   └── __tests__/            # vitest
    ├── index.html
    ├── package.json
    ├── tsconfig.json
    ├── vite.config.ts
    ├── tailwind.config.ts
    ├── postcss.config.js
    └── vitest.config.ts
```

---

## What goes where — quick rules

| You are adding…              | Put it in…                                              |
| ---------------------------- | ------------------------------------------------------- |
| A new database table         | `backend/app/models/` + Alembic revision                |
| A new REST endpoint          | `backend/app/routers/` + `crud/` + `services/`          |
| A new UI primitive (no logic) | `frontend/src/components/ui/`                          |
| A new product feature        | `frontend/src/features/<module>/`                       |
| A new page (route)           | `frontend/src/pages/` (thin) → renders `features/<m>/`  |
| Shared types                  | `frontend/src/types/`                                   |
| Translation key               | `frontend/src/i18n/locales/{bn,en}.json`                |
| AI seed data                  | `backend/data/ai/<capability>.json`                     |
| Documentation                 | `docs/<topic>.md`                                       |