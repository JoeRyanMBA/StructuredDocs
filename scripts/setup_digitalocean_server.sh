#!/bin/bash
# Setup script for Digital Ocean server - run this on your droplet
# Usage: bash setup_digitalocean_server.sh

set -euo pipefail

echo "🚀 Setting up StructuredDocs on Digital Ocean"
echo "=============================================="

# Install Docker
echo "📦 Installing Docker..."
apt-get update
apt-get install -y docker.io
systemctl start docker
systemctl enable docker

echo "✅ Docker installed"
docker --version

# Install Docker Compose plugin
echo "📦 Installing Docker Compose..."
apt-get install -y docker-compose-plugin

echo "✅ Docker Compose installed"
docker compose version

# Create application directory
echo "📁 Creating application directories..."
REMOTE_DIR="/opt/structureddocs"
mkdir -p "$REMOTE_DIR"
mkdir -p "$REMOTE_DIR/data/images"
mkdir -p "$REMOTE_DIR/instance"
chmod 755 "$REMOTE_DIR/data/images"
chmod 755 "$REMOTE_DIR/instance"

echo "✅ Directories created:"
echo "   - $REMOTE_DIR"
echo "   - $REMOTE_DIR/data/images (for uploaded images)"
echo "   - $REMOTE_DIR/instance (for database)"

# Create .enable_blueprints file
echo "📝 Creating .enable_blueprints configuration..."
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

echo "✅ Blueprints configuration created"

# Create backend.env template
echo "📝 Creating backend.env template..."
cat > "$REMOTE_DIR/backend.env.template" <<'ENVTEMPLATE'
# Required environment variables for StructuredDocs
PORT=8080
DATABASE_URL=sqlite:///instance/structured_docs.db
ENABLE_BLUEPRINTS_FILE=.enable_blueprints
SECRET_KEY=CHANGE_THIS_TO_A_RANDOM_SECRET_KEY

# Email configuration (optional)
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=your_sendgrid_api_key_here
DEFAULT_FROM_EMAIL=no-reply@structureddocs.online
FROM_EMAIL=
FROM_NAME=StructuredDocs
SENDGRID_VERIFIED_SENDER=
FRONTEND_URL=https://structureddocs.online
ADMIN_API_KEY=your_admin_api_key_here
ENVTEMPLATE

echo "✅ Environment template created at $REMOTE_DIR/backend.env.template"
echo ""
echo "⚠️  IMPORTANT: Edit $REMOTE_DIR/backend.env and set your actual values"
echo "   cp $REMOTE_DIR/backend.env.template $REMOTE_DIR/backend.env"
echo "   nano $REMOTE_DIR/backend.env"

# Create docker-compose.yml
echo "📝 Creating docker-compose.yml..."
cat > "$REMOTE_DIR/docker-compose.yml" <<'COMPOSE'
version: '3.8'

services:
  app:
    image: structureddocs-backend:latest
    container_name: structureddocs_app
    environment:
      - PORT=8080
      - DATABASE_URL=sqlite:///instance/structured_docs.db
      - ENABLE_BLUEPRINTS_FILE=.enable_blueprints
      - EMAIL_PROVIDER=${EMAIL_PROVIDER:-sendgrid}
      - SENDGRID_API_KEY=${SENDGRID_API_KEY}
      - DEFAULT_FROM_EMAIL=${DEFAULT_FROM_EMAIL:-no-reply@structureddocs.online}
      - FROM_EMAIL=${FROM_EMAIL:-}
      - FROM_NAME=${FROM_NAME:-StructuredDocs}
      - SENDGRID_VERIFIED_SENDER=${SENDGRID_VERIFIED_SENDER:-}
      - FRONTEND_URL=${FRONTEND_URL:-https://structureddocs.online}
      - ADMIN_API_KEY=${ADMIN_API_KEY:-}
      - SECRET_KEY=${SECRET_KEY}
    ports:
      - "8080:8080"
    restart: unless-stopped
    volumes:
      # Mount .enable_blueprints from host
      - ./.enable_blueprints:/app/.enable_blueprints:ro
      # Persist SQLite DB
      - ./instance:/app/instance
      # Persist uploaded images
      - ./data/images:/app/backend/static/images
    env_file:
      - backend.env
    command: ["./start.sh"]
COMPOSE

echo "✅ docker-compose.yml created"
echo ""
echo "🎉 Server setup complete!"
echo ""
echo "Next steps:"
echo "1. Copy your backend.env.template to backend.env and edit it:"
echo "   cd $REMOTE_DIR"
echo "   cp backend.env.template backend.env"
echo "   nano backend.env"
echo ""
echo "2. Deploy your Docker image using the updated deployment script"
echo "   ./scripts/deploy_digitalocean_fixed.sh"
echo ""
echo "3. Your images will persist in: $REMOTE_DIR/data/images"
echo "4. Your database will persist in: $REMOTE_DIR/instance"
