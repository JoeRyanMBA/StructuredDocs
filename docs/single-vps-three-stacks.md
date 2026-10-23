# Single VPS with Three Isolated Stacks

This runbook deploys StructuredDocs as three isolated environments on one VPS:

- dev
- staging
- production

The goal is strict logical isolation (config, data, ports, secrets) while sharing one host.

## Quick start with helper files in this repo

Use the scaffold script and Caddy template added for this deployment style:

- scripts/scaffold_single_vps_three_stacks.sh
- scripts/deploy_single_vps_three_stacks.sh
- scripts/smoke_check_env.sh
- scripts/backup_env_db.sh
- scripts/restore_env_db.sh
- Caddyfile.single-vps.template

Example:

```bash
./scripts/scaffold_single_vps_three_stacks.sh \
  --base-dir /opt/structureddocs \
  --repo-url https://github.com/JoeRyanMBA/StructuredDocs.git \
  --branch main
```

Then start each stack from its environment folder using its matching project name (`structureddocs_dev`, `structureddocs_staging`, or `structureddocs_production`). For example, start staging with:

```bash
docker compose -p structureddocs_staging \
  -f docker-compose.single.yml --env-file .env up -d --build
```

For an existing staging stack started without `-p`, perform this one-time migration before deploying: stop the old `staging` project, update its Compose image line to the isolated staging reference shown below, then start it with `-p structureddocs_staging`. Do not add `-v` to the `down` command; the stack's bind-mounted data is preserved.

```bash
docker compose -p staging -f docker-compose.single.yml --env-file .env down
# Set the image line in docker-compose.single.yml to:
# image: ${IMAGE_REPO:-structureddocs-staging-backend}:${IMAGE_TAG:-latest}
docker compose -p structureddocs_staging \
  -f docker-compose.single.yml --env-file .env up -d --build
```

For production, use the `structureddocs_production` Compose project name so it remains isolated from the legacy app and the other stacks:

```bash
docker compose -p structureddocs_production \
  -f docker-compose.single.yml --env-file .env up -d --build
```

The scaffold script installs the Caddy template at `/etc/caddy/Caddyfile` if that file does not already exist. It preserves an existing Caddy config. Edit the example hostnames in the installed file, then validate and reload the host Caddy service:

```bash
sudo caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile
sudo systemctl enable --now caddy
sudo systemctl reload caddy
```

Deploy all three stacks in promotion order with stop-on-failure:

```bash
./scripts/deploy_single_vps_three_stacks.sh --base-dir /opt/structureddocs
```

By default this script now performs, for each environment in order:

- deploy
- health check (`/api/health`)
- smoke checks (`/api/health`, `/api/version`, and `/`)

Useful variants:

```bash
# Pull first, then deploy dev -> staging -> production
./scripts/deploy_single_vps_three_stacks.sh --base-dir /opt/structureddocs --pull

# Promote only from staging to production
./scripts/deploy_single_vps_three_stacks.sh --base-dir /opt/structureddocs --start-env staging --stop-after production

# Deploy only production without rebuilding
./scripts/deploy_single_vps_three_stacks.sh --base-dir /opt/structureddocs --env production --no-build

# Promote one immutable image tag across all environments
./scripts/deploy_single_vps_three_stacks.sh --base-dir /opt/structureddocs --image-tag 2026.05.28

# Promote one immutable tag from a specific registry/repo
./scripts/deploy_single_vps_three_stacks.sh \
  --base-dir /opt/structureddocs \
  --image-repo ghcr.io/joeryanmba/structured-docs-backend \
  --image-tag 2026.05.28
```

## 1. Architecture

### GitHub branch deployments

- Pushes or merged pull requests to `dev` run **Deploy Dev To VPS**.
- Pushes or merged pull requests to `staging` run **Deploy Staging Stack**,
  rebuilding `/opt/structureddocs/staging` with Compose project
  `structureddocs_staging` on port `28080`. This workflow uses the required repository-level
  `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY`, and `VPS_HOST_KEY` secrets, plus the
  optional `VPS_PORT` secret. It preserves server-local configuration and data.
- Pushes or merged pull requests to `main` run **Deploy Production Stack**.
  The protected `production` environment must be approved in the run's
  **Review deployments** panel before deployment starts. A successful PR
  build does not mean the live application has been updated.

The staging workflow must first be merged into `staging` before automatic
staging deployments can run. Its **Run workflow** action can also deploy the
`staging` branch manually once GitHub exposes the workflow from the default
branch. Production approval remains separate and is not bypassed by staging.

- One VPS hosts three Docker Compose projects.
- One reverse proxy (Caddy or Nginx) routes domains to per-environment backend ports.
- Each environment uses:
  - its own PostgreSQL database
  - its own object storage key prefix
  - its own local bind-mount directories
  - its own environment file and secrets

For the final working setup on this VPS, PostgreSQL runs on the host rather than in a container, and each app container connects back to it through `host.docker.internal:5432`.

