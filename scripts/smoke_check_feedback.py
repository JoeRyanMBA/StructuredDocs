"""Simple smoke test to POST a feedback report to the running API.

Usage:
  python3 scripts/smoke_check_feedback.py https://your-host.example.com

It will POST a minimal feedback payload to /api/feedback and print the response.
"""
import sys
import json
import requests

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/smoke_check_feedback.py <base_url>")
        sys.exit(1)
    base = sys.argv[1].rstrip('/')
    url = f"{base}/api/feedback"
    payload = {
        "report_type": "suggestion",
        "page": "/test-page",
        "component": "smoke-test",
        "user_contact": "tester@example.com",
        "message": "Smoke test: creating feedback report",
        "metadata_json": "{\"env\": \"smoke\"}"
    }
    print('POST', url)
    try:
        r = requests.post(url, json=payload, timeout=10)
        print('Response status:', r.status_code)
        print('Response body:', r.text)
    except Exception as e:
        print('Request failed:', e)

if __name__ == '__main__':
    main()
