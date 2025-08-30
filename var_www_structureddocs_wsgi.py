#!/usr/bin/python3

# This file contains the WSGI configuration required to serve up your
# web application at http://structureddocs.joe-ryan.mba/
# It works by setting the variable 'application' to a WSGI handler of some
# description.

import sys
import os

# The path to your project's directory.
project_home = '/home/JoeRyanMBA/StructuredDocs'

# Add the project directory to the sys.path.
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set the working directory.
os.chdir(project_home)

# Import the Flask app factory from your backend code
# and create the application object.
from backend.app import create_app
application = create_app()
