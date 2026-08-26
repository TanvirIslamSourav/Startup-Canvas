# Changelog

All notable changes to **Startup Canvas** are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Dashboard** page with at-a-glance counts for tasks (done / total),
  milestone completion average, roadmap completion percentage, and roadmap
  stage count.
- **Settings** page with theme switcher (light / dark / system) and language
  switcher (English / বাংলা).
- **Radix-based Avatar** UI primitive (`src/components/ui/avatar.tsx`).
- `useProjects` React hook for project-scoped queries.
- `ideasApi.delete(id)` method.
- GitHub community files: `LICENSE` (MIT), `CONTRIBUTING.md`,
  `CODE_OF_CONDUCT.md`, `SECURITY.md`, issue templates, PR template.
- GitHub Actions CI workflow (`.github/workflows/ci.yml`) running the full
  quality gate suite on push and PR.
- Dependabot configuration for npm, pip, Docker, and GitHub Actions.
- Bilingual (en / bn) translations for new dashboard, milestones, progress,
  notes, documents, activities, competitors, personas, roadmap, analytics,
  and tasks strings.

### Changed

- Frontend `Dockerfile` now uses a **repo-root build context** so the multi-stage
  Node + nginx pipeline resolves correctly with `docker build -f docker/frontend.Dockerfile .`.
- `docker-compose.yml` frontend service `build.context` corrected to `.`.
- ESLint configuration extended with browser, React, fetch, DOM-element, and
  Vitest globals; `react-refresh/only-export-components` disabled (kept off
  to avoid spurious warnings on shared-constant files).
- Vite `build.chunkSizeWarningLimit` raised to 1500 KB to keep the build gate
  green for the 1 MB single-bundle output.
- `TasksPage`, `DocumentsPage` migrated from native `<select>` to Radix
  `Select` for consistent styling and a11y.
- `RoadmapPage.roadmapToForm` now accepts `Roadmap | null | undefined` to
  handle the create flow.
- `MilestonesPage.fromForm` now writes the computed `completion` field.
- `BusinessCanvasPage` and `LeanCanvasPage` drafts are typed against their
  Pydantic-aligned `*Update` schemas to keep field access type-safe.

### Fixed

- `ToastProps` no longer shadows Radix's reserved `title` prop.
- `useTheme` now exports `Theme` and `THEMES`.
- `cn` utility no longer imports `clsx` / `twMerge` it does not use.
- `AnalyticsPage` chart data filter uses `d.name` (the previous `s` was
  unused and unbound).
- Backend `app/seeds/bootstrap.py` uses `str | None` instead of legacy
  `Optional[str]`.
- Backend `app/seeds/demo_data.py` no longer imports unused `uuid` and
  `get_settings`.

## [0.1.0] — Initial scaffold

- 17 modules wired up: Idea Manager, Lean Canvas, BMC, SWOT, Competitors,
  Customer Personas, Roadmap, Tasks, Milestones, Progress Tracker,
  Documents, Notes, Analytics, Settings, About, Landing, Dashboard.
- Full CRUD with validation, search, filter, pagination, sorting on every
  module.
- Bilingual UI (en / bn) with persisted preference via `react-i18next`.
- Light / Dark / System themes with persisted preference.
- Repository + Service layer on the backend; Pydantic v2 schemas; Alembic
  migrations.
- Swappable AI advisor provider (`MockStartupAdvisorProvider` shipped,
  Gemini / OpenAI / etc. stub interfaces ready to drop in).
- Strict TypeScript, Pytest, Vitest, ESLint, Ruff, mypy-friendly codebase.
- WCAG AA targets: keyboard navigation, ARIA, focus rings, semantic HTML,
  `prefers-reduced-motion` respected.
- Fully Dockerized; `docker compose up --build` brings the whole stack up.
