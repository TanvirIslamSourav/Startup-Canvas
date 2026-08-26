# Deployment Guide

> Production deployment of Startup Canvas via Docker Compose.

---

## 1. Prerequisites

- Linux server (Ubuntu 22.04+ recommended) with Docker 24+ and Compose v2.
- A registered domain pointing at the server (optional but recommended).
- Reverse proxy (Caddy or nginx) for TLS termination (covered below with Caddy).

## 2. Environment

Copy `.env.example` to `.env` on the server and set:

```ini
ENVIRONMENT=production
SECRET_KEY=<openssl rand -hex 32>
POSTGRES_PASSWORD=<strong password>
CORS_ORIGINS=https://your-domain.tld
```

## 3. Production compose

The provided `docker-compose.yml` is suitable for local dev. For production, add:

- `restart: always` (already set)
- A reverse proxy with TLS (Caddy example below)
- Postgres backup (cron job running `pg_dump`)

### Caddy example

```caddyfile
your-domain.tld {
    encode zstd gzip
    reverse_proxy startup-canvas-frontend:80
    reverse_proxy /api/* startup-canvas-backend:8000
}
```

## 4. Migrations

On every deploy:

```bash
docker compose run --rm backend alembic upgrade head
```

This is idempotent and safe to run on every release.

## 5. Backups

Daily `pg_dump` to object storage:

```bash
docker exec startup-canvas-postgres pg_dump -U startup startup_canvas \
  | gzip > /backups/startup-canvas-$(date +%F).sql.gz
```

## 6. Logs

```bash
docker compose logs -f --tail=100
```

Structured JSON logs are emitted by the backend; pipe to your aggregator of choice.

## 7. Updating

```bash
git pull
docker compose pull
docker compose up -d --build
docker compose run --rm backend alembic upgrade head
```

## 8. Health checks

- Liveness: `GET /api/v1/health` → `{ "status": "ok" }`
- Readiness: `GET /api/v1/ready` → checks DB

Both are wired into Docker `HEALTHCHECK` for self‑healing restarts.