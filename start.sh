#!/bin/bash

# Simple startup script for StructuredDocs
echo "🚀 Starting StructuredDocs..."

# Load .env if present (simple parser: KEY=VALUE lines)
if [[ -f .env ]]; then
    echo "🔧 Loading environment from .env"
    set -o allexport
    # shellcheck disable=SC2046
    eval $(grep -E '^[A-Za-z_][A-Za-z0-9_]*=.*$' .env | sed 's/^/export /')
    set +o allexport
fi

# Set environment variables
export PYTHONPATH="/app:$PYTHONPATH"

# Change to app directory
cd /app

# Always run DB migrations/schema drift checks on startup
echo "🗄️ Running DB migrations before start..."
if [[ -f /app/run_migrations_production.py ]]; then
    python3 /app/run_migrations_production.py || echo "⚠️ Migrations script failed (continuing to start)"
else
    echo "⚠️ Migration script not found at /app/run_migrations_production.py"
fi

# Start Gunicorn
PORT_TO_BIND=${PORT:-8080}
exec python3 -m gunicorn \
    --bind 0.0.0.0:${PORT_TO_BIND} \
    --workers 2 \
    --timeout 120 \
    --log-level info \
    --access-logfile - \
    --error-logfile - \
    "backend.app:create_app()"