Domain and port map:

- dev.structureddocs.online -> 127.0.0.1:18080
- staging.structureddocs.online -> 127.0.0.1:28080
- structureddocs.online -> 127.0.0.1:38080

## 2. Important constraints in this repo

Legacy production compose files may include fixed container names and shared defaults.
On one VPS, fixed names and shared paths cause collisions.

For single-VPS multi-stack deployments:

- avoid fixed `container_name` values
- use different host ports per environment
- use different host bind-mount paths per environment
- use separate `.env` files per environment

## 3. Server directory layout

Create one parent directory and one folder per environment:

- /opt/structureddocs/dev
- /opt/structureddocs/staging
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

- envs/dev.env.example
- envs/staging.env.example
- envs/production.env.example

Required isolation settings per environment:

- DATABASE_URL points to unique database:
  - structureddocs_dev
  - structureddocs_staging
  - structureddocs_prod
- SPACES_KEY_PREFIX is unique:
  - dev
  - staging
  - prod
- SECRET_KEY and JWT_SECRET_KEY are unique
- ADMIN_API_KEY is unique
- FRONTEND_URL matches environment domain
- EMAIL_DEBUG is true for dev, false for staging/prod (recommended)

Working host-Postgres values for this VPS:

- use `host.docker.internal` in `DATABASE_URL`
- use port `5432`
- use `sslmode=disable`
- add a `pg_hba.conf` rule for each Docker bridge subnet used by the stacks

Example `DATABASE_URL` values:

- dev: `postgresql://structureddocs_dev:YOUR_DEV_PASSWORD@host.docker.internal:5432/structureddocs_dev?sslmode=disable`
- staging: `postgresql://structureddocs_staging:YOUR_STAGING_PASSWORD@host.docker.internal:5432/structureddocs_staging?sslmode=disable`

## 4.1 Secrets and keys during promotion

You do not rotate secrets every time you promote a release.

Use this model:

- Keep one stable secret set per environment (`dev`, `staging`, `production`).
- Promote the same immutable image tag across environments.
- Let each environment inject its own secrets from its local `.env` file.

In practice:

- `SECRET_KEY`, `JWT_SECRET_KEY`, `ADMIN_API_KEY`, `DATABASE_URL`, and storage credentials stay environment-specific.
- Release promotion changes only image/commit version, not secret values.
- Rotate secrets on a schedule or incident response basis, not for every deploy.

## 5. Compose file per environment

Create `docker-compose.single.yml` in each environment folder.
Use this template (set a different `IMAGE_REPO` for each environment, then adjust the `ports` value):

```yaml
services:
  app:
    build: .
    image: ${IMAGE_REPO:?Set an environment-specific image repository}:${IMAGE_TAG:-latest}
    extra_hosts:
      - "host.docker.internal:host-gateway"
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
    mem_limit: ${APP_MEM_LIMIT:-1g}
    cpus: ${APP_CPU_LIMIT:-1.0}
    volumes:
      - ./.enable_blueprints:/app/.enable_blueprints:ro
      - ./instance:/app/instance
      - ./data/images:/app/data/images
      - ./data/images:/app/backend/static/images
    command: ["./start.sh"]
```

Use `structureddocs-dev-backend`, `structureddocs-staging-backend`, and `structureddocs-production-backend` for the three local image repositories. The scaffold generates these environment-specific defaults automatically.

The app reads `.enable_blueprints` as a single comma-separated line. The working value on this VPS is:

```text
users,admin,find_replace,collections,dashboard,feedback,help_links,images,import_handler,links,metrics,milestones,notifications,public_images,variables,projects,publications,review_tokens,reviews,bulk_reviews,sequences,stakeholders,snippets,tags,tasks,topics
```

Use different host ports:

- dev: 18080:8080
- staging: 28080:8080
- production: 38080:8080

Note:

- This repository also includes a canonical base compose template at `docker-compose.base.yml`.
- For root-level production deploys, use both files together:
  `docker compose -f docker-compose.base.yml -f docker-compose.prod.yml up -d`

## 6. Reverse proxy routes

Configure Caddy or Nginx to route each host to the matching local port.

Caddy example:

```caddy
dev.yourdomain.com {
  reverse_proxy 127.0.0.1:18080
}

staging.yourdomain.com {
  reverse_proxy 127.0.0.1:28080
}

app.yourdomain.com {
  reverse_proxy 127.0.0.1:38080
}
```

## 7. First-time bootstrap

Repeat per environment folder:

1. Copy env template to `.env` and fill secrets.
   For this VPS migration, production can reuse the existing production database by setting the valid production `DATABASE_URL` in `/opt/structureddocs/production/.env`. Do not copy Dev or Staging database settings into it.
2. Create data dirs.
3. Ensure writable paths:
   `chmod 777 data/images instance`
