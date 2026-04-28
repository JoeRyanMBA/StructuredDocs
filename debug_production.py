#!/usr/bin/env python3
"""
Production Debug Script
Run this in the production container to diagnose issues
"""

import os
import sys
from pathlib import Path

def main():
    print("🔍 PRODUCTION DEBUG SCRIPT")
    print("=" * 50)

    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path[:3]}...")  # First 3 entries

    # Check environment variables
    print("\n📋 ENVIRONMENT VARIABLES:")
    important_vars = ['PORT', 'PYTHONPATH', 'PATH']
    for var in important_vars:
        value = os.environ.get(var, 'NOT SET')
        if var == 'PATH':
            value = value[:100] + '...' if len(value) > 100 else value
        print(f"  {var}: {value}")

    # Check file structure
    print("\n📁 FILE STRUCTURE:")
    current_files = os.listdir('.')
    print(f"  Files in current directory: {current_files[:10]}...")

    # Check for essential files
    essential_files = [
        '.enable_blueprints',
        'backend/app.py',
        'frontend/dist/index.html',
        'frontend/dist/favicon.ico',
        'requirements.txt'
    ]

    print("\n🔍 ESSENTIAL FILES:")
    for file_path in essential_files:
        exists = Path(file_path).exists()
        status = "✅" if exists else "❌"
        print(f"  {file_path}: {status}")

    # Try to import Flask app
    print("\n🚀 TESTING FLASK APP IMPORT:")
    try:
        from backend.app import create_app
        print("  ✅ Flask app import successful")

        app = create_app()
        print("  ✅ App creation successful")

        # Test basic routes
        with app.test_client() as client:
            response = client.get('/api/health')
            print(f"  Health endpoint: {response.status_code}")

            response = client.get('/')
            print(f"  Main page: {response.status_code}")

            response = client.get('/favicon.ico')
            print(f"  Favicon: {response.status_code}")

    except Exception as e:
        print(f"  ❌ Flask app error: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 50)
    print("🔍 DEBUG COMPLETE")

if __name__ == "__main__":
    main()
