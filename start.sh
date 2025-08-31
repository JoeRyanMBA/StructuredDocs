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
if python3 -c "import flask_sqlalchemy, flask, sqlalchemy, psycopg2, flask_cors, flask_jwt_extended" 2>/dev/null; then
    echo "✅ Python dependencies already installed"
else
    echo "❌ Python dependencies not found, attempting to install..."
    echo "🔧 Attempting installation methods..."

    # Method 1: Try using pip3 directly (if available)
    if command -v pip3 &> /dev/null; then
        echo "📦 Method 1: Using pip3 directly..."
        pip3 install --user flask flask-sqlalchemy sqlalchemy psycopg2-binary flask-cors flask-jwt-extended python-dotenv gunicorn email-validator pillow reportlab python-docx 2>/dev/null && echo "✅ Method 1 successful" && INSTALL_SUCCESS=true
    fi

    # Method 2: Try using pip directly
    if [ "$INSTALL_SUCCESS" != "true" ] && command -v pip &> /dev/null; then
        echo "📦 Method 2: Using pip directly..."
        pip install --user flask flask-sqlalchemy sqlalchemy psycopg2-binary flask-cors flask-jwt-extended python-dotenv gunicorn email-validator pillow reportlab python-docx 2>/dev/null && echo "✅ Method 2 successful" && INSTALL_SUCCESS=true
    fi

    # Method 3: Try using apt-get to install system packages
    if [ "$INSTALL_SUCCESS" != "true" ] && command -v apt-get &> /dev/null; then
        echo "📦 Method 3: Using apt-get for system packages..."
        apt-get update -qq 2>/dev/null && apt-get install -y -qq python3-flask python3-sqlalchemy python3-psycopg2 python3-gunicorn 2>/dev/null && echo "✅ Method 3 successful" && INSTALL_SUCCESS=true
    fi

    # Method 4: Try downloading and installing pip if nothing else works
    if [ "$INSTALL_SUCCESS" != "true" ]; then
        echo "📦 Method 4: Installing pip manually..."
        curl -s https://bootstrap.pypa.io/get-pip.py | python3 2>/dev/null && pip3 install --user flask flask-sqlalchemy sqlalchemy psycopg2-binary flask-cors flask-jwt-extended python-dotenv gunicorn email-validator pillow reportlab python-docx 2>/dev/null && echo "✅ Method 4 successful" && INSTALL_SUCCESS=true
    fi

    # Final verification
    if [ "$INSTALL_SUCCESS" == "true" ] && python3 -c "import flask_sqlalchemy" 2>/dev/null; then
        echo "✅ Python dependencies installed successfully"
    else
        echo "❌ All installation methods failed"
        echo "⚠️  The application may not work correctly without Python dependencies"
        echo "💡 Consider switching to a Python runtime environment on DigitalOcean"
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
