#!/usr/bin/env python3
"""
Simple test script to verify Flask app can start up properly
"""
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_flask_startup():
    """Test basic Flask app startup"""
    print("🧪 Testing Flask import...")
    from backend.app import create_app
    print("✅ Flask import successful")

    # Ensure at least one blueprint loads; include variables so later tests have them
    if 'SKIP_BLUEPRINTS' in os.environ:
        os.environ.pop('SKIP_BLUEPRINTS', None)
    if 'ENABLE_BLUEPRINTS' not in os.environ:
        os.environ['ENABLE_BLUEPRINTS'] = 'users,variables'

    print("🧪 Testing Flask app creation...")
    app = create_app()
    print("✅ Flask app creation successful")

    print("🧪 Testing basic route...")
    with app.test_client() as client:
        response = client.get('/')
        assert response.status_code in (200, 302)
        print(f"✅ Root route responded with status: {response.status_code}")

    print("🎉 Flask startup test passed.")

if __name__ == '__main__':
    success = test_flask_startup()
    sys.exit(0 if success else 1)
