#!/usr/bin/python3

"""
WSGI configuration for StructuredDocs on PythonAnywhere
This content should be copied to: /var/www/structureddocs_joe-ryan_mba_wsgi.py
"""

import sys
import os

# Add your project directory to the sys.path
project_home = '/home/JoeRyanMBA/StructuredDocs'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Set the working directory
os.chdir(project_home)

# Set environment variables
os.environ['FRONTEND_URL'] = 'https://structureddocs.joe-ryan.mba'

# Import your Flask app - prefer backend.app (canonical app factory)
try:
    from backend.app import create_app
    application = create_app()
    print("✅ WSGI: Application created successfully from backend.app")
except Exception as e:
    print(f"❌ WSGI Error importing backend.app: {str(e)}")
    # Fallback to the monolithic app file
    try:
        from app_final_with_notifications_fix import create_app
        application = create_app()
        print("✅ WSGI: Application created successfully from app_final_with_notifications_fix (fallback)")
    except Exception as e2:
        print(f"❌ WSGI Fallback Error: {str(e2)}")
        import traceback
        traceback.print_exc()
        from flask import Flask, jsonify
        application = Flask(__name__)
        @application.route('/')
        def error_page():
            return jsonify({
                'error': 'Application failed to start',
                'details': f'Primary error: {str(e)}, Fallback error: {str(e2)}'
            }), 500

# For debugging - you can remove this once it's working
if __name__ == "__main__":
    application.run(debug=True)
