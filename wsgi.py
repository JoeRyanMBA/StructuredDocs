#!/usr/bin/python3.13

"""
WSGI configuration for StructuredDocs on PythonAnywhere.
This file is used by PythonAnywhere's web servers to serve your Flask app.
"""

import os
import sys

# Add your project directory to sys.path
project_home = '/home/JoeRyanMBA/StructuredDocs'
backend_path = os.path.join(project_home, 'backend')

if project_home not in sys.path:
    sys.path.insert(0, project_home)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Mark PA environment (optional) and ensure CWD is the project root
os.environ['PYTHONANYWHERE_ENVIRONMENT'] = '1'
os.chdir(project_home)

try:
    from backend.app import application
    print("✅ WSGI: Application imported successfully from backend.app")
except Exception as e:
    # Errors printed here go to the PythonAnywhere error log
    print(f"❌ WSGI Error: {e}")
    import traceback
    traceback.print_exc()

    from flask import Flask, jsonify
    application = Flask(__name__)

    @application.route('/')
    def error_page():
        return jsonify({'error': 'Application failed to start', 'details': str(e)}), 500
