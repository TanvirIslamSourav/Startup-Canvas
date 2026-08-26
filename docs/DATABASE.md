# Database — Startup Canvas

> PostgreSQL 16 · SQLAlchemy 2.0 · Alembic

---

## 1. Conventions

- **Naming**: tables in `snake_case` plural (`startup_projects`), columns in `snake_case`, primary keys `id` (UUID v4 by default; optional `BIGSERIAL` for append‑only tables).
- **Time**: every table has `created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()` and `updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()` updated by a generic trigger.
- **Soft delete**: `is_archived BOOLEAN NOT NULL DEFAULT FALSE` + `archived_at TIMESTAMPTZ NULL`. We never hard‑delete user content in v1.
- **Audit**: `created_by` / `updated_by` UUID NULL → FK to `users.id`.
- **Indices**: every FK is indexed; every column used in `ORDER BY` is indexed; composite indexes added per hot query.
- **Money**: stored as `NUMERIC(12, 2)` when needed (e.g. competitor pricing).
- **JSON**: `JSONB` for free‑form metadata (canvas payloads, settings).
- **Enums**: `VARCHAR` with `CHECK` constraints (cheaper than Postgres enums for migrations).

---

## 2. ERD (text)

```
users (1) ──< (N) startup_projects (1) ──< (N) ideas
                                          │
                                          ├──< (1) lean_canvas
                                          ├──< (1) business_canvas
                                          ├──< (1) swot
                                          ├──< (N) competitors
                                          ├──< (N) customer_personas
                                          ├──< (1) roadmap
                                          │       └──< (N) roadmap_stages
                                          ├──< (N) tasks
                                          ├──< (N) milestones
                                          ├──< (1) progress_tracker
                                          ├──< (N) documents
                                          ├──< (N) notes
                                          └──< (N) activities
```

`startup_projects` is the container that groups ideas by stage (Idea → Research → Prototype → MVP → Beta → Launch → Growth → Scale). `ideas` is the actual unit of work.

---

## 3. Tables

> All `VARCHAR` lengths are illustrative. UUIDs are stored as `UUID`.

### 3.1 `users`

| Column         | Type           | Notes                          |
| -------------- | -------------- | ------------------------------ |
| id             | UUID PK        |                                |
| email          | VARCHAR(255)   | UNIQUE, lowercased             |
| display_name   | VARCHAR(120)   |                                |
| locale         | VARCHAR(8)     | `'bn'` or `'en'`               |
| theme          | VARCHAR(16)    | `'light'`/`'dark'`/`'system'`  |
| is_active      | BOOLEAN        | default TRUE                   |
| created_at     | TIMESTAMPTZ    |                                |
| updated_at     | TIMESTAMPTZ    |                                |

### 3.2 `startup_projects`

| Column      | Type           | Notes                                |
| ----------- | -------------- | ------------------------------------ |
| id          | UUID PK        |                                      |
| owner_id    | UUID FK users  |                                      |
| name        | VARCHAR(160)   | NOT NULL                             |
| description | TEXT           |                                      |
| stage       | VARCHAR(32)    | CHECK in stage enum                  |
| status      | VARCHAR(32)    | `'active'`/`'paused'`/`'completed'`  |
| tags        | JSONB          | default `'[]'`                       |
| metadata    | JSONB          | default `'{}'`                       |
| created_at  | TIMESTAMPTZ    |                                      |
| updated_at  | TIMESTAMPTZ    |                                      |

### 3.3 `ideas`

| Column        | Type           | Notes                                          |
| ------------- | -------------- | ---------------------------------------------- |
| id            | UUID PK        |                                                |
| project_id    | UUID FK        |                                                |
| title         | VARCHAR(200)   | NOT NULL                                       |
| problem       | TEXT           |                                                |
| solution      | TEXT           |                                                |
| audience      | TEXT           |                                                |
| category      | VARCHAR(64)    | indexed                                        |
| tags          | JSONB          |                                                |
| status        | VARCHAR(32)    | `'draft'`/`'validating'`/`'planned'`/…         |
| priority      | SMALLINT       | 0–5, default 0                                 |
| score         | SMALLINT       | 0–100, computed in service layer               |
| is_archived   | BOOLEAN        | default FALSE                                  |
| archived_at   | TIMESTAMPTZ    | NULL                                           |
| created_at    | TIMESTAMPTZ    |                                                |
| updated_at    | TIMESTAMPTZ    |                                                |

