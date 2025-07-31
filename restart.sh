#!/bin/bash
# Restart frontend (Vite) and backend (Flask) servers

# Kill any running frontend (Vite) and backend (Flask) processes
pkill -f "vite" 2>/dev/null
pkill -f "flask" 2>/dev/null
pkill -f "app.py" 2>/dev/null

# Start backend (Flask)
echo "Starting backend..."
cd backend
nohup flask run --host=0.0.0.0 --port=5000 &
cd ..

# Start frontend (Vite)
echo "Starting frontend..."
cd frontend
nohup npm run dev &
cd ..

echo "Frontend and backend restarted."
