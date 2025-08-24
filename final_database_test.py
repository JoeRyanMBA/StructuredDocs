#!/usr/bin/env python3
"""
DB smoke test (pytest-friendly). Skips when psycopg2 or the DB host are unavailable.
"""
import pytest
import socket

PG_CONFIG = {
    'host': 'JoeRyanMBA-4757.postgres.pythonanywhere-services.com',
    'port': 14757,
    'database': 'structured_docs',
    'user': 'super',
    'password': 'Picklehead1!'
}


def test_db_smoke_connect_and_simple_query():
    try:
        import psycopg2
    except Exception:
        pytest.skip("psycopg2 not installed; skipping DB integration test")

    # quick reachability check
    try:
        socket.create_connection((PG_CONFIG['host'], PG_CONFIG['port']), timeout=2).close()
    except Exception:
        pytest.skip("Postgres host unreachable; skipping DB integration test")

    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT 1")
    assert cur.fetchone()[0] == 1
    conn.close()

