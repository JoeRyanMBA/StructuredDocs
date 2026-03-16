# Multi-Environment Setup (DigitalOcean)

StructuredDocs runs in three isolated environments: **test**, **training**, and **production**. Each has its own droplet, but they share one Managed PostgreSQL cluster and one Spaces bucket (using folder prefixes for isolation).

## Architecture

```
                      ┌─────────────────────────────────────┐
                      │  Shared Managed PostgreSQL Cluster  │
                      │  structureddocs_test                │
                      │  structureddocs_training            │
                      │  structureddocs_prod                │
                      └─────────────────────────────────────┘
                                       ▲  ▲  ▲
          ┌────────────┐   ┌───────────┘  │  └────────────┐
          │ Test       │   │ Training      │   Production  │
          │ Droplet    │   │ Droplet       │   Droplet     │
          │ $5/mo      │   │ $5/mo         │   $15-25/mo   │
          └────────────┘   └───────────────┘   └───────────┘
                      ▼          ▼                    ▼
                      ┌─────────────────────────────────────┐
                      │  Shared Spaces Bucket               │
                      │  test/images/...                    │
                      │  training/images/...                │
                      │  prod/images/...                    │
                      └─────────────────────────────────────┘
```

## Estimated Monthly Cost

| Resource | Test | Training | Production | Notes |
|---|---|---|---|---|
| Droplet | $5 | $5 | $15–25 | 1 vCPU/1 GB for test+training |
| Managed Postgres | — | — | ~$15 | Shared across all three |
| Spaces | — | — | ~$5 | Shared bucket with prefixes |
| **Total** | | | | **~$45–55/month** |

## Initial Setup (One-Time)

### 1. Provision Resources in DigitalOcean

1. Create **3 Droplets** (Ubuntu 22.04 LTS):
   - `structureddocs-test` — 1 vCPU / 1 GB ($5/mo)
   - `structureddocs-training` — 1 vCPU / 1 GB ($5/mo)
   - `structureddocs-production` — 2 vCPU / 2 GB or larger ($15+/mo)

2. Create **1 Managed PostgreSQL** cluster (smallest tier).  
   Note the admin connection string from the DO control panel.

3. Create **1 Spaces bucket** named `structureddocs-assets`.  
   Generate a Spaces Access Key in API → Spaces Keys.

### 2. Initialise Databases

```bash
export PG_ADMIN_URL="postgresql://doadmin:PASSWORD@DB_HOST:25060/defaultdb?sslmode=require"
./scripts/init_databases.sh
```

This creates `structureddocs_test`, `structureddocs_training`, and `structureddocs_prod` databases, each with a dedicated user.

### 3. Bootstrap Each Droplet

Run once on each new droplet (replace IP and env accordingly):

```bash
# From your local machine:
ssh root@TEST_DROPLET_IP 'bash -s' < scripts/setup_droplet.sh test
ssh root@TRAINING_DROPLET_IP 'bash -s' < scripts/setup_droplet.sh training
ssh root@PROD_DROPLET_IP 'bash -s' < scripts/setup_droplet.sh production
```

### 4. Fill In Real Secrets

SSH into each droplet and edit the env file with real credentials:

```bash
ssh root@TEST_DROPLET_IP
nano /opt/structureddocs/backend.env
```

Key values to set per environment:
- `SECRET_KEY` and `JWT_SECRET_KEY` (unique per env — use `python -c "import secrets; print(secrets.token_hex(32))"`)
- `DATABASE_URL` with the correct database name and user password
- `SPACES_ACCESS_KEY`, `SPACES_SECRET_KEY` (same key works for all envs)
- `FRONTEND_URL` (your Vercel preview/prod URL)

See `envs/<environment>.env.example` for the full list of variables.

## Deploying

### Set Droplet IPs (once, in your shell profile)

```bash
export STRUCTUREDDOCS_TEST_HOST=YOUR_TEST_DROPLET_IP
export STRUCTUREDDOCS_TRAINING_HOST=YOUR_TRAINING_DROPLET_IP
export STRUCTUREDDOCS_PRODUCTION_HOST=YOUR_PRODUCTION_DROPLET_IP
```

### Deploy to an Environment

```bash
./scripts/deploy.sh test
./scripts/deploy.sh training
./scripts/deploy.sh production

# Or override the IP inline:
./scripts/deploy.sh production 64.225.29.187
```

The script builds the Docker image locally, ships it to the droplet, and restarts the container.

## Git Branching Strategy

Promotions flow in one direction:

```
feature/* → test → training → main (production)
```

| Branch | Environment | Deployed by |
|---|---|---|
| `test` | Test droplet | Push to `test` branch |
| `training` | Training droplet | Merge `test` → `training` |
| `main` | Production droplet | Merge `training` → `main` |

## Spaces Folder Isolation

Each environment uploads images under its own folder prefix, controlled by `SPACES_KEY_PREFIX` in the env file:

| Environment | Prefix | Example key |
|---|---|---|
| test | `test` | `test/images/abc123.png` |
| training | `training` | `training/images/abc123.png` |
| production | `prod` | `prod/images/abc123.png` |

Images from one environment cannot overwrite another's assets.

## Cost Control Tips

- **Shut down test/training droplets** when not in use (you only pay for Droplet storage, not CPU, when powered off).
- Monitor usage in DO → Monitoring; downscale if consistently under-utilised.
- The Spaces 250 GB included storage comfortably covers all three environments at typical usage.
