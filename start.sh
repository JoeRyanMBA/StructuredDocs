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

# Check if Python dependencies are installed
echo "📦 Checking Python dependencies..."
if python3 -c "import flask_sqlalchemy" 2>/dev/null; then
    echo "✅ Python dependencies already installed"
else
    echo "❌ Python dependencies not found, attempting to install..."
    if command -v pip3 &> /dev/null; then
        echo "📦 Installing Python dependencies with pip3..."
        pip3 install --user -r backend/requirements.txt || echo "⚠️ Failed to install with pip3 --user, trying without --user..."
        pip3 install -r backend/requirements.txt || echo "⚠️ Failed to install Python dependencies"
    else
        echo "❌ pip3 not found, cannot install Python dependencies"
    fi
fi

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
