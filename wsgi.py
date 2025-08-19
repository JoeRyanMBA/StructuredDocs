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
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Set up the Flask app
os.chdir(project_home)

# Import your Flask app
from backend.app import create_app

# Create the application instance
application = create_app()

if __name__ == "__main__":
    application.run()
