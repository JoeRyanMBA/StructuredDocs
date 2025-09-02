#!/usr/bin/env bash
# dev.sh – start both API (Gunicorn) and Vite dev server with hot reload

# Exit on error
set -e

# Start backend API
echo "🚀 Starting Flask API on 8080..."
./start.sh &
API_PID=$!

echo "🌐 Waiting a few seconds for API to initialize..."
sleep 3

# Start frontend dev server
echo "✨ Starting Vite dev server on 5173..."
npm --prefix frontend run dev &
VITE_PID=$!

# Wait for both processes to exit
wait $API_PID $VITE_PID
