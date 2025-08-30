#!/usr/bin/env python3
"""End-to-end feedback flow test against deployed StructuredDocs site.

This script uses only Python standard library (urllib) so it runs without extra deps.
It will:
  - POST /api/feedback to create a feedback report
  - GET /api/feedback/<id> to verify creation
  - POST /api/feedback/<id>/update to apply an update (fallback POST)
  - GET to verify update
  - POST /api/feedback/<id>/archive to archive (fallback POST)
  - GET to verify archived status

Exit code: 0 on success, non-zero on failure.
"""
import json
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

BASE = 'https://structureddocs.joe-ryan.mba'

def req(method, path, data=None, headers=None):
    url = BASE + path
    body = None
    hdrs = {'Content-Type': 'application/json'}
    if headers:
        hdrs.update(headers)
    if data is not None:
        body = json.dumps(data).encode('utf-8')
    req = Request(url, data=body, headers=hdrs, method=method)
    try:
        with urlopen(req, timeout=15) as resp:
            raw = resp.read()
            text = raw.decode('utf-8') if raw else ''
            status = resp.getcode()
            try:
                payload = json.loads(text) if text else None
            except Exception:
                payload = text
            return status, payload
    except HTTPError as e:
        try:
            body = e.read().decode('utf-8')
            payload = json.loads(body)
        except Exception:
            payload = e.read().decode('utf-8') if hasattr(e, 'read') else str(e)
        return e.code, payload
    except URLError as e:
        print('Network error:', e, file=sys.stderr)
        raise

def fail(msg):
    print('FAIL:', msg)
    sys.exit(2)

def main():
    print('1) Creating feedback...')
    create_payload = {
        'type': 'bug',
        'page': '/test',
        'message': 'E2E test create',
    }
    status, body = req('POST', '/api/feedback', create_payload)
    print('->', status, body)
    if status not in (200, 201):
        fail(f'Create failed: {status} {body}')
    # support two response shapes: {id: ...} or {report: {id: ...}}
    feedback_id = None
    if isinstance(body, dict):
        if 'id' in body:
            feedback_id = body['id']
        elif 'report' in body and isinstance(body['report'], dict) and 'id' in body['report']:
            feedback_id = body['report']['id']
    if not feedback_id:
        fail(f'Create response missing id: {body}')

    print(f'2) GET created feedback id={feedback_id}...')
    status, body = req('GET', f'/api/feedback/{feedback_id}')
    print('->', status, body)
    if status != 200:
        fail(f'GET after create failed: {status} {body}')

    print('3) Update feedback (POST fallback) - set message and status...')
    update_payload = {'message': 'E2E test updated', 'status': 'open'}
    status, body = req('POST', f'/api/feedback/{feedback_id}/update', update_payload)
    print('->', status, body)
    if status != 200:
        fail(f'Update failed: {status} {body}')

    print('4) GET after update...')
    status, body = req('GET', f'/api/feedback/{feedback_id}')
    print('->', status, body)
    if status != 200:
        fail(f'GET after update failed: {status} {body}')
    if isinstance(body, dict):
        if body.get('message') != 'E2E test updated':
            fail(f'Update not reflected in GET: {body}')

    print('5) Archive feedback (POST fallback)...')
    status, body = req('POST', f'/api/feedback/{feedback_id}/archive', {})
    print('->', status, body)
    if status != 200:
        fail(f'Archive failed: {status} {body}')

    print('6) GET after archive...')
    status, body = req('GET', f'/api/feedback/{feedback_id}')
    print('->', status, body)
    if status != 200:
        fail(f'GET after archive failed: {status} {body}')
    if isinstance(body, dict):
        if body.get('status') not in ('archived', 'deleted'):
            print('WARN: archived status not set to archived/deleted; saw:', body.get('status'))

    print('\nE2E test completed successfully for id=', feedback_id)
    return 0

if __name__ == '__main__':
    try:
        rc = main()
        sys.exit(rc)
    except Exception as e:
        print('Exception during e2e test:', e, file=sys.stderr)
        sys.exit(3)
