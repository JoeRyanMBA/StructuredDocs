#!/bin/bash
# Startup script for DigitalOcean App Platform
# This script properly handles the PORT environment variable

# Set default port if not provided
PORT=${PORT:-8000}

echo "🚀 Starting StructuredDocs on port $PORT"

# Start gunicorn with the correct port
exec gunicorn --bind 0.0.0.0:$PORT backend.app:create_app --log-level info
