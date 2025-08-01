#!/bin/bash
set -e
# Restart frontend (Vite) and backend (Flask) servers

echo "Stopping any running servers..."
# Only kill actual dev servers, not VS Code internals
pkill -f "flask run" 2>/dev/null || true
pkill -f "npm run dev" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true
sleep 1

echo "Activating Python virtual environment..."
source .venv/bin/activate

echo "Starting backend (Flask)..."
export FLASK_APP=backend.app
nohup flask run --host=0.0.0.0 --port=5050 > backend/nohup.out 2>&1 &

echo "Starting frontend (Vite)..."
cd frontend
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
