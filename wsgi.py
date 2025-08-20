#!/usr/bin/python3

"""
WSGI configuration for StructuredDocs on PythonAnywhere

This file is used by PythonAnywhere's web servers to serve your Flask application.
"""

import sys
import os

# Add your project directory to the sys.path
# Update this path to match your actual PythonAnywhere username and directory
project_home = '/home/JoeRyanMBA/StructuredDocs'  # Update this path if different
backend_path = os.path.join(project_home, 'backend')

if project_home not in sys.path:
    sys.path = [project_home] + sys.path
if backend_path not in sys.path:
    sys.path = [backend_path] + sys.path

# Set environment variable for PythonAnywhere
os.environ['PYTHONANYWHERE_ENVIRONMENT'] = '1'

# Set up the Flask app
os.chdir(project_home)

# Try to import and create application with error handling
try:
    # Import your Flask app
    from backend.app import create_app

    # Create the application instance
    application = create_app()
    print("✅ WSGI: Application created successfully")
    
except Exception as e:
    print(f"❌ WSGI Error: {str(e)}")
    import traceback
    traceback.print_exc()
    
    # Create a minimal error app
    from flask import Flask, jsonify
    application = Flask(__name__)
    
    @application.route('/')
    def error_page():
        return jsonify({
            'error': 'Application failed to start',
            'details': str(e)
        }), 500

if __name__ == "__main__":
    application.run()
