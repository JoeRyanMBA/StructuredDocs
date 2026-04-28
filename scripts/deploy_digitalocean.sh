#!/bin/bash
# Deploy to a VPS via SSH using Docker Compose
# Prerequisites: SSH key added, remote has docker + docker-compose plugin
# Usage: ./scripts/deploy_digitalocean.sh [REMOTE_HOST]

set -euo pipefail

REMOTE_HOST="${1:-64.225.29.187}"  # Can override with first argument
REMOTE_USER="root"                  # or a non-root sudo user
REMOTE_DIR="/opt/structureddocs"
IMAGE_NAME="structureddocs-backend"
TAG="latest"

echo "🚀 Building multi-stage image locally..."
docker build -t ${IMAGE_NAME}:${TAG} .

echo "📦 Saving image archive..."
docker save ${IMAGE_NAME}:${TAG} | gzip > structureddocs_backend_image.tar.gz

echo "📤 Copying image to remote host..."
scp structureddocs_backend_image.tar.gz ${REMOTE_USER}@${REMOTE_HOST}:/tmp/

echo "📋 Copying docker-compose.yml to remote host..."
scp docker-compose.prod.yml ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/docker-compose.yml || \
scp docker-compose.yml ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/docker-compose.yml || \
echo "⚠️  Could not find docker-compose file"

ssh ${REMOTE_USER}@${REMOTE_HOST} bash -s <<'EOF'
set -euo pipefail
REMOTE_DIR="/opt/structureddocs"
IMAGE_NAME="structureddocs-backend"
TAG="latest"
mkdir -p "$REMOTE_DIR"
cd "$REMOTE_DIR"

echo "📥 Loading new image..."
gzip -dc /tmp/structureddocs_backend_image.tar.gz | docker load
rm /tmp/structureddocs_backend_image.tar.gz || true

echo "🗑️  Cleaning old containers..."
docker ps -a --filter "name=structureddocs-backend" -q | xargs -r docker rm -f

echo "🗄️  Starting application with Docker Compose..."
cd "$REMOTE_DIR"

# Stop and remove existing containers
docker compose down || true

# Start with docker compose (includes volume mounts)
docker compose up -d

echo "🧪 Health check (curl)..."
sleep 5
curl -f http://localhost:8080/api/health || (echo "❌ Health check failed" && docker compose logs && exit 1)

echo "✅ Deployment successful"
echo "📁 Images persist in: $REMOTE_DIR/data/images"
echo "📁 Database persists in: $REMOTE_DIR/instance"
EOF

echo "🧹 Cleaning local artifacts..."
rm structureddocs_backend_image.tar.gz || true

echo ""
echo "🎉 Deployment complete!"
echo "   Server: $REMOTE_HOST"
echo "   Images: $REMOTE_DIR/data/images"
echo "   Database: $REMOTE_DIR/instance"
echo ""
echo "💡 To check logs: ssh $REMOTE_USER@$REMOTE_HOST 'cd $REMOTE_DIR && docker compose logs -f'"