Index: `(project_id, status)`, `(category)`, GIN on `tags`.

### 3.4 `lean_canvas`

| Column             | Type        |
| ------------------ | ----------- |
| id                 | UUID PK     |
| idea_id            | UUID FK UNIQUE |
| problem            | TEXT        |
| solution           | TEXT        |
| key_metrics        | TEXT        |
| unique_value_prop  | TEXT        |
| unfair_advantage   | TEXT        |
| channels           | TEXT        |
| customer_segments  | TEXT        |
| cost_structure     | TEXT        |
| revenue_streams    | TEXT        |
| created_at         | TIMESTAMPTZ |
| updated_at         | TIMESTAMPTZ |

### 3.5 `business_canvas`

Same shape as Lean but with the 9 BMC blocks:

| Column              | Type        |
| ------------------- | ----------- |
| id                  | UUID PK     |
| idea_id             | UUID FK UNIQUE |
| key_partners        | TEXT        |
| key_activities      | TEXT        |
| key_resources       | TEXT        |
| value_propositions  | TEXT        |
| customer_relationships | TEXT     |
| channels            | TEXT        |
| customer_segments   | TEXT        |
| cost_structure      | TEXT        |
| revenue_streams     | TEXT        |
| created_at          | TIMESTAMPTZ |
| updated_at          | TIMESTAMPTZ |

### 3.6 `swot`

| Column     | Type        |
| ---------- | ----------- |
| id         | UUID PK     |
| idea_id    | UUID FK UNIQUE |
| strengths  | TEXT        |
| weaknesses | TEXT        |
| opportunities | TEXT     |
| threats    | TEXT        |
| score      | SMALLINT    | 0–100, computed
| summary    | TEXT        |
| created_at | TIMESTAMPTZ |
| updated_at | TIMESTAMPTZ |

### 3.7 `competitors`

| Column         | Type           |
| -------------- | -------------- |
| id             | UUID PK        |
| idea_id        | UUID FK        |
| name           | VARCHAR(160)   |
| website_url    | VARCHAR(255)   |
| pricing        | NUMERIC(12,2)  |
| pricing_currency | VARCHAR(8)   | default `'USD'`
| strengths      | TEXT           |
| weaknesses     | TEXT           |
| features       | JSONB          | array of `{ name, has }`
| market_position | VARCHAR(64)   |
| notes          | TEXT           |
| created_at     | TIMESTAMPTZ    |
| updated_at     | TIMESTAMPTZ    |

Index: `(idea_id)`.

### 3.8 `customer_personas`

| Column       | Type           |
| ------------ | -------------- |
| id           | UUID PK        |
| idea_id      | UUID FK        |
| name         | VARCHAR(120)   |
| age          | SMALLINT       |
| occupation   | VARCHAR(120)   |
| goals        | TEXT           |
| pain_points  | TEXT           |
| needs        | TEXT           |
| behaviour    | TEXT           |
| avatar_url   | VARCHAR(512)   |
| created_at   | TIMESTAMPTZ    |
| updated_at   | TIMESTAMPTZ    |

### 3.9 `roadmap`

```
roadmap (1) ──< (N) roadmap_stages
```

`roadmap` holds the idea‑level title; `roadmap_stages` is the ordered list.

| Column      | Type           |
| ----------- | -------------- |
| id          | UUID PK        |
| idea_id     | UUID FK UNIQUE |
| title       | VARCHAR(160)   |
| created_at  | TIMESTAMPTZ    |
| updated_at  | TIMESTAMPTZ    |

`roadmap_stages`:

| Column        | Type           |
| ------------- | -------------- |
| id            | UUID PK        |
| roadmap_id    | UUID FK        |
| name          | VARCHAR(64)    | Idea / Research / Prototype / MVP / Beta / Launch / Growth / Scale
| order_index   | SMALLINT       |
| target_date   | DATE           |
| completed_at  | TIMESTAMPTZ    |
| notes         | TEXT           |
| created_at    | TIMESTAMPTZ    |
| updated_at    | TIMESTAMPTZ    |

Index: `(roadmap_id, order_index)`.

### 3.10 `tasks`

