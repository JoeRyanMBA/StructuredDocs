#!/usr/bin/env python3
"""
Production Database Migration Script
Run this to initialize the database schema in production
"""

import sys
import os
import subprocess
import shutil

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

        # Prefer using `python -m pip` to avoid missing pip binaries
        def python_pip_install(args: list[str]) -> bool:
            try:
                # Check if pip module is available
                pip_check = subprocess.run([sys.executable, "-m", "pip", "--version"], capture_output=True)
                if pip_check.returncode != 0:
                    # Bootstrap pip via ensurepip, then fallback to get-pip.py
                    print("🛠️ Bootstrapping pip with ensurepip...")
                    ep = subprocess.run([sys.executable, "-m", "ensurepip", "--upgrade"], capture_output=True)
                    if ep.returncode != 0:
                        print(f"⚠️ ensurepip failed: {ep.stderr.decode(errors='ignore')[:200]}")
                        # Fallback: download and run get-pip.py
                        try:
                            print("🛠️ Falling back to get-pip.py bootstrap...")
                            import tempfile, urllib.request
                            with tempfile.TemporaryDirectory() as td:
                                gp = os.path.join(td, "get-pip.py")
                                url = "https://bootstrap.pypa.io/get-pip.py"
                                with urllib.request.urlopen(url, timeout=30) as r, open(gp, "wb") as f:
                                    f.write(r.read())
                                gp_proc = subprocess.run([sys.executable, gp], capture_output=True)
                                if gp_proc.returncode != 0:
                                    print(f"⚠️ get-pip.py failed: {gp_proc.stderr.decode(errors='ignore')[:200]}")
                                    return False
                        except Exception as ge:
                            print(f"⚠️ get-pip bootstrap exception: {ge}")
                            return False

                # Try upgrading pip quietly (best-effort)
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], capture_output=True)
                except Exception:
                    pass

                print("📦 Installing packages via python -m pip --user ...")
                proc = subprocess.run([sys.executable, "-m", "pip", "install", "--user", *args], capture_output=True)
                if proc.returncode == 0:
                    return True
                print(f"⚠️ pip install failed: {proc.stderr.decode(errors='ignore')[:200]}")
                return False
            except Exception as e:
                print(f"⚠️ pip install exception: {e}")
                return False

        packages = [
            "flask",
            "flask-sqlalchemy",
            "sqlalchemy",
            "psycopg2-binary",
            "flask-cors",
            "flask-jwt-extended",
            "flask-migrate",
            "python-dotenv",
            "gunicorn",
            "email-validator",
            "pillow",
            "reportlab",
            "python-docx",
        ]

        if python_pip_install(packages):
            try:
                # Add user site-packages to path if needed
                import site
                site.addsitedir(site.getusersitepackages())
                import flask_sqlalchemy  # noqa: F401
                print("✅ Dependencies installed successfully")
                return True
            except ImportError as e:
                print(f"⚠️ Verification failed after install: {e}")

        # Last resort: try pip/pip3 binaries if present
        for bin_name in ("pip3", "pip"):
            if shutil.which(bin_name):
                print(f"📦 Trying fallback binary: {bin_name} ...")
                try:
                    proc = subprocess.run([bin_name, "install", "--user", *packages], capture_output=True)
                    if proc.returncode == 0:
                        import flask_sqlalchemy  # noqa: F401
                        print("✅ Fallback binary install successful")
                        return True
                    print(f"⚠️ {bin_name} failed: {proc.stderr.decode(errors='ignore')[:200]}")
                except Exception as e:
                    print(f"⚠️ {bin_name} exception: {e}")

        print("❌ All installation methods failed")
        return False

# Try to install dependencies before importing
if not install_dependencies():
    print("❌ Cannot proceed without Python dependencies")
    sys.exit(1)

