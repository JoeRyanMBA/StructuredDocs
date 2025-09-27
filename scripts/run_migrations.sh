#!/bin/sh
set -e

# Run Alembic migrations inside the running backend container or local env
# Usage (local): DATABASE_URL=... ./scripts/run_migrations.sh
# If running in container orchestrator, ensure env vars are present.

if [ -z "$DATABASE_URL" ]; then
  echo "ERROR: DATABASE_URL is not set" >&2
  exit 1
fi

echo "🚀 Running Alembic migrations..."
python -c "from backend.app import create_app; from backend.extensions import db; from flask_migrate import upgrade; app=create_app();
with app.app_context(): upgrade(); print('✅ Migrations complete')"
