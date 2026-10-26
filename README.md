# StructuredDocs 

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)

StructuredDocs is a document management and knowledge-base platform. Users organize content into a **Project → Collection → Topic** hierarchy, edit rich HTML content with TinyMCE or Quill, route topics through a structured review and approval workflow, and publish finished content as PDFs, HTML knowledge bases, or mobile-optimised sites. Word (`.docx`), HTML, and Markdown documents can be imported and automatically parsed into the hierarchy.

## Documentation Hub

For implementation, database, infrastructure, and operations guidance, start with:

- [docs/README.md](docs/README.md)

## Features

- **Hierarchical authoring** – Projects contain nested Collections and Topics with a rich-text editor (TinyMCE 6 / Quill 2)
- **Document import** – Upload `.docx` or Markdown; headings are parsed into the Project → Collection → Topic tree with embedded images preserved
- **Review workflow** – Assign reviewers, generate time-limited token links for external (no-account) reviewers, collect inline feedback, and track approval status through configurable review sequences
- **Publications & export** – Assemble ordered topic snapshots into a Publication and export as PDF (multiple style configs), self-contained HTML, or a mobile knowledge base
- **Variables & snippets** – Reusable content blocks and variable substitution across documents
- **Milestones & tasks** – Lightweight project task tracking
- **Admin** – User management, diagnostics, metrics dashboard

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Vue 3, Vite, Bootstrap 5, TinyMCE 6, Quill 2, Axios |
| Backend | Python 3.11, Flask, SQLAlchemy ORM, Flask-Migrate |
| Database | PostgreSQL (production), SQLite (development) |
| Auth | Flask-JWT-Extended (JWT bearer tokens) |
| Background jobs | Redis + RQ |
| Rate limiting | Flask-Limiter |
| Storage | S3-compatible object storage or local filesystem (images) |
| Email | SMTP |

## Quick Start

### Frontend (Vercel)

- Repo root contains `frontend/` linked to your Vercel project.

- On push to `main`, Vercel builds the frontend with Vite (`npm run build`).

- Set `VITE_API_BASE_URL` (and optionally `VITE_APP_ENV=production`) in Vercel Project Settings → Environment Variables to your backend API URL, e.g. `https://api.yourdomain.com`.

- If using a monorepo, keep `vercel.json` at root to point build to `frontend/`.

### Backend (VPS)

Three supported deployment styles (choose one):

1. VPS + Docker (recommended for current setup)

   - Build & run locally first: `docker compose -f docker-compose.app.yml up --build`.

   - The GitHub Actions `Deploy Production Stack` workflow deploys `main` to `/opt/structureddocs/production`; keep its `.env` on the VPS and configure the GitHub `production` environment approval.
   - Follow the [single-VPS production cutover runbook](docs/single-vps-three-stacks.md) when migrating a live site from the legacy app path.

2. VPS + systemd (no containers)

   - Install Python 3.11, create venv, install `backend/requirements.txt`.

   - Use Gunicorn unit: `/etc/systemd/system/structureddocs.service` pointing to `backend.app:create_app()`.
   - Run Alembic migrations with `scripts/run_migrations.sh` (ensure env loaded).

### Environment Variables

Frontend (Vercel):

- `VITE_API_BASE_URL=https://your-backend-domain`

- `VITE_APP_ENV=production` (optional feature gating)

Backend (VPS):

- `DATABASE_URL=postgresql://user:pass@host:5432/dbname`

- `SECRET_KEY`, `JWT_SECRET_KEY`

- `FRONTEND_URL=https://your-frontend.vercel.app`

- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `MAIL_DEFAULT_SENDER`

- (Optional) `SENTRY_DSN`, `REDIS_URL`, `ENABLE_BLUEPRINTS`
- (Optional, remote image storage) `STORAGE_BUCKET`, `STORAGE_ENDPOINT`, `STORAGE_ACCESS_KEY`, `STORAGE_SECRET_KEY`, `STORAGE_REGION`, `STORAGE_PUBLIC_BASE_URL`

See `backend/.env.example` for a full template.

See `.env.example` and `docs/email-sending.md` for SMTP configuration and DMARC alignment guidance.

### Deployment Workflow Summary

| Layer    | Dev Command                            | Production Path                                                |
|----------|----------------------------------------|----------------------------------------------------------------|
| Frontend | `cd frontend && npm run dev`           | Vercel build + CDN                                             |
| Backend  | `python -m gunicorn "backend.app:create_app()" -b 0.0.0.0:8080` | VPS container or service (Gunicorn) |
| DB       | SQLite (auto-created)                  | Managed or self-hosted Postgres (set `DATABASE_URL`)           |
| Migrations | `cd backend && flask db upgrade`    | Manual or container start (`RUN_DB_MIGRATIONS=1`)              |

For canonical Docker production layering, use:

`docker compose -f docker-compose.base.yml -f docker-compose.prod.yml up -d --build`

### Promote Between Environments

Run **Actions → Promote Environment → Run workflow** from the default branch,
select `source_env` and `target_env`, and leave `force_sync` unchecked for the
recommended review flow. The workflow must be present on the default branch
before it appears in the Actions UI.

Only **dev → staging** and **staging → production** are allowed. Environment
names map to branches `dev`, `staging`, and **`main` for production**, matching
the deployment workflows. Both branches must already exist.

