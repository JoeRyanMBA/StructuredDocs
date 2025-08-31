#!/bin/bash
# Startup script for DigitalOcean App Platform
# This script properly handles the PORT environment variable

# Set default port if not provided
PORT=${PORT:-8000}

echo "🚀 Starting StructuredDocs on port $PORT"
echo "Current working directory: $(pwd)"
echo "Python version: $(python3 --version 2>/dev/null || echo 'Python3 not found')"
echo "Pip version: $(pip3 --version 2>/dev/null || echo 'Pip3 not found')"

# Change to the app directory (this is crucial for container environments)
cd /workspace/StructuredDocs || cd /app || echo "⚠️  Could not change to app directory"

echo "Working directory after cd: $(pwd)"

# Check if Python dependencies are installed
echo "📦 Checking Python dependencies..."
if python3 -c "import flask_sqlalchemy, flask, sqlalchemy, psycopg2" 2>/dev/null; then
    echo "✅ Python dependencies already installed"
else
    echo "❌ Python dependencies not found, attempting to install..."
    echo "🔧 Updating package list..."
    apt-get update -qq
    
    echo "📦 Installing Python packages via apt-get..."
    apt-get install -y -qq python3-pip python3-dev build-essential python3-flask python3-sqlalchemy python3-psycopg2 python3-gunicorn 2>/dev/null || echo "⚠️ apt-get installation failed"
    
    echo "📦 Installing additional packages via pip3..."
    pip3 install --user flask flask-sqlalchemy sqlalchemy psycopg2-binary flask-cors flask-jwt-extended python-dotenv gunicorn email-validator pillow reportlab python-docx 2>/dev/null || pip3 install flask flask-sqlalchemy sqlalchemy psycopg2-binary flask-cors flask-jwt-extended python-dotenv gunicorn email-validator pillow reportlab python-docx 2>/dev/null || echo "⚠️ pip3 installation failed"
    
    # Final verification
    if python3 -c "import flask_sqlalchemy" 2>/dev/null; then
        echo "✅ Python dependencies installed successfully"
    else
        echo "❌ Python dependencies still not available after installation attempts"
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
if python3 -c "import flask_sqlalchemy, flask, sqlalchemy" 2>/dev/null; then
    echo "🌐 Starting gunicorn server..."
    exec gunicorn --bind 0.0.0.0:$PORT "backend.app:create_app()" --log-level info --timeout 120
else
    echo "❌ Critical: Python dependencies still not available. Cannot start application."
    echo "This might be due to the Node.js environment not supporting Python dependencies properly."
    echo "Consider switching to a Python environment on DigitalOcean App Platform."
    echo "Available Python packages:"
    python3 -c "import sys; print(sys.path)" 2>/dev/null || echo "Cannot check Python path"
    exit 1
fi
