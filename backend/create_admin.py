"""
Idempotent admin seeding script.

Usage examples:
  python backend/create_admin.py --email admin@example.com --password 'StrongPass123'
  ADMIN_EMAIL=admin@example.com ADMIN_PASSWORD='StrongPass123' python backend/create_admin.py

Notes:
- Run from the repo root or any dir; this script adjusts sys.path to import backend.*
- Assumes DB schema is created via migrations; it won't call create_all by default.
"""

import argparse
import os
import sys

# Ensure project root on sys.path so `from backend...` works regardless of CWD
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app import create_app
from backend.extensions import db
from backend.models import User
from werkzeug.security import generate_password_hash
from sqlalchemy import func


def create_admin_user(email: str, password: str, name: str = "Admin User") -> None:
    app = create_app()
    with app.app_context():
        # Normalize email
        email_norm = (email or '').strip().lower()
        # Look up existing user
        user = User.query.filter(func.lower(User.email) == email_norm).first()
        if user:
            changed = False
            # Normalize stored email if needed
            if user.email != email_norm:
                user.email = email_norm
                changed = True
            if user.role != 'admin':
                user.role = 'admin'
                changed = True
            if password:
                user.password_hash = generate_password_hash(password)
                changed = True
            if changed:
                db.session.commit()
                print(f"✅ Updated existing user '{email_norm}' as admin and set password.")
            else:
                print(f"✅ Admin user '{email_norm}' already exists; no changes needed.")
            return

        # Create new admin
        user = User(
            name=name,
            email=email_norm,
            password_hash=generate_password_hash(password) if password else None,
            role='admin',
            active=True,
        )
        db.session.add(user)
        db.session.commit()
        print(f"✅ Created admin user '{email_norm}'.")


def main():
    parser = argparse.ArgumentParser(description="Create or update an admin user.")
    parser.add_argument("--email", default=os.getenv("ADMIN_EMAIL", "admin@example.com"))
    parser.add_argument("--password", default=os.getenv("ADMIN_PASSWORD", "password"))
    parser.add_argument("--name", default=os.getenv("ADMIN_NAME", "Admin User"))
    args = parser.parse_args()

    # Basic validation
    if not args.email:
        raise SystemExit("--email is required")
    if not args.password:
        print("⚠️  Empty password provided; user will have no password set.")

    create_admin_user(args.email, args.password, args.name)


if __name__ == "__main__":
    main()
