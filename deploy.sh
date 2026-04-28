#!/usr/bin/env bash
# Production deploy script for a VPS host
# Usage: ./deploy.sh
set -euo pipefail

APP_DIR="/opt/structureddocs"
REPO="https://github.com/JoeRyanMBA/StructuredDocs.git"
BRANCH="main"

echo "=== StructuredDocs Deploy ==="

cd "$APP_DIR"

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
docker compose build

echo "Restarting containers..."
docker compose up -d

echo "Waiting for startup..."
sleep 5

echo "Container status:"
docker ps --filter name=structureddocs

echo ""
echo "Recent logs:"
docker logs structureddocs_app --tail 20 2>/dev/null || true

echo ""
echo "=== Deploy complete ==="
