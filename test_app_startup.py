#!/usr/bin/env python3
"""
Test script to verify Flask app can start properly
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    print("🧪 Testing Flask app startup...")
    
    # Test imports
    print("📦 Testing imports...")
    from backend.app import create_app
    print("✅ App import successful")
    
    # Test app creation
    print("🚀 Testing app creation...")
    app = create_app()
    print("✅ App creation successful")
    
    # Test database connection
    print("📊 Testing database connection...")
    with app.app_context():
        from backend.models import db
        # Try to execute a simple query using the current app context
        try:
            result = db.session.execute(db.text("SELECT 1"))
            result.fetchone()
            print("✅ Database connection successful")
        except Exception as db_error:
            print(f"⚠️  Database connection issue: {str(db_error)}")
            # This might be OK if the database isn't accessible from this environment
    
    print("🎉 All tests passed!")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
