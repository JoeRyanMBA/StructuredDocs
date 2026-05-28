# Multi-Environment Setup (VPS)

StructuredDocs runs in three isolated environments: test, training, and production. Each environment can run on a separate VPS, while sharing one managed PostgreSQL cluster and one S3-compatible object-storage bucket using key prefixes.

## Architecture

- test server -> database: structureddocs_test -> storage prefix: test/
- training server -> database: structureddocs_training -> storage prefix: training/
- production server -> database: structureddocs_prod -> storage prefix: prod/

## Initial setup

1. Provision three Linux servers (Ubuntu 22.04 or newer):

- structureddocs-test
- structureddocs-training
- structureddocs-production

1. Provision one managed PostgreSQL cluster and create three databases:

- structureddocs_test
- structureddocs_training
- structureddocs_prod

1. Provision one S3-compatible bucket for shared assets.

1. Configure each environment file from `envs/*.env.example` and set:

- `DATABASE_URL` for that environment
- `SPACES_BUCKET`, `SPACES_REGION`, `SPACES_ACCESS_KEY`, `SPACES_SECRET_KEY`
- `SPACES_KEY_PREFIX` to test, training, or prod

## Deployment

Use your deployment script per environment:

```bash
./scripts/deploy.sh test
./scripts/deploy.sh training
./scripts/deploy.sh production
```

## Branching strategy

feature/* -> test -> training -> main

## Storage isolation

Images are isolated by `SPACES_KEY_PREFIX` so environments do not overwrite each other.

## Cost controls

- Stop non-production servers when idle.
- Monitor database and object-storage usage monthly.

## Single VPS alternative

If you want lower cost and can accept a single host as a shared failure domain,
run three isolated stacks on one VPS (test, training, production) with:

- separate compose project names
- separate directories and volumes
- separate databases
- separate storage prefixes
- separate env files and secrets

See full guide: `docs/single-vps-three-stacks.md`
