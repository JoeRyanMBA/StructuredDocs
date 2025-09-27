#!/bin/bash
# Deploy to DigitalOcean Droplet via SSH using Docker
# Prerequisites: SSH key added, remote has docker + docker-compose plugin
# Usage: ./scripts/deploy_digitalocean.sh

set -euo pipefail

REMOTE_HOST="your_droplet_ip"   # e.g. 203.0.113.10
REMOTE_USER="root"              # or a non-root sudo user
REMOTE_DIR="/opt/structureddocs"
IMAGE_NAME="structureddocs-backend"
TAG="latest"

echo "🚀 Building multi-stage image locally..."
docker build -t ${IMAGE_NAME}:${TAG} .

echo "📦 Saving image archive..."
docker save ${IMAGE_NAME}:${TAG} | gzip > structureddocs_backend_image.tar.gz

echo "📤 Copying image to remote host..."
scp structureddocs_backend_image.tar.gz ${REMOTE_USER}@${REMOTE_HOST}:/tmp/

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

echo "🗄️  Starting new container..."
docker run -d --name structureddocs-backend \
  -p 8080:8080 \
  --env-file backend.env \
  --restart unless-stopped \
  structureddocs-backend:latest

echo "🧪 Health check (curl)..."
sleep 5
curl -f http://localhost:8080/api/health || (echo "❌ Health check failed" && docker logs structureddocs-backend && exit 1)

echo "✅ Deployment successful"
EOF

echo "🧹 Cleaning local artifacts..."
rm structureddocs_backend_image.tar.gz || true

echo "🎉 Done. Remember to create a backend.env on the server with real secrets."
