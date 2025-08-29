"""Smoke test for /api/feedback using stdlib only.

Usage:
  source .venv/bin/activate  # optional
  python scripts/smoke_feedback_urllib.py https://host:port
"""
import json
import sys
import urllib.request

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/smoke_feedback_urllib.py <base_url>")
        sys.exit(1)
    base = sys.argv[1].rstrip('/')
    url = f"{base}/api/feedback"
    payload = {
        "type": "bug",
        "page": "/smoke",
        "message": "Smoke test: bug via urllib",
        "contact": "smoke@example.com",
        "metadata": {"client": "urllib"}
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        print("POST status:", resp.status)
        body = resp.read().decode('utf-8')
        print("POST body:", body[:300])
    with urllib.request.urlopen(url, timeout=10) as resp:
        print("LIST status:", resp.status)
        body = resp.read().decode('utf-8')
        print("LIST body sample:", body[:600])

if __name__ == "__main__":
    main()
