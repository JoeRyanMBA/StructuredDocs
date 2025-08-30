#!/usr/bin/env python3
"""
Simple diagnostic: create Flask app and fetch /api/dashboard/stats via test client.
Run: python3 scripts/check_dashboard_stats.py
"""
import json
import sys

# Ensure we can import the backend app
try:
    from backend.app import create_app
except Exception as e:
    print('ERROR: Failed to import create_app from backend.app:', e)
    sys.exit(2)

app = create_app()
with app.test_client() as client:
    try:
        resp = client.get('/api/dashboard/stats')
        print('Status:', resp.status_code)
        try:
            data = resp.get_json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except Exception:
            print('Response text:', resp.get_data(as_text=True))
    except Exception as e:
        print('ERROR during request:', e)
        sys.exit(3)