| Column       | Type           |
| ------------ | -------------- |
| id           | UUID PK        |
| idea_id      | UUID FK        |
| title        | VARCHAR(200)   |
| description  | TEXT           |
| priority     | VARCHAR(16)    | `'low'`/`'medium'`/`'high'`/`'urgent'`
| status       | VARCHAR(16)    | `'todo'`/`'in_progress'`/`'blocked'`/`'done'`
| progress     | SMALLINT       | 0–100
| due_date     | DATE           |
| started_at   | TIMESTAMPTZ    |
| completed_at | TIMESTAMPTZ    |
| created_at   | TIMESTAMPTZ    |
| updated_at   | TIMESTAMPTZ    |

Index: `(idea_id, status)`, `(due_date)`.

### 3.11 `milestones`

| Column        | Type           |
| ------------- | -------------- |
| id            | UUID PK        |
| idea_id       | UUID FK        |
| title         | VARCHAR(200)   |
| description   | TEXT           |
| target_date   | DATE           |
| completed_at  | TIMESTAMPTZ    |
| completion    | SMALLINT       | 0–100
| created_at    | TIMESTAMPTZ    |
| updated_at    | TIMESTAMPTZ    |

### 3.12 `progress_tracker`

One row per idea. Server‑computed aggregates cached here for the dashboard.

| Column              | Type        |
| ------------------- | ----------- |
| id                  | UUID PK     |
| idea_id             | UUID FK UNIQUE |
| overall_completion  | SMALLINT    | 0–100
| health_score        | SMALLINT    | 0–100
| milestone_progress  | SMALLINT    | 0–100
| task_completion     | SMALLINT    | 0–100
| last_computed_at    | TIMESTAMPTZ |

### 3.13 `documents`

| Column        | Type           |
| ------------- | -------------- |
| id            | UUID PK        |
| idea_id       | UUID FK        |
| kind          | VARCHAR(32)    | `'business_plan'`/`'pitch_deck'`/`'note'`/`'attachment'`
| title         | VARCHAR(200)   |
| file_path     | VARCHAR(512)   |
| mime_type     | VARCHAR(120)   |
| size_bytes    | BIGINT         |
| notes         | TEXT           |
| created_at    | TIMESTAMPTZ    |
| updated_at    | TIMESTAMPTZ    |

### 3.14 `notes`

| Column     | Type           |
| ---------- | -------------- |
| id         | UUID PK        |
| idea_id    | UUID FK        |
| body       | TEXT           |
| pinned     | BOOLEAN        | default FALSE
| created_at | TIMESTAMPTZ    |
| updated_at | TIMESTAMPTZ    |

### 3.15 `activities`

Append‑only timeline shown on the dashboard.

| Column     | Type           |
| ---------- | -------------- |
| id         | BIGSERIAL PK   |
| idea_id    | UUID FK        |
| actor_id   | UUID FK users  |
| verb       | VARCHAR(32)    | `'created'`/`'updated'`/`'completed'`/…
| subject    | VARCHAR(64)    | `'idea'`/`'task'`/`'milestone'`/…
| summary    | VARCHAR(255)   |
| metadata   | JSONB          |
| created_at | TIMESTAMPTZ    |

Index: `(idea_id, created_at DESC)`.

---

## 4. Migrations

- Tool: **Alembic** (`backend/alembic/`).
- One revision per logical change; never edit a shipped migration.
- Initial migration (`0001_init`) creates all 15 tables + the `updated_at` trigger.
- Subsequent migrations are named `NNNN_short_slug.py`.

The trigger:

```sql
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

applied to every table that has `updated_at`.

---

## 5. Seeding

`backend/app/seeds/run.py` runs idempotently on startup if `ENVIRONMENT=development` and the DB is empty:

1. Insert one default user (`sourav@startup.local` / display `Sourav`).
2. Insert one default `startup_projects` row.
3. Insert one demo `ideas` row with full canvas / SWOT / persona / competitor / roadmap / tasks / milestones.
4. Insert one demo `notes` row.

This makes the app usable on first boot without any manual setup.

---

## 6. Connection & pooling

- Driver: **`psycopg[binary]` 3.x**.
- Pool: SQLAlchemy default `QueuePool`, `pool_size=5`, `max_overflow=10`, `pool_pre_ping=True`.
- `DATABASE_URL` is parsed from env; in tests we swap to SQLite (`sqlite:///:memory:`) via the dependency override in `backend/app/db/session.py`.