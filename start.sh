#!/bin/bash
# Startup script for DigitalOcean App Platform
# This script properly handles the PORT environment variable

# Set default port if not provided
PORT=${PORT:-8000}

echo "🚀 Starting StructuredDocs on port $PORT"
echo "Current working directory: $(pwd)"

# Change to the app directory (this is crucial for container environments)
cd /workspace/StructuredDocs || cd /app || echo "⚠️  Could not change to app directory"

echo "Working directory after cd: $(pwd)"

# Verify essential files exist
if [ -f "frontend/dist/index.html" ]; then
    echo "✅ frontend/dist/index.html found"
else
    echo "❌ frontend/dist/index.html NOT found - checking if we need to build..."
    if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
        echo "📦 Building frontend..."
        cd frontend
        npm install
        npm run build
        cd ..
    fi
fi

# Start gunicorn with the correct port
echo "🌐 Starting gunicorn server..."
exec gunicorn --bind 0.0.0.0:$PORT "backend.app:create_app()" --log-level info
