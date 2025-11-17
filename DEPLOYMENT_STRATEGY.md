# StructuredDocs Deployment Strategy

## Current issues and solutions

After experiencing issues with earlier infrastructure setups, this guide outlines a reliable deployment approach together with several fallback options.

## Recommended hybrid strategy

### Option 1 · DigitalOcean App Platform (current baseline)

**Pros:** Full control, database included, auto-scaling

**Cons:** Docker complexity, build reliability issues

### Improvements made

- ✅ Multi-stage Docker build for reliable asset copying

- ✅ Automated build verification

- ✅ Health checks and monitoring

- ✅ Non-root user for security

### Option 2 · Vercel + Railway (preferred alternative)

**Pros:** Extremely reliable, fast deployments, great DX

**Cons:** More complex setup, separate services

#### Frontend on Vercel

```bash

# Deploy frontend only

cd frontend
npm run build
npx vercel --prod

```

#### Backend on Railway

```bash

# Deploy backend as separate service

railway login
railway init
railway up

```

### Step 3 · Trigger the backup plan

```bash

# Deploy to Vercel as backup

npm install -g vercel
vercel --prod

```

## GHCR Redeploy (One-Liner)

Use this when the backend image is published to GHCR and you want to pull and restart the container quickly on the server. Replace placeholders with your values and ensure a token with `packages:read` is available on the host (or injected by your secrets manager).

```bash
ssh <user>@<host> '
  set -euo pipefail
  export GHCR_USER="joeryanmba"
  export GHCR_TOKEN="<your-ghcr-token>" # or use an existing secret/env on the host
  echo "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_USER" --password-stdin
  docker pull ghcr.io/joeryanmba/structured-docs-backend:latest
  docker rm -f structureddocs_app || true
  docker run -d --name structureddocs_app \
    --restart unless-stopped \
    -p 8080:8080 \
    -e PORT=8080 \
    -e DATABASE_URL="${DATABASE_URL:-sqlite:///structured_docs.db}" \
    -e ENABLE_BLUEPRINTS_FILE=.enable_blueprints \
    -e FRONTEND_URL="${FRONTEND_URL:-https://structureddocs.online}" \
    -e ADMIN_API_KEY="${ADMIN_API_KEY:-}" \
    -e EMAIL_PROVIDER="${EMAIL_PROVIDER:-sendgrid}" \
    -e SENDGRID_API_KEY="${SENDGRID_API_KEY:-}" \
    -e DEFAULT_FROM_EMAIL="${DEFAULT_FROM_EMAIL:-no-reply@structureddocs.online}" \
    -e FROM_EMAIL="${FROM_EMAIL:-}" \
    -e FROM_NAME="${FROM_NAME:-StructuredDocs}" \
    -e SENDGRID_VERIFIED_SENDER="${SENDGRID_VERIFIED_SENDER:-}" \
    -v /srv/structured-docs/data/images:/app/backend/static/images \
    -v /srv/structured-docs/instance:/app/instance \
    ghcr.io/joeryanmba/structured-docs-backend:latest
'
```

Notes:

- Adjust volume paths (`/srv/structured-docs/...`) to match your server layout.
- If you already run via `docker compose`, consider a small override file:

```yaml
# docker-compose.ghcr.yml (example)
services:
  backend:
    image: ghcr.io/joeryanmba/structured-docs-backend:latest
    restart: unless-stopped
    ports: ["8080:8080"]
    volumes:
      - ./data/images:/app/backend/static/images
      - ./instance:/app/instance
    environment:
      PORT: 8080
      ENABLE_BLUEPRINTS_FILE: .enable_blueprints
      FRONTEND_URL: https://structureddocs.online
```

Then redeploy with:

```bash
ssh <user>@<host> 'cd /srv/structured-docs && docker compose -f docker-compose.ghcr.yml pull && docker compose -f docker-compose.ghcr.yml up -d'
```

### Verify after redeploy

- API health: `curl -sS https://<your-backend-domain>/api/health`
- Images: `curl -I https://<your-frontend-domain>/images/<file>` (expect 200)
- Aggregated list: `curl -sS https://<your-backend-domain>/api/images | head`