4. If PostgreSQL is on the host, add the production Docker bridge subnet to `/etc/postgresql/16/main/pg_hba.conf`. Find the subnet with `docker network inspect structureddocs_production_default`; permit only the required database/user and that subnet, never the public IP or all IPs.
5. Start stack:
   `docker compose -p structureddocs_production -f docker-compose.single.yml --env-file .env up -d --build`
6. Verify health:
   `curl -fsS http://127.0.0.1:38080/api/health`

## 8. Migrate production from the legacy app

The live site currently uses the legacy app under `/opt/structureddocs/app`, with Caddy proxying `structureddocs.online` to `app:8080`. The isolated production stack is deployed separately to `/opt/structureddocs/production` on port `38080`. Keep the old app running until the new stack and proxy cutover are verified.

The `Deploy Production Stack` GitHub Actions workflow syncs `main` into `/opt/structureddocs/production` and builds that stack. It preserves server-local `.env` files, Compose configuration, blueprint selection, uploads, instance files, and backups. It does not change Caddy.

Before merging the workflow change to `main`:

1. Disable the legacy `Deploy To VPS` workflow in GitHub Actions so it cannot deploy to `/opt/structureddocs/app` or interfere with Caddy.
2. Ensure `/opt/structureddocs/production/.env`, `docker-compose.single.yml`, and `.enable_blueprints` exist and are readable by the deploy user.
3. Configure production `.env` with the current production database connection and production secrets. Do not overwrite an existing production `.env` without backing it up and reviewing it privately.
   Include a non-empty `ADMIN_API_KEY`; the production deployment workflow checks for it before syncing or building.
4. Ensure the production Compose file builds from `.` and maps `38080:8080`. It must include `extra_hosts: ["host.docker.internal:host-gateway"]` when its database URL uses `host.docker.internal`.
5. Ensure the PostgreSQL `pg_hba.conf` permits the production Docker network subnet. A successful login from the legacy stack’s network does not prove the production stack’s subnet is allowed.
6. Configure the GitHub `production` environment with a required reviewer before enabling automatic production deployment.

After the updated workflow is merged to `main`, wait for the production deployment to pass its health check at `http://127.0.0.1:38080/api/health`. Confirm the new app responds before changing the public route.

For the current containerized Caddy setup, back up `/opt/structureddocs/app/Caddyfile`, then change only the `structureddocs.online` upstream from `app:8080` to `host.docker.internal:38080`. Validate and reload Caddy:

```bash
docker exec structureddocs-caddy-1 \
  caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile
docker exec structureddocs-caddy-1 \
  caddy reload --config /etc/caddy/Caddyfile
curl --resolve structureddocs.online:443:127.0.0.1 \
  -fsS https://structureddocs.online/api/health
```

If the public health check fails, restore the Caddyfile backup and reload Caddy; leave the old app available for rollback. Once production is verified, stop only the legacy app service, not its Caddy service:

```bash
docker compose -p structureddocs \
  --env-file /opt/structureddocs/.env \
  -f /opt/structureddocs/app/docker-compose.yml stop app
```

The migration reuses the existing production database; it does not drop or recreate it.

## 9. Deploy and promote

Promotion path:

- dev -> staging -> production

Deploy command per environment folder:

- `docker compose -p structureddocs_<environment> -f docker-compose.single.yml --env-file .env pull`
- `docker compose -p structureddocs_<environment> -f docker-compose.single.yml --env-file .env up -d --build`

In the working host-Postgres setup, the app container must have `extra_hosts` for `host.docker.internal`, and `DATABASE_URL` must point at `host.docker.internal:5432` with `sslmode=disable`.

If using local source checkout instead of image pull:

1. `git fetch`
2. `git checkout <target-branch-or-tag>`
3. run compose up command above

## 10. Rollback plan

Before each deploy:

1. take database backup for the target environment
2. capture current image tag/commit

Rollback steps:

1. checkout previous known-good commit or image tag
2. redeploy with compose
3. if migration caused incompatibility, restore environment-specific DB backup

### Backup and restore helpers

Backup one environment database:

```bash
./scripts/backup_env_db.sh --env dev --base-dir /opt/structureddocs
```

Restore one environment database:

```bash
./scripts/restore_env_db.sh --env dev --base-dir /opt/structureddocs --file /opt/structureddocs/dev/backups/dev_YYYYMMDDTHHMMSSZ.dump
```

## 11. Operational checks (every release)

- DB URL points to correct environment DB
- Storage prefix matches environment
- Domain routes to correct local port
- Health endpoint returns OK
- Login, create topic, request review, and image upload smoke tests pass

## 12. Known trade-offs of single VPS

Pros:

- lower cost
- simpler initial operations

Cons:

- one host failure impacts all environments
- resource contention between environments
- stricter need for CPU/memory monitoring and limits

## 13. Recommended hardening

- Add container resource limits per environment
- Add nightly DB backups per environment
- Add alerting on disk, memory, and health endpoints
- Keep production deploys gated by dev and staging smoke checks
