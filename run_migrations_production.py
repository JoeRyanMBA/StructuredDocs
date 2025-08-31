#!/usr/bin/env python3
"""
Production Database Migration Script
Run this to initialize the database schema in production
"""

import sys
import os
import subprocess

# Add project paths
sys.path.insert(0, '/workspaces/StructuredDocs')
sys.path.insert(0, '/workspaces/StructuredDocs/backend')

# Set environment variables to avoid emergency mode
os.environ['ENABLE_BLUEPRINTS'] = 'users,topics,projects,publications,links,notifications,reviews,import,organize,publish'

def install_dependencies():
    """Install Python dependencies if they're missing"""
    print("📦 Checking Python dependencies...")

    try:
        import flask_sqlalchemy
        print("✅ Python dependencies already available")
        return True
    except ImportError:
        print("❌ Python dependencies not found, attempting to install...")

        # Try multiple installation methods
        methods = [
            ["pip3", "install", "--user", "flask", "flask-sqlalchemy", "sqlalchemy", "psycopg2-binary", "flask-cors", "flask-jwt-extended", "python-dotenv", "gunicorn", "email-validator", "pillow", "reportlab", "python-docx"],
            ["pip", "install", "--user", "flask", "flask-sqlalchemy", "sqlalchemy", "psycopg2-binary", "flask-cors", "flask-jwt-extended", "python-dotenv", "gunicorn", "email-validator", "pillow", "reportlab", "python-docx"],
            ["apt-get", "update", "&&", "apt-get", "install", "-y", "python3-flask", "python3-sqlalchemy", "python3-psycopg2", "python3-gunicorn"]
        ]

        for i, method in enumerate(methods, 1):
            print(f"📦 Method {i}: Trying {' '.join(method[:3])}...")
            try:
                if "apt-get" in method[0]:
                    # For apt-get, run as separate commands
                    subprocess.run(["apt-get", "update"], check=True, capture_output=True)
                    subprocess.run(["apt-get", "install", "-y", "python3-flask", "python3-sqlalchemy", "python3-psycopg2", "python3-gunicorn"], check=True, capture_output=True)
                else:
                    subprocess.run(method, check=True, capture_output=True)

                # Verify installation
                import flask_sqlalchemy
                print(f"✅ Method {i} successful")
                return True
            except (subprocess.CalledProcessError, ImportError) as e:
                print(f"⚠️ Method {i} failed: {e}")
                continue

        print("❌ All installation methods failed")
        return False

# Try to install dependencies before importing
if not install_dependencies():
    print("❌ Cannot proceed without Python dependencies")
    sys.exit(1)

# Now safe to import
from backend.app import create_app

def run_migrations():
    app = create_app()
    
    with app.app_context():
        from backend.extensions import db, migrate
        from flask_migrate import upgrade
        
        print("🗄️ Running database migrations...")
        
        try:
            # First create all tables (in case migrations haven't been run)
            db.create_all()
            print("✅ Database tables created")
            
            # Set the correct migrations directory path
            import os
            migrations_dir = os.path.join(os.path.dirname(__file__), 'backend', 'migrations')
            
            # Check if migrations directory exists and has versions
            if os.path.exists(migrations_dir):
                versions_dir = os.path.join(migrations_dir, 'versions')
                if os.path.exists(versions_dir) and os.listdir(versions_dir):
                    print(f"📁 Found migrations in: {migrations_dir}")
                    # Try to run migrations
                    try:
                        upgrade(directory=migrations_dir)
                        print("✅ Database migrations completed")
                    except Exception as mig_e:
                        print(f"⚠️ Migration issue (may be already up to date): {mig_e}")
                else:
                    print("⚠️ No migration versions found - using db.create_all() only")
            else:
                print("⚠️ Migrations directory not found - using db.create_all() only")
            
            # Try to create admin user
            from backend.models import User
            from werkzeug.security import generate_password_hash
            from sqlalchemy import func
            
            admin_email = 'admin@example.com'
            admin_password = 'Admin123!'
            
            existing_admin = User.query.filter(func.lower(User.email) == admin_email.lower()).first()
            if not existing_admin:
                admin_user = User(
                    name='Admin User',
                    email=admin_email,
                    password_hash=generate_password_hash(admin_password),
                    role='admin',
                    active=True
                )
                db.session.add(admin_user)
                db.session.commit()
                print(f"✅ Created admin user: {admin_email}")
            else:
                print(f"✅ Admin user already exists: {admin_email}")
                
        except Exception as e:
            print(f"❌ Migration error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1)
