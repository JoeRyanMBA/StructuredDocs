#!/bin/bash
set -e
# Restart frontend (Vite) and backend (Flask) servers

# Make port 5050 public in Codespaces (if possible)
if [ -f ./make_port_5050_public.sh ]; then
  bash ./make_port_5050_public.sh
fi
echo "Stopping any running servers..."
# Only kill actual dev servers, not VS Code internals
pkill -f "flask run" 2>/dev/null || true
pkill -f "npm run dev" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true
sleep 1

echo "Activating Python virtual environment..."
source .venv/bin/activate

# Dynamically set URLs for Codespaces environment
if [ -n "$CODESPACE_NAME" ]; then
  echo "Codespaces environment detected. Setting public URLs."
  # Assumes the default domain for GitHub Codespaces
  GITHUB_HOST="app.github.dev"
  export FRONTEND_URL="https://$CODESPACE_NAME-5173.$GITHUB_HOST"
  export VITE_API_BASE_URL="https://$CODESPACE_NAME-5050.$GITHUB_HOST"
  echo "Frontend URL set to: $FRONTEND_URL"
  echo "API Base URL set to: $VITE_API_BASE_URL"
else
  echo "Local environment detected. Using localhost URLs."
  export FRONTEND_URL="http://localhost:5173"
  # For local dev, the API base can be relative
  export VITE_API_BASE_URL="" 
fi

echo "Starting backend (Flask)..."
export FLASK_APP=backend.app
# The FRONTEND_URL is now available to the Flask process
nohup flask run --host=0.0.0.0 --port=5050 > backend/nohup.out 2>&1 &

echo "Starting frontend (Vite)..."
cd frontend
# The VITE_API_BASE_URL is automatically picked up by Vite
nohup npm run dev > nohup.out 2>&1 &
cd ..

sleep 1

echo "Checking server status..."
# Check backend
if pgrep -f "flask run" > /dev/null; then
  echo "✅ Backend (Flask) is running."
else
  echo "❌ Backend (Flask) failed to start. Check backend/nohup.out."
fi
# Check frontend
if pgrep -f "vite" > /dev/null || pgrep -f "npm run dev" > /dev/null; then
  echo "✅ Frontend (Vite) is running."
else
  echo "❌ Frontend (Vite) failed to start. Check frontend/nohup.out."
fi

echo "Restart complete."
