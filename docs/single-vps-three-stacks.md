# Single VPS with Three Isolated Stacks

This runbook deploys StructuredDocs as three isolated environments on one VPS:

- test
- training
- production

The goal is strict logical isolation (config, data, ports, secrets) while sharing one host.

## Quick start with helper files in this repo

Use the scaffold script and Caddy template added for this deployment style:

- scripts/scaffold_single_vps_three_stacks.sh
- scripts/deploy_single_vps_three_stacks.sh
- Caddyfile.single-vps.template

Example:

```bash
./scripts/scaffold_single_vps_three_stacks.sh \
  --base-dir /opt/structureddocs \
  --repo-url https://github.com/JoeRyanMBA/StructuredDocs.git \
  --branch main
```

Then, in each environment folder (`/opt/structureddocs/test`, `/opt/structureddocs/training`, `/opt/structureddocs/production`):

```bash
docker compose -f docker-compose.single.yml --env-file .env up -d --build
```

For routing, copy and adapt the template:

```bash
cp Caddyfile.single-vps.template /etc/caddy/Caddyfile
```

Deploy all three stacks in promotion order with stop-on-failure:

```bash
./scripts/deploy_single_vps_three_stacks.sh --base-dir /opt/structureddocs
```

Useful variants:

```bash
# Pull first, then deploy test -> training -> production
./scripts/deploy_single_vps_three_stacks.sh --base-dir /opt/structureddocs --pull

# Promote only from training to production
./scripts/deploy_single_vps_three_stacks.sh --base-dir /opt/structureddocs --start-env training --stop-after production

# Deploy only production without rebuilding
./scripts/deploy_single_vps_three_stacks.sh --base-dir /opt/structureddocs --env production --no-build
```

## 1. Architecture

- One VPS hosts three Docker Compose projects.
- One reverse proxy (Caddy or Nginx) routes domains to per-environment backend ports.
- Each environment uses:
  - its own PostgreSQL database
  - its own object storage key prefix
  - its own local bind-mount directories
  - its own environment file and secrets

Example domain and port map:

- test.yourdomain.com -> 127.0.0.1:18080
- training.yourdomain.com -> 127.0.0.1:28080
- app.yourdomain.com -> 127.0.0.1:38080

## 2. Important constraints in this repo

Current production compose files include fixed container names and shared defaults.
On one VPS, fixed names and shared paths cause collisions.

For single-VPS multi-stack deployments:

- avoid fixed `container_name` values
- use different host ports per environment
- use different host bind-mount paths per environment
- use separate `.env` files per environment

## 3. Server directory layout

Create one parent directory and one folder per environment:

- /opt/structureddocs/test
- /opt/structureddocs/training
- /opt/structureddocs/production

Inside each folder:

- app code checkout
- .env
- .enable_blueprints
- data/images
- instance
- docker-compose.single.yml

## 4. Environment variable files

Start from templates:

- envs/test.env.example
- envs/training.env.example
- envs/production.env.example

Required isolation settings per environment:

- DATABASE_URL points to unique database:
  - structureddocs_test
  - structureddocs_training
  - structureddocs_prod
- SPACES_KEY_PREFIX is unique:
  - test
  - training
  - prod
- SECRET_KEY and JWT_SECRET_KEY are unique
- ADMIN_API_KEY is unique
- FRONTEND_URL matches environment domain
- EMAIL_DEBUG is true for test, false for training/prod (recommended)

## 5. Compose file per environment

Create `docker-compose.single.yml` in each environment folder.
Use this template (adjust only the `ports` value per environment):

```yaml
services:
  app:
    build: .
    environment:
      - PORT=8080
      - DATABASE_URL=${DATABASE_URL}
      - DISABLE_SQLITE_FALLBACK=1
      - ENABLE_BLUEPRINTS_FILE=.enable_blueprints
      - STORAGE_BACKEND=local
      - IMAGE_STORAGE_ROOT=/app/data/images
      - FRONTEND_URL=${FRONTEND_URL}
      - SECRET_KEY=${SECRET_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - EMAIL_PROVIDER=${EMAIL_PROVIDER:-smtp}
      - SMTP_SERVER=${SMTP_SERVER:-}
      - SMTP_PORT=${SMTP_PORT:-587}
      - SMTP_USERNAME=${SMTP_USERNAME:-}
      - SMTP_PASSWORD=${SMTP_PASSWORD:-}
      - SMTP_USE_SSL=${SMTP_USE_SSL:-false}
      - DEFAULT_FROM_EMAIL=${DEFAULT_FROM_EMAIL:-no-reply@yourdomain.com}
      - FROM_EMAIL=${FROM_EMAIL:-}
      - FROM_NAME=${FROM_NAME:-StructuredDocs}
      - ADMIN_API_KEY=${ADMIN_API_KEY}
      - RUN_DB_MIGRATIONS=1
    ports:
      - "18080:8080"
    restart: unless-stopped
    volumes:
      - ./.enable_blueprints:/app/.enable_blueprints:ro
      - ./instance:/app/instance
      - ./data/images:/app/data/images
      - ./data/images:/app/backend/static/images
    command: ["./start.sh"]
```

Use different host ports:

- test: 18080:8080
- training: 28080:8080
- production: 38080:8080

## 6. Reverse proxy routes

Configure Caddy or Nginx to route each host to the matching local port.

Caddy example:

```caddy
test.yourdomain.com {
  reverse_proxy 127.0.0.1:18080
}

training.yourdomain.com {
  reverse_proxy 127.0.0.1:28080
}

app.yourdomain.com {
  reverse_proxy 127.0.0.1:38080
}
```

## 7. First-time bootstrap

Repeat per environment folder:

1. Copy env template to `.env` and fill secrets.
2. Create data dirs.
3. Ensure writable paths:
   - `chmod 777 data/images instance`
4. Start stack:
   - `docker compose -f docker-compose.single.yml --env-file .env up -d --build`
5. Verify health:
   - `curl -sS http://127.0.0.1:<env-port>/api/health`

## 8. Deploy and promote

Promotion path:

- test -> training -> production

Deploy command per environment folder:

- `docker compose -f docker-compose.single.yml --env-file .env pull`
- `docker compose -f docker-compose.single.yml --env-file .env up -d --build`

If using local source checkout instead of image pull:

1. `git fetch`
2. `git checkout <target-branch-or-tag>`
3. run compose up command above

## 9. Rollback plan

Before each deploy:

1. take database backup for the target environment
2. capture current image tag/commit

Rollback steps:

1. checkout previous known-good commit or image tag
2. redeploy with compose
3. if migration caused incompatibility, restore environment-specific DB backup

## 10. Operational checks (every release)

- DB URL points to correct environment DB
- Storage prefix matches environment
- Domain routes to correct local port
- Health endpoint returns OK
- Login, create topic, request review, and image upload smoke tests pass

## 11. Known trade-offs of single VPS

Pros:

- lower cost
- simpler initial operations

Cons:

- one host failure impacts all environments
- resource contention between environments
- stricter need for CPU/memory monitoring and limits

## 12. Recommended hardening

- Add container resource limits per environment
- Add nightly DB backups per environment
- Add alerting on disk, memory, and health endpoints
- Keep production deploys gated by test and training smoke checks
