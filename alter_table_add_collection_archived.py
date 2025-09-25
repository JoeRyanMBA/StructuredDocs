"""One-off helper to add 'archived' column to collections if missing.

Usage: python alter_table_add_collection_archived.py
Safe to run multiple times.
"""
from backend.app import create_app
from backend.models import db
from sqlalchemy import text

app = create_app()
with app.app_context():
    inspector = db.inspect(db.engine)
    cols = [c['name'] for c in inspector.get_columns('collections')]
    if 'archived' not in cols:
        print("➕ Adding archived column to collections...")
        db.session.execute(text("ALTER TABLE collections ADD COLUMN archived BOOLEAN NOT NULL DEFAULT 0"))
        db.session.commit()
        print("✅ archived column added")
    else:
        print("ℹ️ archived column already exists; no action taken")