#!/bin/bash
# Startup script for DigitalOcean App Platform
# This script properly handles the PORT environment variable

# Set default port if not provided
PORT=${PORT:-8000}

echo "🚀 Starting StructuredDocs on port $PORT"
echo "Current working directory: $(pwd)"
echo "Files in directory: $(ls -la | head -10)"
echo "Python path: $PYTHONPATH"
echo "PORT environment variable: $PORT"

# Change to the app directory (this is crucial for container environments)
cd /workspace/StructuredDocs || cd /app || echo "⚠️  Could not change to app directory"

echo "Working directory after cd: $(pwd)"
echo "Files in app directory: $(ls -la | head -10)"

# Verify essential files exist
if [ -f ".enable_blueprints" ]; then
    echo "✅ .enable_blueprints found"
else
    echo "❌ .enable_blueprints NOT found"
fi

if [ -f "frontend/dist/index.html" ]; then
    echo "✅ frontend/dist/index.html found"
else
    echo "❌ frontend/dist/index.html NOT found"
fi

if [ -f "frontend/dist/favicon.ico" ]; then
    echo "✅ frontend/dist/favicon.ico found"
else
    echo "❌ frontend/dist/favicon.ico NOT found"
fi

# Start gunicorn with the correct port
exec gunicorn --bind 0.0.0.0:$PORT "backend.app:create_app()" --log-level info
