#!/bin/bash
# Bootstrap a new Linux VPS for a given environment.
# Run this on the server itself (or pipe via SSH) immediately after provisioning.
#
# Usage (run on the server):
#   bash "$0" <dev|staging|production>
#
# Usage (run from local machine):
#   ssh root@SERVER_IP 'bash -s' < /path/to/this-script.sh dev

set -euo pipefail

ENV="${1:-}"
if [[ "$ENV" == "test" ]]; then
  ENV="staging"
elif [[ "$ENV" == "training" ]]; then
  ENV="dev"
fi

if [[ -z "$ENV" || ! "$ENV" =~ ^(dev|staging|production)$ ]]; then
  echo "Usage: $0 <dev|staging|production>"
  exit 1
fi

REMOTE_DIR="/opt/structureddocs"

echo "🚀 Setting up StructuredDocs VPS — environment: $ENV"
echo "   App dir: $REMOTE_DIR"
echo ""

# ---------------------------------------------------------------------------
# Docker
# ---------------------------------------------------------------------------
if ! command -v docker &>/dev/null; then
  echo "📦 Installing Docker..."
  apt-get update -qq
  apt-get install -y ca-certificates curl gnupg

  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
    | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  chmod a+r /etc/apt/keyrings/docker.gpg

  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
    | tee /etc/apt/sources.list.d/docker.list > /dev/null

  apt-get update -qq
  apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

  systemctl enable docker
  systemctl start docker
  echo "✅ Docker $(docker --version) installed"
else
  echo "✅ Docker already installed: $(docker --version)"
fi

# ---------------------------------------------------------------------------
# App directories
# ---------------------------------------------------------------------------
echo "📁 Creating application directories..."
mkdir -p "$REMOTE_DIR/data/images" "$REMOTE_DIR/instance"
chmod 777 "$REMOTE_DIR/data/images" "$REMOTE_DIR/instance"

# ---------------------------------------------------------------------------
# Blueprint config
# ---------------------------------------------------------------------------
cat > "$REMOTE_DIR/.enable_blueprints" <<'BLUEPRINTS'
auth
collections
topics
publications
images
search
documents
notifications
BLUEPRINTS
echo "✅ .enable_blueprints written"

# ---------------------------------------------------------------------------
# Environment-specific backend.env template
# ---------------------------------------------------------------------------
ENV_TEMPLATE="envs/${ENV}.env.example"
DEST_ENV="$REMOTE_DIR/backend.env"

if [[ -f "$ENV_TEMPLATE" ]]; then
  cp "$ENV_TEMPLATE" "$DEST_ENV"
  echo "✅ backend.env seeded from $ENV_TEMPLATE"
else
  echo "⚠️  $ENV_TEMPLATE not found — creating a minimal placeholder"
  cat > "$DEST_ENV" <<ENVPLACEHOLDER
APP_ENV=$ENV
PORT=8080
FLASK_ENV=production
SECRET_KEY=CHANGE_ME
JWT_SECRET_KEY=CHANGE_ME
DATABASE_URL=postgresql://structureddocs_${ENV}:CHANGE_ME@DB_HOST:25060/structureddocs_${ENV}?sslmode=require
FRONTEND_URL=https://CHANGE_ME
RUN_DB_MIGRATIONS=1
ENVPLACEHOLDER
fi

echo ""
echo "🎉 VPS setup complete for: $ENV"
echo ""
echo "⚠️  REQUIRED: Edit the env file with real secrets before deploying:"
echo "   nano $DEST_ENV"
echo ""
echo "📋 Then deploy from your local machine:"
echo "   ./scripts/deploy.sh $ENV <this-server-ip>"
