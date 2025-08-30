#!/usr/bin/env python
"""
Startup script for DigitalOcean App Platform
Handles PORT environment variable properly for gunicorn
"""
import os
import sys

# Ensure PORT is set with a default value
port = os.environ.get('PORT', '8000')
os.environ['PORT'] = port

print(f"🚀 Starting StructuredDocs on port {port}")

# Import and create the Flask app
from backend.app import create_app
app = create_app()

if __name__ == '__main__':
    # For local testing
    app.run(host='0.0.0.0', port=int(port), debug=False)
