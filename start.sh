#!/bin/bash

# Simple startup script for StructuredDocs
echo "🚀 Starting StructuredDocs..."

# Set environment variables
export PYTHONPATH="/app:$PYTHONPATH"

# Change to app directory
cd /app

# Start Gunicorn
exec python3 -m gunicorn \
    --bind 0.0.0.0:8080 \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    "backend.app:create_app()"
