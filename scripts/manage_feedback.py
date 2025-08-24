#!/usr/bin/env python3
"""
Manage feedback reports: list and remove smoke-test rows.

Usage examples:
  python3 scripts/manage_feedback.py --list --count 10
  python3 scripts/manage_feedback.py --delete-smoke --yes

This script is safe by default: destructive actions require --yes.
"""
import os
import sys
import argparse

# Ensure project root is importable so top-level 'models' resolves correctly
sys.path.insert(0, os.path.abspath('.'))

# If running on PythonAnywhere, set the environment variable so the app uses Postgres
os.environ.setdefault('PYTHONANYWHERE_ENVIRONMENT', os.environ.get('PYTHONANYWHERE_ENVIRONMENT', ''))

def create_and_get_app():
    # Import here so the module-level side-effects in backend.app run with the correct env
    from backend.app import create_app
    return create_app()

def list_latest(n=10):
    app = create_and_get_app()
    with app.app_context():
        try:
            from models import FeedbackReport
            rows = FeedbackReport.query.order_by(FeedbackReport.id.desc()).limit(n).all()
            if not rows:
                print('No feedback rows found')
                return
            for r in rows:
                print(r.to_dict())
        except Exception as e:
            print('Failed to list feedback rows:', e)

def delete_smoke_tests(confirm=False):
    if not confirm:
        print('Refusing to delete without --yes')
        return
    app = create_and_get_app()
    with app.app_context():
        try:
            from models import FeedbackReport, db
            q = FeedbackReport.query.filter(
                FeedbackReport.page == '/smoke-test',
                FeedbackReport.component == 'smoke'
            )
            matches = q.all()
            if not matches:
                print('No matching smoke-test rows found.')
                return
            print(f'Deleting {len(matches)} rows:')
            for r in matches:
                print(r.to_dict())
            for r in matches:
                db.session.delete(r)
            db.session.commit()
            print('Deleted.')
        except Exception as e:
            print('Failed to delete smoke-test rows:', e)

def main():
    parser = argparse.ArgumentParser(description='Manage feedback reports')
    parser.add_argument('--list', action='store_true', help='List recent feedback rows')
    parser.add_argument('--count', type=int, default=10, help='Number of rows to list')
    parser.add_argument('--delete-smoke', action='store_true', help='Delete smoke-test feedback rows')
    parser.add_argument('--yes', action='store_true', help='Confirm destructive actions')
    args = parser.parse_args()

    if args.list:
        list_latest(args.count)
    elif args.delete_smoke:
        delete_smoke_tests(confirm=args.yes)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
