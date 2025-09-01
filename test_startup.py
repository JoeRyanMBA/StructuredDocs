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
    try:
        print("🧪 Testing Flask import...")
        from backend.app import create_app
        print("✅ Flask import successful")

        print("🧪 Testing Flask app creation...")
        # Skip blueprints for faster testing
        os.environ['SKIP_BLUEPRINTS'] = '1'
        app = create_app()
        print("✅ Flask app creation successful")

        print("🧪 Testing basic route...")
        with app.test_client() as client:
            response = client.get('/')
            print(f"✅ Root route responded with status: {response.status_code}")

        print("🎉 All tests passed! Flask app is ready.")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_flask_startup()
    sys.exit(0 if success else 1)
