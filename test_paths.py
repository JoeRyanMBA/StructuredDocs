#!/usr/bin/env python3

import os
import sys
sys.path.insert(0, '/workspaces/StructuredDocs/backend')

from flask import Flask
from models import db, Publication
from routes.publications import generate_pdf

def test_path_construction():
    """Test path construction in the actual app context"""
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////workspaces/StructuredDocs/instance/structured_docs.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    with app.app_context():
        pub = Publication.query.first()
        if not pub:
            print("No publications found")
            return
            
        print(f'Working directory: {os.getcwd()}')
        print(f'Script location: {os.path.dirname(os.path.abspath(__file__))}')
        
        # Test the path construction used in the routes/publications.py code
        routes_file = '/workspaces/StructuredDocs/backend/routes/publications.py'
        routes_dir = os.path.dirname(routes_file)
        default_bg_path = os.path.join(routes_dir, 'static', 'backgrounds', 'SC Cover Background.png')
        print(f'Default background path (from routes): {default_bg_path}')
        print(f'Exists: {os.path.exists(default_bg_path)}')
        
        # Test the actual backend static path
        backend_static_path = os.path.join('/workspaces/StructuredDocs/backend', 'static', 'backgrounds', 'SC Cover Background.png')
        print(f'Backend static path: {backend_static_path}')
        print(f'Exists: {os.path.exists(backend_static_path)}')

if __name__ == "__main__":
    test_path_construction()