## Images Routing & Persistence

This app now serves images predictably in production and during local dev. Keep these notes handy when deploying or troubleshooting thumbnails/previews.

- Static images route: `GET /images/<path>`
  - Search order: `frontend/dist/images` → `frontend/public/images` → `backend/static/images`
  - This means images imported during runtime (backend) are available without rebuilding the frontend.

- Aggregated images API: `GET /api/images`
  - Returns a combined list from the same three locations, recursively (e.g., `imports/{doc_id}/...`).
  - Useful for thumbnails in Document Builder and the All Images view.

- Vercel rewrites (frontend): ensure these are present so the SPA can reach the backend using same-origin paths
  - In `vercel.json`:
    - `/api/(.*)` → `https://<your-backend-domain>/api/$1`
    - `/images/(.*)` → `https://<your-backend-domain>/images/$1`

- DigitalOcean persistence (backend): persist imported images across restarts
  - In `docker-compose.prod.yml` add a host volume:
    - `./data/images:/app/backend/static/images`
  - Create the host folder once: `mkdir -p ./data/images`

- Environment flags
  - `ENABLE_BLUEPRINTS_FILE=.enable_blueprints` should include `images` to expose `/api/images`.
  - `ENABLE_PLACEHOLDER_ASSETS=1` (optional, local only): when set, creates temporary placeholder JS/CSS in `dist/assets` if bundles are missing. Disabled by default; on production start, known placeholders are cleaned up automatically.
  - `FRONTEND_URL` guides CORS; set to your frontend origin in production.

- Quick verify (production):
  - API: `curl -sS https://<your-backend-domain>/api/images | head`
  - Static: `curl -sS -o /dev/null -w "%{http_code}\n" https://<your-frontend-domain>/images/<some-file>`

## Platform comparison

| Platform     | Reliability | Ease of use | Cost | Best for         |
|--------------|-------------|-------------|------|------------------|
| DigitalOcean | ⭐⭐⭐⭐        | ⭐⭐⭐         | $$   | Full control     |
| Vercel       | ⭐⭐⭐⭐⭐       | ⭐⭐⭐⭐⭐      | $    | Frontend / SPA   |
| Railway      | ⭐⭐⭐⭐⭐       | ⭐⭐⭐⭐       | $$   | Backend / API    |
| Render       | ⭐⭐⭐⭐⭐       | ⭐⭐⭐⭐⭐      | $$   | Simple full apps |

## Troubleshooting checklist

### If assets do not load

1. Check build output: `ls -la frontend/dist/assets/`

2. Verify Docker copy: `docker run structureddocs:latest ls -la frontend/dist/assets/`

3. Check logs: `docker logs <container_id>`

### If the app does not start

1. Check health endpoint: `curl /api/health`

2. Verify environment variables

3. Check database connection

### If the build fails

1. Clear cache: `docker system prune -a`

2. Rebuild: `./build-deploy.sh`

3. Inspect logs for specific errors

## Long-term recommendations

1. **Use Vercel for the frontend** — most reliable for SPAs

2. **Use Railway for the backend** — excellent for Python APIs

3. **Keep DigitalOcean for PostgreSQL** — managed database with backups

4. **Implement CI/CD** — automate testing and deployment gates

5. **Add monitoring** — Sentry, DataDog, or similar tools

## Support and monitoring

- **Health check:** `/api/health`

- **Logs:** DigitalOcean dashboard

- **Metrics:** Monitor response times and error rates

- **Backup:** Maintain a ready-to-ship Vercel deployment

## Migration plan

If you want to transition platforms, follow this phased approach:

1. **Week 1:** Set up Vercel and Railway accounts

2. **Week 2:** Deploy the frontend to Vercel

3. **Week 3:** Deploy the backend to Railway

4. **Week 4:** Test end-to-end functionality and migrate data

5. **Week 5:** Switch DNS and announce the go-live

This sequence provides multiple reliable options and removes single points of failure.
