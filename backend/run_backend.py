#!/usr/bin/env python3
import os
import sys

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Change to backend directory
os.chdir(backend_dir)

# Set environment variables
os.environ['FLASK_APP'] = 'app.py'
os.environ['FLASK_ENV'] = 'development'

# Import and run the app
from app import create_app

if __name__ == '__main__':
    print("🚀 Starting StructuredDocs Backend...")
    app = create_app()
    
    # Create database tables
    with app.app_context():
        from models import db
        try:
            db.create_all()
            print("✅ Database tables created successfully")
        except Exception as e:
            print(f"⚠️ Database setup warning: {e}")
    
    print("🌐 Starting Flask development server...")
    app.run(host='0.0.0.0', port=5000, debug=True)
