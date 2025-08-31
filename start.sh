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
        pip3 install --user -r backend/requirements.txt 2>/dev/null || pip3 install -r backend/requirements.txt 2>/dev/null || echo "⚠️ Failed to install Python dependencies"
    elif command -v pip &> /dev/null; then
        echo "📦 Installing Python dependencies with pip..."
        pip install --user -r backend/requirements.txt 2>/dev/null || pip install -r backend/requirements.txt 2>/dev/null || echo "⚠️ Failed to install Python dependencies"
    else
        echo "❌ Neither pip3 nor pip found, cannot install Python dependencies"
    fi
fi

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

# Final check for Python dependencies before starting
if python3 -c "import flask_sqlalchemy" 2>/dev/null; then
    echo "🌐 Starting gunicorn server..."
    exec gunicorn --bind 0.0.0.0:$PORT "backend.app:create_app()" --log-level info
else
    echo "❌ Critical: Python dependencies still not available. Cannot start application."
    echo "This might be due to the Node.js environment not supporting Python dependencies properly."
    echo "Consider switching to a Python environment on DigitalOcean App Platform."
    exit 1
fi
