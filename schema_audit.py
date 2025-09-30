#!/usr/bin/env python3
"""Lightweight schema audit utility.
Run inside the deployment environment (with app context) to list drift between models and DB.
"""
from __future__ import annotations
import sys, os

sys.path.insert(0, '/workspaces/StructuredDocs')
sys.path.insert(0, '/workspaces/StructuredDocs/backend')

os.environ.setdefault('ENABLE_BLUEPRINTS', 'users,topics,projects,publications,links,notifications,reviews,import,organize,publish')

from backend.app import create_app  # type: ignore
from backend.extensions import db  # type: ignore

EXPECTED_TABLE_COLUMNS = {
    'projects': {'id','name','description','status','start_date','target_completion','created_at','updated_at','archived'},
    'collections': {'id','name','description','form_number','parent_id','project_id','position','created_at','updated_at','archived'},
}

def main():
    app = create_app()
    with app.app_context():
        insp = db.inspect(db.engine)
        print('🔍 Schema Audit Report')
        overall_ok = True
        for table, expected in EXPECTED_TABLE_COLUMNS.items():
            if table not in insp.get_table_names():
                print(f'❌ Missing table: {table}')
                overall_ok = False
                continue
            existing = {c['name'] for c in insp.get_columns(table)}
            missing = expected - existing
            unexpected = existing - expected
            if not missing:
                print(f'✅ {table}: all expected columns present ({len(expected)})')
            else:
                print(f'⚠️ {table}: missing columns -> {sorted(missing)}')
                overall_ok = False
            if unexpected:
                print(f'   ℹ️ {table}: extra columns present (not in EXPECTED set): {sorted(unexpected)}')
        print('\nResult: ' + ('✅ PASSED' if overall_ok else '⚠️ DRIFT DETECTED'))
        return 0 if overall_ok else 1

if __name__ == '__main__':
    raise SystemExit(main())
