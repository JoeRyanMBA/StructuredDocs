#!/bin/bash
# Startup script for DigitalOcean App Platform
# This script properly handles the PORT environment variable

# Set default port if not provided
PORT=${PORT:-8000}

echo "🚀 Starting StructuredDocs on port $PORT"
echo "Current working directory: $(pwd)"
echo "Python version: $(python3 --version 2>/dev/null || echo 'Python3 not found')"
echo "Pip version: $(python3 -m pip --version 2>/dev/null || echo 'python -m pip not found')"

# Change to the repo directory (handle multiple possible roots in App Platform)
if [ -f "backend/app.py" ]; then
    echo "📁 Repo root detected: $(pwd)"
elif [ -d "/workspace" ]; then
    cd /workspace || true
    [ -f "backend/app.py" ] || [ -f "package.json" ] && echo "📁 Using /workspace as repo root"
elif [ -d "/app" ]; then
    cd /app || true
    [ -f "backend/app.py" ] || [ -f "package.json" ] && echo "📁 Using /app as repo root"
else
    echo "⚠️  Could not detect repo root; continuing in $(pwd)"
fi

echo "Working directory after cd: $(pwd)"

# Check/install Python dependencies using python -m pip with ensurepip fallback
echo "📦 Checking Python dependencies..."
if python3 - <<'PY'
import importlib
mods=["flask_sqlalchemy","flask","sqlalchemy","psycopg2","flask_cors","flask_jwt_extended"]
missing=[m for m in mods if importlib.util.find_spec(m) is None]
print("MISSING:"+",".join(missing))
PY
then :; fi

NEED_INSTALL=$(python3 - <<'PY'
import importlib
mods=["flask_sqlalchemy","flask","sqlalchemy","psycopg2","flask_cors","flask_jwt_extended"]
missing=[m for m in mods if importlib.util.find_spec(m) is None]
print("yes" if missing else "no")
PY
)

if [ "$NEED_INSTALL" = "yes" ]; then
    echo "❌ Python deps missing; installing via python -m pip..."
    python3 -m pip --version >/dev/null 2>&1 || python3 -m ensurepip --upgrade >/dev/null 2>&1 || curl -s https://bootstrap.pypa.io/get-pip.py | python3
    # Upgrade pip quietly, then install
    python3 -m pip install --upgrade pip >/dev/null 2>&1 || true
    python3 -m pip install --user \
        flask flask-sqlalchemy sqlalchemy psycopg2-binary flask-cors flask-jwt-extended \
        python-dotenv gunicorn email-validator pillow reportlab python-docx >/dev/null 2>&1 || true
fi

# Verify installation
if python3 -c "import flask_sqlalchemy" 2>/dev/null; then
    echo "✅ Python dependencies ready"
else
    echo "⚠️ Python dependencies still missing; app may fail to start"
fi

# Run DB migrations (best-effort) before starting app
if [ -f "run_migrations_production.py" ]; then
    echo "�️ Running database migrations (best-effort)..."
    python3 run_migrations_production.py || echo "⚠️ Migrations failed or skipped"
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
