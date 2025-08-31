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

# Check if frontend is built
if [ -f "frontend/dist/index.html" ]; then
    echo "✅ Frontend build found"
else
    echo "❌ Frontend build not found - attempting to build..."
    if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
        cd frontend
        npm install
        npm run build
        cd ..
    fi
fi

# Start gunicorn with the correct port
echo "🌐 Starting gunicorn server..."
exec gunicorn --bind 0.0.0.0:$PORT "backend.app:create_app()" --log-level info
