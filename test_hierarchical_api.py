#!/usr/bin/env python3
"""
Test the hierarchical import functionality with the backend
"""

import requests
import json
import io
import os
import sys
import time
from typing import Optional, Dict, Any

BASE_URL = os.environ.get("STRUCTUREDDOCS_BASE_URL", "http://localhost:5000").rstrip('/')
DEFAULT_MD_PATH = os.environ.get("STRUCTUREDDOCS_IMPORT_FILE", "/workspaces/StructuredDocs/test_employee_handbook.md")
TIMEOUT = int(os.environ.get("STRUCTUREDDOCS_TIMEOUT", "25"))


def _ping(base_url: str) -> bool:
    try:
        r = requests.get(f"{base_url}/api/collections", timeout=5)
        return r.status_code == 200
    except Exception:
        return False


def _load_markdown(path: str) -> str:
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Markdown file not found: {path}")
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def _post_import(content: str, base_url: str) -> requests.Response:
    file_content = content.encode('utf-8')
    files = {'file': (os.path.basename(DEFAULT_MD_PATH), file_content, 'text/markdown')}
    data = {
        'source': 'markdown',
        'import_type': 'topics',
        'preserve_hierarchy': 'true'
    }
    return requests.post(f"{base_url}/api/import/upload", files=files, data=data, timeout=TIMEOUT)


def _fetch_collection(collection_id: int, base_url: str) -> Optional[Dict[str, Any]]:
    # There is no single collection GET endpoint; fetch all and filter
    try:
        resp = requests.get(f"{base_url}/api/collections", timeout=TIMEOUT)
        if resp.status_code != 200:
            return None
        cols = resp.json()
        for c in cols:
            if c.get('id') == collection_id:
                return c
    except Exception:
        return None
    return None


def _print_heading_stats(content: str):
    h1 = content.count('\n# ')
    # Count headings that start at beginning too
    if content.startswith('# '):
        h1 += 1
    h2 = content.count('\n## ')
    if content.startswith('## '):
        h2 += 1
    h3 = content.count('\n### ')
    if content.startswith('### '):
        h3 += 1
    print(f"Heading counts -> H1:{h1} H2:{h2} H3:{h3}")
    return h1, h2, h3


def test_hierarchical_import():
    """Pytest-compatible test; also works as a CLI script."""
    print(f"=== Hierarchical Import Test (BASE_URL={BASE_URL}) ===")
    if not _ping(BASE_URL):
        # For pytest, mark as skipped instead of failing hard
        msg = f"Backend not reachable at {BASE_URL}. Start server before running test."
        print(f"SKIP: {msg}")
        # If running under pytest, raise pytest.skip dynamically
        if 'PYTEST_CURRENT_TEST' in os.environ:
            try:
                import pytest  # type: ignore
                pytest.skip(msg)
            except Exception:
                pass
        return

    try:
        content = _load_markdown(DEFAULT_MD_PATH)
    except FileNotFoundError as e:
        print(f"❌ {e}")
        if 'PYTEST_CURRENT_TEST' in os.environ:
            raise
        return

    print(f"File: {DEFAULT_MD_PATH}")
    print(f"Size: {len(content)} chars")
    h1, h2, h3 = _print_heading_stats(content)
    theoretical_topic_floor = h1  # usually at least each H1 becomes a topic
    print(f"Expected minimum topics (heuristic): {theoretical_topic_floor}")

    start = time.time()
    try:
        response = _post_import(content, BASE_URL)
    except requests.exceptions.ConnectionError:
        print(f"❌ Lost connection while posting to {BASE_URL}")
        if 'PYTEST_CURRENT_TEST' in os.environ:
            raise
        return

    elapsed = (time.time() - start) * 1000
    print(f"Response status: {response.status_code}  ({elapsed:.1f} ms)")
    print(f"Response headers: {dict(response.headers)}")

    assert response.status_code in (200, 201), f"Unexpected status {response.status_code}: {response.text[:400]}"

    # Parse JSON
    try:
        result = response.json()
    except json.JSONDecodeError:
        raise AssertionError("Response was not valid JSON")

    print("Result JSON:")
    print(json.dumps(result, indent=2)[:4000])

    # Core assertions
    assert 'id' in result, 'Response missing collection id'
    collection_id = result['id']
    topics_count = result.get('topics_count')
    if topics_count is not None:
        print(f"Reported topics_count: {topics_count}")
        # Soft heuristic check (don't fail if mismatch, just warn)
        if topics_count < theoretical_topic_floor:
            print(f"⚠️  topics_count ({topics_count}) < heuristic floor ({theoretical_topic_floor})")

    # Verify collection exists in listings
    fetched = _fetch_collection(collection_id, BASE_URL)
    assert fetched is not None, f"Collection {collection_id} not found after import"
    print(f"✅ Collection {collection_id} present in /api/collections list")

    # Optional: verify name/message fields
    if 'message' in result:
        print(f"Message: {result['message']}")

    # Provide structured summary for CI parsing
    summary = {
        'collection_id': collection_id,
        'topics_count': topics_count,
        'h1': h1,
        'h2': h2,
        'h3': h3,
        'base_url': BASE_URL,
        'file': DEFAULT_MD_PATH
    }
    print("SUMMARY:")
    print(json.dumps(summary, indent=2))

    return summary

if __name__ == '__main__':
    try:
        test_hierarchical_import()
    except AssertionError as e:
        print(f"FAILED: {e}")
        sys.exit(1)