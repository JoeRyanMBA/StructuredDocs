#!/bin/bash
# Deploy StructuredDocs to a specific environment VPS.
# Usage: ./scripts/deploy.sh <environment> [server-ip] [image-tag]
#
# Examples:
#   ./scripts/deploy.sh dev
#   ./scripts/deploy.sh staging
#   ./scripts/deploy.sh production 64.225.29.187
#   ./scripts/deploy.sh production 64.225.29.187 2026.05.28

set -euo pipefail

ENV="${1:-}"
OVERRIDE_HOST="${2:-}"
IMAGE_TAG_OVERRIDE="${3:-}"

if [[ -z "$ENV" ]]; then
  echo "Usage: $0 <dev|staging|production> [server-ip]"
  exit 1
fi

if [[ "$ENV" == "test" ]]; then
  ENV="staging"
elif [[ "$ENV" == "training" ]]; then
  ENV="dev"
fi

# ---------------------------------------------------------------------------
# Server IP addresses — update these after provisioning
# ---------------------------------------------------------------------------
DEV_HOST="${STRUCTUREDDOCS_DEV_HOST:-${STRUCTUREDDOCS_TRAINING_HOST:-}}"
STAGING_HOST="${STRUCTUREDDOCS_STAGING_HOST:-${STRUCTUREDDOCS_TEST_HOST:-}}"
PRODUCTION_HOST="${STRUCTUREDDOCS_PRODUCTION_HOST:-}"

case "$ENV" in
  dev)
    REMOTE_HOST="${OVERRIDE_HOST:-$DEV_HOST}"
    ENV_FILE="envs/dev.env.example"
    ;;
  staging)
    REMOTE_HOST="${OVERRIDE_HOST:-$STAGING_HOST}"
    ENV_FILE="envs/staging.env.example"
    ;;
  production)
    REMOTE_HOST="${OVERRIDE_HOST:-$PRODUCTION_HOST}"
    ENV_FILE="envs/production.env.example"
    ;;
  *)
    echo "❌ Unknown environment: $ENV. Must be one of: dev, staging, production"
    exit 1
    ;;
esac

if [[ -z "$REMOTE_HOST" ]]; then
  echo "❌ No IP address for '$ENV' environment."
  echo "   Pass it as a second argument, or set STRUCTUREDDOCS_${ENV^^}_HOST in your shell."
  exit 1
fi

REMOTE_USER="root"
REMOTE_DIR="/opt/structureddocs"
IMAGE_NAME="structureddocs-backend"
TAG="${IMAGE_TAG_OVERRIDE:-latest}"

echo "🚀 Deploying to: $ENV ($REMOTE_HOST)"
echo "   Remote dir:    $REMOTE_DIR"
echo ""

echo "📦 Building Docker image..."
docker build -t ${IMAGE_NAME}:${TAG} .

echo "🗜️  Saving image archive..."
docker save ${IMAGE_NAME}:${TAG} | gzip > structureddocs_backend_image.tar.gz

echo "📤 Copying image to $REMOTE_HOST..."
scp structureddocs_backend_image.tar.gz ${REMOTE_USER}@${REMOTE_HOST}:/tmp/

echo "📋 Copying docker-compose.app.yml..."
scp docker-compose.app.yml ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/docker-compose.yml

ssh ${REMOTE_USER}@${REMOTE_HOST} bash -s -- "$REMOTE_DIR" "$IMAGE_NAME" "$TAG" <<'REMOTE_SCRIPT'
set -euo pipefail
REMOTE_DIR="$1"
IMAGE_NAME="$2"
TAG="$3"

cd "$REMOTE_DIR"

echo "📥 Loading new image..."
gzip -dc /tmp/structureddocs_backend_image.tar.gz | docker load
rm /tmp/structureddocs_backend_image.tar.gz

echo "♻️  Restarting container..."
docker compose down || true
IMAGE_TAG="$TAG" docker compose up -d

echo "⏳ Waiting for health check..."
sleep 5
curl -sf http://localhost:8080/api/health > /dev/null \
  && echo "✅ Health check passed" \
  || (echo "❌ Health check failed" && docker compose logs --tail=50 && exit 1)
REMOTE_SCRIPT

echo "🧹 Cleaning up local archive..."
rm -f structureddocs_backend_image.tar.gz

echo ""
echo "🎉 Deployment complete!"
echo "   Environment: $ENV"
echo "   Server:      $REMOTE_HOST"
echo ""
echo "💡 View logs: ssh $REMOTE_USER@$REMOTE_HOST 'cd $REMOTE_DIR && docker compose logs -f'"
