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

# Always run DB migrations/schema drift checks on startup.
# Default behavior is fail-fast to avoid serving a partially migrated schema.
echo "🗄️ Running DB migrations before start..."
ALLOW_START_WITHOUT_MIGRATIONS=${ALLOW_START_WITHOUT_MIGRATIONS:-0}

run_migrations() {
    if [[ -f /app/run_migrations_production.py ]]; then
        python3 /app/run_migrations_production.py
        return $?
    fi

    # Fallback when the helper script is unavailable.
    if command -v flask >/dev/null 2>&1; then
        flask db upgrade
        return $?
    fi

    echo "❌ No migration runner available (missing run_migrations_production.py and flask CLI)."
    return 1
}

if ! run_migrations; then
    if [[ "$ALLOW_START_WITHOUT_MIGRATIONS" == "1" ]]; then
        echo "⚠️ Migration failed but ALLOW_START_WITHOUT_MIGRATIONS=1, continuing startup."
    else
        echo "❌ Migration failed. Refusing to start with outdated schema."
        exit 1
    fi
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
