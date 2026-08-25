#!/usr/bin/env bash
# Production deploy script for a VPS host
# Usage: ./deploy.sh
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/structureddocs}"
COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-structureddocs}"
REPO="https://github.com/JoeRyanMBA/StructuredDocs.git"
BRANCH="main"

echo "=== StructuredDocs Deploy ==="

if [[ ! -f "$APP_DIR/docker-compose.yml" && -d "$APP_DIR/app" ]]; then
  APP_DIR="$APP_DIR/app"
fi

cd "$APP_DIR"
git config --global --add safe.directory "$APP_DIR"

# The container runs as appuser (UID 1000) and needs to write runtime uploads.
mkdir -p "$APP_DIR/data/branding"
chown -R 1000:1000 "$APP_DIR/data/branding"

# If not a git repo, initialise it (one-time setup)
if [ ! -d ".git" ]; then
  echo "Initialising git repo..."
  git init
  git remote add origin "$REPO"
  git fetch origin "$BRANCH"
  git reset --hard "origin/$BRANCH"
  echo "Git repo initialised."
else
  echo "Pulling latest code from $BRANCH..."
  git fetch origin "$BRANCH"
  git reset --hard "origin/$BRANCH"
fi

# Enable BuildKit for faster pip caching
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

echo "Building Docker image..."
docker compose -p "$COMPOSE_PROJECT_NAME" build

echo "Restarting containers..."
docker compose -p "$COMPOSE_PROJECT_NAME" up -d

echo "Waiting for startup..."
sleep 5

echo "Container status:"
docker ps --filter name=structureddocs

echo ""
echo "Recent logs:"
docker compose -p "$COMPOSE_PROJECT_NAME" logs --tail 20 2>/dev/null || true

echo ""
echo "=== Deploy complete ==="
