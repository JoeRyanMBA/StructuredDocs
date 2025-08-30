#!/usr/bin/env python3
"""
Startup script for StructuredDocs backend.
This script properly sets up the Python path and runs the backend app.
"""
import os
import sys

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Set environment variables
os.environ['FLASK_APP'] = 'backend.app'
os.environ['FLASK_ENV'] = 'development'

# Change to project root directory  
os.chdir(project_root)

def main():
    print("🚀 Starting StructuredDocs Backend...")
    
    try:
        from backend.app import create_app
        app = create_app()
        
        # Create database tables
        with app.app_context():
            from backend.models import db
            try:
                db.create_all()
                print("✅ Database tables created successfully")
            except Exception as e:
                print(f"⚠️ Database setup warning: {e}")
        
        print("🌐 Starting Flask development server...")
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()