- **Default (PR):** creates a source-to-target pull request for normal review,
  checks, and merge. Reuses an existing open PR; does nothing if there are no
  source commits to promote. Enable **Settings → Actions → General → Workflow
  permissions → Allow GitHub Actions to create and approve pull requests**.
  Repository/organization policies may restrict this setting.
- **Force sync (destructive):** rewrites the target branch to the captured source
  commit, discarding target-only commits from its history, including any
  branch-specific configuration. Back up the target SHA first; the old and new
  SHAs are logged. An explicit `--force-with-lease` rejects the push if the target
  changes after it is fetched. A moving source requires another run to capture
  its latest tip. Branch protection/rulesets can block force pushes; the workflow
  fails rather than bypassing protections. Prefer a PR instead of relaxing them.
- Promotions to the same target are serialized, but other writers can still
  update branches. The workflow uses only `GITHUB_TOKEN`: PR mode grants
  contents read / pull requests write; force mode grants contents write.
- Events created with `GITHUB_TOKEN` do **not** trigger other Actions workflows.
  For a bot-created PR, arrange required checks through your repository's
  approved process. After force sync, manually run the matching deployment
  workflow on the updated target (`staging` or `main`); promotion alone does not
  deploy the app or change environment secrets.

### Local Development (without Docker)

```bash
# Backend
cd /path/to/repo
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
cp .env.example .env          # fill in values
python -m gunicorn "backend.app:create_app()" -b 0.0.0.0:8080

# Frontend (separate terminal)
cd frontend
npm install
npm run dev                   # Vite dev server on :5173, proxies /api → :8080

# Run tests
python -m pytest test_hierarchical_parsing_logic.py   # unit tests (no server needed)
python -m pytest test_integration.py                  # integration tests (requires backend on :5050)
```

### Legacy

- PythonAnywhere was a previous hosting target. Residual helper scripts (`pa_*.sh`, `deploy_pythonanywhere.sh`, etc.) remain in `scripts/` for reference but are not part of the current deployment workflow.

## Operational Enhancements (Infrastructure Overview)

### Version & Build Metadata

`/api/version` returns JSON:

```json

{
  "service": "StructuredDocs",
  "version": "0.2.0",
  "commit": "abc1234",
  "build_time": "2025-09-27T12:34:56Z"
}

```

Values come from build args (`APP_VERSION`, `GIT_COMMIT`, `BUILD_TIME`) set in CI or fall back to git at runtime.

### Database Connection Pooling

```env

DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_RECYCLE=1800
DB_POOL_TIMEOUT=30

```

Applied via `SQLALCHEMY_ENGINE_OPTIONS` (ignored for SQLite).

### Rate Limiting (Flask-Limiter)

```env

RATE_LIMIT_DEFAULT=200 per day;50 per hour
RATE_LIMIT_LOGIN=5 per minute
RATE_LIMIT_AUTH=30 per hour
RATE_LIMIT_WRITE=100 per hour
RATE_LIMIT_STORAGE_URI=redis://localhost:6379/1

```

Defaults override limiter internal defaults; per-endpoint limits applied best-effort.

### Security Headers

```env

ENABLE_SECURITY_HEADERS=1
CSP_HEADER="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src *; font-src 'self' data:; frame-ancestors 'none'; object-src 'none'"
PERMISSIONS_POLICY="geolocation=(), microphone=(), camera=()"

```

Disable by setting `ENABLE_SECURITY_HEADERS=0`.

### Background Jobs (Redis + RQ)

Provide `REDIS_URL`. Worker entrypoint:

```bash

python -m backend.worker

```

Enqueue programmatically:

```python

from backend.utils.tasks import enqueue_task
enqueue_task('backend.tasks.examples.example_long_task', duration=10)

```

HTTP example:

```bash

curl -X POST -H 'Content-Type: application/json' \
   -d '{"duration":3}' http://localhost:8080/api/tasks/enqueue-example

```

### Build Metadata Injection

Docker build args -> environment -> `/api/version`.

### Frontend Version Footer

`VersionFooter.vue` surfaces build info in UI footer.

### Removed Font Awesome

Replaced with Bootstrap Icons, inline SVG, or Unicode to reduce bundle size.

### Sentry (Optional)

Set `SENTRY_DSN` to enable error and trace capture (sample rate 0.1).

### Adding New Tasks

Add task function under `backend/tasks/` then enqueue via dotted path.

### Structured Logging (Optional)

Set `LOG_FORMAT=json` to emit structured JSON logs with `event`, `ts`, and a short request id propagated via `X-Request-ID` header.

### Local Run Cheat Sheet

```bash

# Backend (with Docker compose)

docker compose -f docker-compose.app.yml up --build

# Run worker (requires REDIS_URL)

python -m backend.worker

# Enqueue example task

python -c "from backend.utils.tasks import enqueue_task; print(enqueue_task('backend.tasks.examples.example_long_task', duration=3))"

```

### Future Hardening Ideas

- Structured JSON logging w/ request IDs

- Metrics exporter (Prometheus or OTLP)

- Nonce / hashed CSP

- Scheduled tasks (cron + RQ)

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to open issues and submit pull requests.

## License

This project is licensed under the [MIT License](LICENSE).
