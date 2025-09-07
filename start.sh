#!/bin/bash

# Simple startup script for StructuredDocs
echo "🚀 Starting StructuredDocs..."

# Set environment variables
export PYTHONPATH="/app:$PYTHONPATH"

# Change to app directory
cd /app

# Optionally run DB migrations before starting
if [[ "${RUN_DB_MIGRATIONS}" == "1" ]]; then
    echo "🗄️ Running DB migrations before start..."
    if [[ -f /app/run_migrations_production.py ]]; then
        python3 /app/run_migrations_production.py || echo "⚠️ Migrations script failed (continuing to start)"
    else
        echo "⚠️ Migration script not found at /app/run_migrations_production.py"
    fi
fi

# Start Gunicorn
PORT_TO_BIND=${PORT:-8080}
exec python3 -m gunicorn \
    --bind 0.0.0.0:${PORT_TO_BIND} \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    "backend.app:create_app()"
