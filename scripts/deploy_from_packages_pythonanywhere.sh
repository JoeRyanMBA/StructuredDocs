#!/usr/bin/env bash
set -euo pipefail

# Simple deploy: unpack backend/frontend packages, install deps, migrate, seed admin.
# Usage:
#   VENV_PATH=$HOME/.virtualenvs/structureddocs \
#   ADMIN_EMAIL=admin@example.com ADMIN_PASSWORD='password' \
#   bash scripts/deploy_from_packages_pythonanywhere.sh [frontend_package.tar.gz] [backend_package.tar.gz]

APP_DIR=$(pwd)
FRONTEND_TGZ="${1:-$APP_DIR/frontend_package.tar.gz}"
BACKEND_TGZ="${2:-$APP_DIR/backend_package.tar.gz}"
VENV_PATH="${VENV_PATH:-$HOME/.virtualenvs/structureddocs}"

echo "App dir: $APP_DIR"
echo "Frontend package: $FRONTEND_TGZ"
echo "Backend package:  $BACKEND_TGZ"
echo "Venv: $VENV_PATH"

if [[ ! -f "$FRONTEND_TGZ" ]]; then
  echo "Missing frontend package: $FRONTEND_TGZ" >&2; exit 1
fi
if [[ ! -f "$BACKEND_TGZ" ]]; then
  echo "Missing backend package: $BACKEND_TGZ" >&2; exit 1
fi
if [[ ! -x "$VENV_PATH/bin/python" ]]; then
  echo "Virtualenv Python not found at $VENV_PATH/bin/python" >&2; exit 1
fi

echo "Unpacking backend..."
tar -xzf "$BACKEND_TGZ" -C "$APP_DIR"

echo "Unpacking frontend into frontend/dist..."
mkdir -p "$APP_DIR/frontend/dist"
tar -xzf "$FRONTEND_TGZ" -C "$APP_DIR/frontend/dist"

echo "Installing backend requirements..."
source "$VENV_PATH/bin/activate"
pip install -r "$APP_DIR/backend/requirements.txt"

echo "Applying migrations..."
export PYTHONPATH="$APP_DIR:$PYTHONPATH"
python - <<'PY'
from backend.app import create_app
from flask_migrate import upgrade
app = create_app()
with app.app_context():
    upgrade(directory='backend/migrations')
print('✅ Migrations applied')
PY

echo "Seeding admin user..."
python "$APP_DIR/backend/create_admin.py" \
  --email "${ADMIN_EMAIL:-admin@example.com}" \
  --password "${ADMIN_PASSWORD:-password}"

echo "Done. Go to the PythonAnywhere Web tab and click Reload for your app."
