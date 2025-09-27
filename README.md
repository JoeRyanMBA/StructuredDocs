# StructuredDocs

## Quick Start

### Frontend (Vercel)

- Repo root contains `frontend/` linked to your Vercel project.
- On push to `main`, Vercel builds the frontend with Vite (`npm run build`).
- Set `VITE_API_BASE_URL` (and optionally `VITE_APP_ENV=production`) in Vercel Project Settings → Environment Variables to your DigitalOcean backend URL, e.g. `https://api.yourdomain.com`.
- If using a monorepo, keep `vercel.json` at root to point build to `frontend/`.

### Backend (DigitalOcean)

Three supported deployment styles (choose one):

1. Droplet + Docker (recommended for current setup)
   - Build & run locally first: `docker compose -f docker-compose.app.yml up --build`.
   - Use `scripts/deploy_digitalocean.sh` (updates image via SSH & restarts container).
   - Provide a `backend.env` file on the server (never commit) with real secrets.

2. Droplet + systemd (no containers)
   - Install Python 3.12, create venv, install `backend/requirements.txt`.
   - Use Gunicorn unit: `/etc/systemd/system/structureddocs.service` pointing to `backend.app:create_app()`.
   - Run Alembic migrations with `scripts/run_migrations.sh` (ensure env loaded).

3. DigitalOcean App Platform
   - Point to repo, set build command (multi-stage Dockerfile already present) or supply this Gunicorn start: `gunicorn backend.app:create_app() -b 0.0.0.0:$PORT`.
   - Add environment variables in App Platform UI.

### Environment Variables

Frontend (Vercel):

- `VITE_API_BASE_URL=https://your-backend-domain`
- `VITE_APP_ENV=production` (optional feature gating)

Backend (DigitalOcean):

- `DATABASE_URL=postgresql://user:pass@host:5432/dbname` (Managed DB connection string)
- `SECRET_KEY`, `JWT_SECRET_KEY`
- `FRONTEND_URL=https://your-frontend.vercel.app`
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `MAIL_DEFAULT_SENDER`
- (Optional) `SENTRY_DSN`, `REDIS_URL`, `ENABLE_BLUEPRINTS`

See `backend/.env.example` for a full template.

See `.env.example` and `EMAIL_SENDING_README.md` for email provider configuration and DMARC alignment guidance.

### Deployment Workflow Summary

| Layer    | Dev Command                            | Production Path                                                |
|----------|----------------------------------------|----------------------------------------------------------------|
| Frontend | `cd frontend && npm run dev`           | Vercel build + CDN                                             |
| Backend  | `docker compose -f docker-compose.app.yml up` | Droplet container (Gunicorn)                             |
| DB       | DO Managed Postgres                    | Managed service (set `DATABASE_URL`)                           |
| Migrations | `scripts/run_migrations.sh`         | Manual or container start (`RUN_DB_MIGRATIONS=1`)               |

### Legacy

PythonAnywhere scripts are deprecated. Safe to delete when no longer referenced in docs.