# Now safe to import - do this inside the function to avoid module-level import
def run_migrations():
    # Import here, after dependencies are guaranteed to be installed
    from backend.app import create_app
    
    app = create_app()
    
    with app.app_context():
        from backend.extensions import db, migrate
        from flask_migrate import upgrade
        
        print("🗄️ Running database migrations...")
        
        try:
            # Only run db.create_all() if this looks like a fresh database (avoid masking drift)
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            if not existing_tables:
                print("📭 No tables detected – initializing with db.create_all() before migrations...")
                db.create_all()
                print("✅ Base tables created via create_all()")
            else:
                print(f"ℹ️ Detected {len(existing_tables)} existing tables – skipping create_all() to preserve migration integrity")
            
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
            
            # Schema drift audit & hot-fix section
            print("🔍 Auditing schema for expected columns (hot-fix path)...")
            inspector = db.inspect(db.engine)

            drift_issues = []

            def ensure_boolean_column(table: str, column: str, default_sql: str = 'FALSE'):
                cols = [c['name'] for c in inspector.get_columns(table)]
                if column not in cols:
                    print(f"➕ Adding missing column {table}.{column} ...")
                    db.session.execute(db.text(f"ALTER TABLE {table} ADD COLUMN {column} BOOLEAN NOT NULL DEFAULT {default_sql}"))
                    db.session.commit()
                    print(f"✅ Added column {table}.{column}")
                    return True
                return False

            def ensure_varchar_column(table: str, column: str, length: int = 100):
                cols = [c['name'] for c in inspector.get_columns(table)]
                if column not in cols:
                    print(f"➕ Adding missing column {table}.{column} ...")
                    db.session.execute(db.text(f"ALTER TABLE {table} ADD COLUMN {column} VARCHAR({length})"))
                    db.session.commit()
                    print(f"✅ Added column {table}.{column}")
                    return True
                return False

            def ensure_table(table: str, create_sql: str, create_sql_sqlite: str = None):
                existing = inspector.get_table_names()
                if table not in existing:
                    print(f"➕ Creating missing table '{table}' ...")
                    dialect = db.engine.dialect.name
                    sql = (create_sql_sqlite if create_sql_sqlite and dialect == 'sqlite' else create_sql)
                    db.session.execute(db.text(sql))
                    db.session.commit()
                    # Refresh inspector after DDL
                    inspector.__init__(db.engine)
                    print(f"✅ Created table '{table}'")
                    return True
                return False

            # Ensure snippets table exists
            ensure_table(
                'snippets',
                """CREATE TABLE snippets (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(200) NOT NULL,
                    content TEXT,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
                )""",
                """CREATE TABLE snippets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title VARCHAR(200) NOT NULL,
                    content TEXT,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )"""
            )

            def ensure_nullable_column(table: str, column: str, col_type: str = 'TIMESTAMP'):
                cols = [c['name'] for c in inspector.get_columns(table)]
                if column not in cols:
                    print(f"➕ Adding missing column {table}.{column} ...")
                    db.session.execute(db.text(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"))
                    db.session.commit()
                    print(f"✅ Added column {table}.{column}")
                    return True
                return False

            # Expected boolean columns we defensively backfill if missing
            added_collections_archived = ensure_boolean_column('collections', 'archived', 'FALSE')
            added_projects_archived = ensure_boolean_column('projects', 'archived', 'FALSE')
            added_publications_form_number = ensure_varchar_column('publications', 'form_number', 100)
            # users.last_seen — critical: missing column causes login 500
            added_users_last_seen = ensure_nullable_column('users', 'last_seen', 'TIMESTAMP')
            # review token activity tracking
            added_rt_last_accessed = ensure_nullable_column('review_tokens', 'last_accessed_at', 'TIMESTAMP')
            added_rbt_last_accessed = ensure_nullable_column('review_batch_tokens', 'last_accessed_at', 'TIMESTAMP')

            # Summarize drift outcome
            if not (added_collections_archived or added_projects_archived or added_publications_form_number or added_users_last_seen or added_rt_last_accessed or added_rbt_last_accessed):
                print("✅ No hot-fix column additions required")
            else:
                print("ℹ️ One or more columns were added directly (consider verifying Alembic revisions are stamped correctly)")

            # Produce a concise audit report for critical tables
            expected = {
                'projects': {'archived'},
                'collections': {'archived'},
                'users': {'last_seen'},
                'review_tokens': {'last_accessed_at'},
                'review_batch_tokens': {'last_accessed_at'},
            }
            for table, exp_cols in expected.items():
                existing = {c['name'] for c in inspector.get_columns(table)}
                missing = exp_cols - existing
                if missing:
                    drift_issues.append((table, sorted(missing)))
                    print(f"❌ Drift persists: {table} still missing {missing}")
                else:
                    print(f"✅ {table} columns OK: required {sorted(exp_cols)} present")

            if drift_issues:
                print("⚠️ Remaining drift detected (manual follow-up advised):")
                for table, cols in drift_issues:
                    print(f"   - {table}: missing {cols}")
            else:
                print("🧮 Schema audit passed – no remaining required columns missing")
            
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
