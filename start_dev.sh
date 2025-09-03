#!/bin/bash
# Development startup script for StructuredDocs
# This script starts both frontend and backend in development mode

echo "🚀 Starting StructuredDocs Development Environment..."

# Function to handle cleanup on exit
cleanup() {
    echo "🛑 Shutting down development servers..."
    pkill -f "vite"
    pkill -f "start_backend.py"
    exit 0
}

# Trap signals for cleanup
trap cleanup SIGINT SIGTERM

# Start backend
echo "📡 Starting backend server..."
cd "$(dirname "$0")"
python3 start_backend.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "🖥️ Starting frontend development server..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo "✅ Development environment started!"
echo "   Backend:  http://localhost:5000"
echo "   Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for either process to exit
wait $BACKEND_PID $FRONTEND_PID