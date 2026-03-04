# backend/app.py

import sys
import os
import mimetypes
import secrets
from flask import Flask, jsonify, send_from_directory, send_file, request, make_response
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from .extensions import db, migrate, jwt, limiter, init_sentry, redis_conn, task_queue
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode, quote
import socket
from datetime import datetime, timedelta
import json
import uuid

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def load_env_file():
    """Load environment variables from .env files (.env at repo root and backend/.env.email).

    Uses python-dotenv when available (preferred), then falls back to a minimal
    manual loader for the repo root .env. Never overrides existing env vars.
    """
    # Preferred: python-dotenv for both files, without override
    try:
        from dotenv import load_dotenv  # type: ignore
        repo_root = os.path.dirname(os.path.dirname(__file__))
        backend_dir = os.path.dirname(__file__)
        # Load root .env first, then backend/.env.email
        load_dotenv(os.path.join(repo_root, '.env'), override=False)
        load_dotenv(os.path.join(backend_dir, '.env.email'), override=False)
    except Exception:
        # Fallback: minimal manual loader for root .env
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        k = key.strip()
                        v = value.strip()
                        # Don't override existing environment variables set by the platform
                        if k in os.environ:
                            continue
                        # Strip surrounding quotes if present
                        if (v.startswith("'") and v.endswith("'")) or (v.startswith('"') and v.endswith('"')):
                            v = v[1:-1]
                        os.environ[k] = v

def _load_version_metadata():
    """Load version/build metadata from environment or version.json (non-fatal)."""
    meta = {
        'version': os.environ.get('APP_VERSION'),
        'commit': os.environ.get('GIT_COMMIT'),
        'build_time': os.environ.get('BUILD_TIME')
    }
    candidate_paths = [
        os.path.join(os.getcwd(), 'backend', 'version.json'),
        os.path.join(os.getcwd(), 'version.json')
    ]
    for p in candidate_paths:
        if os.path.exists(p):
            try:
                import json
                with open(p, 'r') as f:
                    data = json.load(f)
                for k, v in data.items():
                    if v and not meta.get(k):
                        meta[k] = v
                break
            except Exception as e:
                print(f"⚠️  Failed reading version metadata from {p}: {e}")
    # Fallback commit using git (best-effort)
    if not meta.get('commit'):
        try:
            import subprocess
            meta['commit'] = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], stderr=subprocess.DEVNULL).decode().strip()
        except Exception:
            pass
    if not meta.get('build_time'):
        meta['build_time'] = datetime.utcnow().isoformat() + 'Z'
    return meta

def create_app(environ=None, start_response=None):
    print("🚀 Creating Flask app...")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Files in current directory: {os.listdir('.')[:5]}...")  # Show first 5 files
    print(f"Python path: {sys.path[:3]}...")  # Show first 3 paths
    print(f"Environment PORT: {os.environ.get('PORT', 'not set')}")
    print(f"Environment variables: {[k for k in os.environ.keys() if 'PORT' in k or 'HOST' in k or 'DATABASE' in k]}")

    # CRITICAL: Check if essential files exist
    essential_files = ['.enable_blueprints', 'frontend/dist/index.html', 'frontend/dist/favicon.ico']
    for file_path in essential_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} MISSING!")

    # EMERGENCY FALLBACK: If critical files missing, create minimal app
    if not all(os.path.exists(f) for f in essential_files):
        print("⚠️  Critical files missing! Creating emergency fallback app...")
        app = Flask(__name__)

        @app.route('/')
        def emergency_root():
            print("🏠 Emergency root endpoint requested")
            return jsonify({
                'status': 'emergency',
                'service': 'StructuredDocs',
                'message': 'App in emergency mode - missing critical files',
                'timestamp': datetime.now().isoformat()
            }), 200

        @app.route('/api/ping', methods=['GET'])
        def emergency_ping():
            print("🏓 Emergency ping requested")
            return jsonify({
                'status': 'emergency_pong',
                'timestamp': datetime.now().isoformat(),
                'message': 'Emergency mode active'
            }), 200

        @app.route('/favicon.ico')
        def emergency_favicon():
            return "Favicon placeholder", 200

        @app.route('/api/health')
        def emergency_health():
            print("🏥 Emergency health check requested")
            return jsonify({
                "status": "emergency",
                "message": "App in emergency mode",
                "timestamp": datetime.now().isoformat()
            }), 200

        return app

    # WORKAROUND: Placeholder assets (opt-in only)
    # To avoid stray files in production, only create placeholders when ENABLE_PLACEHOLDER_ASSETS=1
    try:
        enable_placeholders = os.environ.get('ENABLE_PLACEHOLDER_ASSETS') == '1'
        assets_dir = os.path.join(os.getcwd(), 'frontend', 'dist', 'assets')
        index_js_path = os.path.join(assets_dir, 'index-C_NHaPTA.js')
        index_css_path = os.path.join(assets_dir, 'index-CiVy6UYJ.css')

        if enable_placeholders:
            print("🔧 Placeholder assets: ENABLE_PLACEHOLDER_ASSETS=1 — creating if missing...")
            os.makedirs(assets_dir, exist_ok=True)
            if not os.path.exists(index_js_path):
                try:
                    with open(index_js_path, 'w') as f:
                        f.write(
                            """
console.log('Placeholder JavaScript loaded - main app bundle missing from Docker container');
console.log('This is a workaround for Docker file copying issues');
// Minimal Vue.js placeholder
window.Vue = { createApp: () => ({ mount: () => console.log('App mounted (placeholder)') }) };
"""
                        )
                    print(f"✅ Created placeholder JS at: {index_js_path}")
                except Exception as e:
                    print(f"❌ Failed to create placeholder JS: {e}")
            if not os.path.exists(index_css_path):
                try:
                    with open(index_css_path, 'w') as f:
                        f.write(
                            """
body { 
    font-family: Arial, sans-serif; 
    margin: 0; 
    padding: 20px; 
    background: #f5f5f5; 
}
#app { 
    max-width: 800px; 
    margin: 0 auto; 
    background: white; 
    padding: 20px; 
    border-radius: 8px; 
    box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
}
h1 { color: #333; }
p { color: #666; }
"""
                        )
                    print(f"✅ Created placeholder CSS at: {index_css_path}")
                except Exception as e:
                    print(f"❌ Failed to create placeholder CSS: {e}")
        else:
            # Cleanup known placeholder files if present
            removed = []
            for p in (index_js_path, index_css_path):
                try:
                    if os.path.exists(p):
                        os.remove(p)
                        removed.append(os.path.basename(p))
                except Exception as _e_rm:
                    print(f"⚠️ Could not remove placeholder asset {p}: {_e_rm}")
            if removed:
                print(f"🧹 Removed placeholder assets: {removed}")
            else:
                print("🧹 No placeholder assets to remove; keeping dist clean.")
    except Exception as _ph_e:
        print(f"⚠️ Placeholder asset handling skipped due to error: {_ph_e}")
    # Load environment variables from .env file
    load_env_file()

    app = Flask(__name__, instance_relative_config=True)
    print("📱 Flask instance created")
    print(f"Instance path: {app.instance_path}")
    print(f"Root path: {app.root_path}")    # Load configuration
    # Load configuration — prefer environment variables; fall back to ephemeral random keys
    # with a loud warning so the operator knows sessions won't survive restarts.
    _secret_key = os.environ.get('SECRET_KEY')
    _jwt_secret = os.environ.get('JWT_SECRET_KEY')
    if not _secret_key:
        _secret_key = secrets.token_hex(32)
        print("⚠️  WARNING: SECRET_KEY not set — using ephemeral key. Set SECRET_KEY in .env for persistent sessions.")
    if not _jwt_secret:
        _jwt_secret = secrets.token_hex(32)
        print("⚠️  WARNING: JWT_SECRET_KEY not set — using ephemeral key. All JWT tokens will be invalidated on restart.")

    app.config.from_mapping(
        SECRET_KEY=_secret_key,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY=_jwt_secret,
        JWT_ACCESS_TOKEN_EXPIRES=timedelta(minutes=15),
        JWT_REFRESH_TOKEN_EXPIRES=timedelta(days=7),
        MAX_CONTENT_LENGTH=20 * 1024 * 1024,  # 20 MB upload limit
        STATIC_FOLDER=os.path.join(os.getcwd(), 'frontend', 'dist'),
        STATIC_URL_PATH='/',
        FRONTEND_FOLDER=os.path.join(os.getcwd(), 'frontend', 'dist')
    )

    # Configure JWT cookie settings for cross-domain requests
    # Accept tokens from both Authorization header (existing clients) and HttpOnly cookies
    app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
    app.config['JWT_COOKIE_HTTPONLY'] = True
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False  # CSRF protection can be enabled later when fully cookie-based
    # In Codespaces, frontend and backend are on different subdomains, requiring SameSite=None
    if os.environ.get('CODESPACE_NAME'):
        app.config['JWT_COOKIE_SECURE'] = True
        app.config['JWT_COOKIE_SAMESITE'] = 'None'
    else:
        # For local development over HTTP, 'Lax' is the secure default.
        app.config['JWT_COOKIE_SECURE'] = False
        app.config['JWT_COOKIE_SAMESITE'] = 'Lax'

    # Environment-specific database configuration
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        # Normalize postgres scheme and enforce SSL if not provided
        if db_url.startswith('postgres://'):
            db_url = 'postgresql://' + db_url[len('postgres://'):]

        # Append sslmode=require if missing for Postgres/Supabase compatibility
        try:
            parsed = urlparse(db_url)
            if parsed.scheme in ("postgresql", "postgres"):
                q = dict(parse_qsl(parsed.query, keep_blank_values=True))
                if 'sslmode' not in q:
                    q['sslmode'] = 'require'
                    new_query = urlencode(q)
                    db_url = urlunparse((
                        parsed.scheme,
                        parsed.netloc,
                        parsed.path,
                        parsed.params,
                        new_query,
                        parsed.fragment,
                    ))
                # Prefer IPv4: resolve host to IPv4 to avoid IPv6-only routing issues
                try:
                    host = parsed.hostname
                    port = parsed.port or 5432
                    if host and socket is not None:
                        addrs = socket.getaddrinfo(host, port, family=socket.AF_INET, type=socket.SOCK_STREAM)
                        if addrs:
                            ipv4 = addrs[0][4][0]
                            userinfo = ''
                            if parsed.username:
                                userinfo = quote(parsed.username, safe='')
                                if parsed.password:
                                    userinfo += f":{quote(parsed.password, safe='')}"
                                userinfo += '@'
                            new_netloc = f"{userinfo}{ipv4}:{port}"
                            db_url = urlunparse((
                                parsed.scheme,
                                new_netloc,
                                parsed.path,
                                parsed.params,
                                urlencode(q),
                                parsed.fragment,
                            ))
                            print(f"🌐 Using IPv4 for DB host: {host} -> {ipv4}")
                except Exception as _ipv4e:
                    print(f"⚠️ Could not force IPv4 for DB host: {_ipv4e}")
        except Exception as _e:
            print(f"⚠️ Could not normalize DATABASE_URL: {_e}")

        if db_url.startswith('sqlite'):
            path_part = db_url.split('sqlite:///')[-1]
            if not os.path.isabs(path_part):
                path_part = os.path.join(app.instance_path, path_part)
            app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{path_part}'
        else:
            app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    else:
        # Optional safety: fail fast if instructed not to allow SQLite fallback in production
        if os.environ.get('DISABLE_SQLITE_FALLBACK') == '1':
            raise RuntimeError(
                'DATABASE_URL is not set and DISABLE_SQLITE_FALLBACK=1; refusing to start with SQLite. '\
                'Set DATABASE_URL in your server environment or hosting control panel.' 
            )
        # Default local development database - use app root instead of instance for container compatibility
        # In production, use a more reliable path
        if os.environ.get('PORT'):  # DigitalOcean sets PORT in production
            # Use current working directory for database in production
            db_path = os.path.join(os.getcwd(), 'structured_docs.db')
        else:
            db_path = os.path.join(os.path.dirname(app.root_path), 'instance', 'structured_docs.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"

    # Log (safely) which database we're using to help diagnose env issues
    try:
        uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if uri.startswith('sqlite'):
            print(f"🗄️ DB: SQLite -> {uri}")
        else:
            parsed = urlparse(uri)
            host = parsed.hostname or 'unknown-host'
            dbname = (parsed.path or '').lstrip('/') or 'unknown-db'
            print(f"🗄️ DB: {parsed.scheme} -> host={host}, db={dbname}")
    except Exception as _e:
        print(f"⚠️ Could not log DB URI info: {_e}")

    # Ensure the instance folder exists (use app root path for container compatibility)
    instance_dir = os.path.join(os.path.dirname(app.root_path), 'instance')
    try:
        os.makedirs(instance_dir, exist_ok=True)
    except OSError as e:
        print(f"⚠️ Could not create instance directory {instance_dir}: {e}")

    # --- Database engine pooling (non-SQLite) ---------------------------------
    try:
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if not db_uri.startswith('sqlite'):
            def _int_env(name: str, default: int):
                try:
                    raw = os.environ.get(name, '').strip()
                    if not raw:
                        return default
                    val = int(raw)
                    return val if val >= 0 else default
                except Exception:
                    return default
            engine_opts = {
                'pool_size': _int_env('DB_POOL_SIZE', 5),
                'max_overflow': _int_env('DB_MAX_OVERFLOW', 10),
                'pool_recycle': _int_env('DB_POOL_RECYCLE', 1800),
                'pool_timeout': _int_env('DB_POOL_TIMEOUT', 30),
            }
            app.config['SQLALCHEMY_ENGINE_OPTIONS'] = engine_opts
            print(f"🛢️ Applied SQLAlchemy engine options: {engine_opts}")
        else:
            print("🛢️ Skipping engine pool options for SQLite")
    except Exception as _e_pool:
        print(f"⚠️ Could not set engine options: {_e_pool}")

    # --- Centralized rate limit configuration BEFORE limiter.init_app --------
    rate_default = os.environ.get('RATE_LIMIT_DEFAULT')  # e.g. "200 per day;50 per hour"
    if rate_default and limiter:
        try:
            parsed = [r.strip() for r in rate_default.replace(',', ';').split(';') if r.strip()]
            if parsed:
                limiter._default_limits = parsed  # type: ignore (private attr acceptable here)
                print(f"🚦 Overriding default rate limits: {parsed}")
        except Exception as _rl_e:
            print(f"⚠️ Could not apply RATE_LIMIT_DEFAULT: {_rl_e}")
    rate_login = os.environ.get('RATE_LIMIT_LOGIN')
    rate_auth = os.environ.get('RATE_LIMIT_AUTH')
    rate_write = os.environ.get('RATE_LIMIT_WRITE')

    # Initialize extensions
    print("🔧 Initializing extensions...")
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    if limiter:
        limiter.init_app(app)
        print("✅ Limiter initialized")
    print("✅ Extensions initialized")

    # Structured logging helper (opt-in via LOG_FORMAT=json)
    log_json = os.environ.get('LOG_FORMAT') == 'json'
    def log_event(event: str, **fields):  # lightweight structured log
        if log_json:
            payload = {'event': event, 'ts': datetime.utcnow().isoformat() + 'Z', **fields}
            try:
                print(json.dumps(payload, ensure_ascii=False))
            except Exception:
                print(f"{event} | {fields}")
        else:
            print(f"{event}: {fields}")

    @app.before_request
    def _assign_request_id():  # type: ignore
        rid = request.headers.get('X-Request-ID') or uuid.uuid4().hex[:12]
        request.environ['request_id'] = rid
        if log_json:
            log_event('request_start', path=request.path, method=request.method, rid=rid, ip=request.remote_addr)

    @app.after_request
    def _after(resp):  # type: ignore
        rid = request.environ.get('request_id')
        if log_json:
            log_event('request_end', path=request.path, status=resp.status_code, rid=rid)
        resp.headers.setdefault('X-Request-ID', rid)
        return resp

    # Sentry (optional)
    sentry_dsn = os.environ.get('SENTRY_DSN')
    if sentry_dsn:
        try:
            ok = init_sentry(sentry_dsn)
            print(f"🛰  Sentry enabled: {ok}")
        except Exception as e:
            print(f"⚠️  Sentry init failed: {e}")

    # Redis / RQ queue (optional)
    global redis_conn, task_queue
    redis_url = os.environ.get('REDIS_URL') or os.environ.get('REDISCLOUD_URL')
    if redis_url:
        try:
            import redis as _redis  # type: ignore
            import rq as _rq  # type: ignore
            redis_conn = _redis.from_url(redis_url)
            task_queue = _rq.Queue('default', connection=redis_conn)
            print('✅ Redis task queue initialized')
        except Exception as e:
            print(f"⚠️  Redis/RQ init failed: {e}")
    
    # Configure CORS - use production URL if available, otherwise allow the current origin
    print("🌐 Configuring CORS...")
    frontend_url = os.environ.get('FRONTEND_URL')
    if not frontend_url:
        # In production, allow the same origin (for full-stack apps)
        if os.environ.get('PORT'):  # DigitalOcean sets PORT in production
            # Allow all origins for now to avoid CORS issues
            frontend_url = '*'
        else:
            frontend_url = 'http://localhost:5173'  # Local development

    CORS(app, resources={r"/*": {"origins": frontend_url}}, supports_credentials=True)
    print(f"✅ CORS configured with origins: {frontend_url}")

    print("🗄️ Setting up database context...")
    with app.app_context():
        print("📦 Importing models...")
        # Import models to ensure they are registered with SQLAlchemy
        from backend import models
        print("✅ Models imported")
        
        # Force mapper configuration
        from sqlalchemy.orm import configure_mappers
        configure_mappers()
        print("✅ Mappers configured")
        
        # Test database connection
        try:
            print("🔍 Testing database connection...")
            with db.engine.connect() as conn:
                conn.execute(db.text('SELECT 1'))
            print("✅ Database connection successful")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            print(f"Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'not set')}")
            print("ℹ️ This might be normal during first deployment if tables don't exist yet")
            # Don't fail here, just log the error

        # Ensure critical new tables exist (lightweight safety net if migrations not yet run)
        try:
            from sqlalchemy import inspect as _inspect
            inspector = _inspect(db.engine)
            existing_tables = set(inspector.get_table_names())
            critical = {'variables', 'variable_values', 'collection_variable_selections'}
            missing = critical - existing_tables
            if missing:
                print(f"🛠  Creating missing critical tables (fallback): {missing}")
                db.create_all()
            else:
                print("✅ Critical tables present")

            # Safety net: ensure import_links table exists so Word imports don't 500 if migration not applied
            if 'import_links' not in existing_tables:
                try:
                    from backend.models import ImportLink
                    print("🛠  Creating missing table: import_links (fallback until migration applied)")
                    ImportLink.__table__.create(bind=db.engine, checkfirst=True)
                except Exception as _imp_e:
                    print(f"⚠️ Could not create import_links fallback table: {_imp_e}")

            # Safety net: ensure snippets table exists
            if 'snippets' not in existing_tables:
                try:
                    from backend.models import Snippet
                    print("🛠  Creating missing table: snippets (fallback until migration applied)")
                    Snippet.__table__.create(bind=db.engine, checkfirst=True)
                except Exception as _snip_e:
                    print(f"⚠️ Could not create snippets fallback table: {_snip_e}")

            # Safety net: ensure tags / entity_tags tables exist (used by snippets, topics, etc.)
            for _model_name, _table_name in [('Tag', 'tags'), ('EntityTag', 'entity_tags')]:
                if _table_name not in existing_tables:
                    try:
                        from backend import models as _models
                        _model_cls = getattr(_models, _model_name)
                        print(f"🛠  Creating missing table: {_table_name} (fallback until migration applied)")
                        _model_cls.__table__.create(bind=db.engine, checkfirst=True)
                    except Exception as _tag_e:
                        print(f"⚠️ Could not create {_table_name} fallback table: {_tag_e}")

            # Safety net: ensure publications.form_number column exists
            if 'publications' in existing_tables:
                try:
                    _pub_cols = {c['name'] for c in inspector.get_columns('publications')}
                    if 'form_number' not in _pub_cols:
                        print("🛠  Adding missing column: publications.form_number")
                        db.session.execute(db.text(
                            "ALTER TABLE publications ADD COLUMN form_number VARCHAR(100)"
                        ))
                        db.session.commit()
                        print("✅ Added publications.form_number")
                except Exception as _fn_e:
                    print(f"⚠️ Could not add publications.form_number: {_fn_e}")
                    db.session.rollback()
        except Exception as _crit_e:
            print(f"⚠️ Could not ensure critical tables: {_crit_e}")
        
        # Reload email service configuration with loaded environment variables
        try:
            from backend.utils.email_service import email_service
            email_service.reload_config()
            print("✅ Email service configured")
        except Exception as e:
            print(f"⚠️ Email service configuration failed: {e}")
            # Don't fail the app for email issues
        
        # Create admin user if it doesn't exist (for production deployment)
        try:
            from backend.models import User
            from werkzeug.security import generate_password_hash
            from sqlalchemy import func
            
            admin_email = 'admin@example.com'
            admin_password = 'Admin123!'
            
            # Check if admin user exists
            try:
                admin_user = User.query.filter(func.lower(User.email) == admin_email.lower()).first()
                if not admin_user:
                    # Create admin user
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
            except Exception as db_error:
                print(f"⚠️ Database query failed (tables may not exist yet): {db_error}")
                print("ℹ️ This is normal during first deployment - migrations will create tables")
                # Don't fail here, just log the error
                
        except Exception as e:
            print(f"⚠️ Could not create admin user: {e}")
            # Don't fail the app for admin user creation issues
        
        # Import and register blueprints (skippable for migrations/CLI)
        print("🔧 Starting blueprint registration...")
        # Support selective enabling via ENABLE_BLUEPRINTS env var (comma-separated short names)
        # or via a file path provided in ENABLE_BLUEPRINTS_FILE. Reading from a file
        # is more reliable when uWSGI runs multiple Python sub-interpreters.
        # - If ENABLE_BLUEPRINTS_FILE exists and contains a comma-separated list, use that.
        # - Else if ENABLE_BLUEPRINTS env var is set, use that.
        # - Else if SKIP_BLUEPRINTS=="1", skip all blueprint registration.
        enable_list = None
        # Precedence change: if ENABLE_BLUEPRINTS env var is explicitly set, honor it FIRST.
        env_enable = os.environ.get('ENABLE_BLUEPRINTS')
        if env_enable:
            enable_list = env_enable
            print(f"✅ Using ENABLE_BLUEPRINTS env var (takes precedence over file): {enable_list}")
        else:
            eb_file = os.environ.get('ENABLE_BLUEPRINTS_FILE')
            if eb_file:
                print(f"📄 Checking ENABLE_BLUEPRINTS_FILE: {eb_file}")
                if os.path.exists(eb_file):
                    try:
                        with open(eb_file, 'r') as _f:
                            enable_list = _f.read().strip()
                        print(f"✅ Read blueprints from file: {enable_list}")
                    except Exception as _e:
                        print(f"⚠️ Could not read ENABLE_BLUEPRINTS_FILE '{eb_file}': {_e}")
                else:
                    print(f"⚠️ ENABLE_BLUEPRINTS_FILE '{eb_file}' does not exist, ignoring")
        
        if enable_list:
            print("🔧 Registering selective blueprints...")
            # Map short names to (module_name, blueprint_attr_name)
            blueprint_map = {
                'admin': ('admin', 'admin_bp'),
                'collections': ('collections', 'collections_bp'),
                'dashboard': ('dashboard', 'bp'),
                'feedback': ('feedback', 'feedback_bp'),
                'images': ('images', 'images_bp'),
                'import_handler': ('import_handler', 'import_bp'),
                'links': ('links', 'links_bp'),
                'metrics': ('metrics', 'metrics_bp'),
                'milestones': ('milestones', 'milestones_bp'),
                'notifications': ('notifications', 'notifications_bp'),
                'public_images': ('public_images', 'public_images_bp'),
                'variables': ('variables', 'variables_bp'),
                'projects': ('projects', 'projects_bp'),
                'publications': ('publications', 'pubs_bp'),
                'review_tokens': ('review_tokens', 'review_tokens_bp'),
                'reviews': ('reviews', 'reviews_bp'),
                'sequences': ('sequences', 'sequences_bp'),
                'stakeholders': ('stakeholders', 'stakeholders_bp'),
                'snippets': ('snippets', 'snippets_bp'),
                'tags': ('tags', 'tags_bp'),
                'tasks': ('tasks', 'tasks_bp'),
                'topics': ('topics', 'topics_bp'),
                'users': ('users', 'users_bp'),
            }

            requested = [p.strip() for p in enable_list.split(',') if p.strip()]
            print(f"📋 Requested blueprints: {requested}")
            import importlib
            for name in requested:
                if name not in blueprint_map:
                    print(f"\u26a0\ufe0f ENABLE_BLUEPRINTS: unknown blueprint '{name}' - skipping")
                    continue
                module_name, attr = blueprint_map[name]
                try:
                    print(f"📦 Importing backend.routes.{module_name}...")
                    mod = importlib.import_module(f'backend.routes.{module_name}')
                    bp = getattr(mod, attr)
                    print(f"🔗 Registering blueprint {name}...")
                    app.register_blueprint(bp)
                    print(f"\u2705 Registered blueprint '{name}' from backend.routes.{module_name}.{attr}")
                except Exception as _e:
                    print(f"\u274c Error registering blueprint '{name}': {_e}")
                    # Alias legacy login path in selective mode
            # Alias legacy login path in selective mode
            if 'users' in requested:
                try:
                    from backend.routes.users import login as users_login
                    app.add_url_rule('/api/login', 'login', users_login, methods=['POST'])
                    print("🔗 Alias route '/api/login' registered for users_login")
                except Exception as _e:
                    print(f"⚠️ Could not register alias route '/api/login': {_e}")
        elif os.environ.get('SKIP_BLUEPRINTS') == '1':
            print("\u23ed\ufe0f  SKIP_BLUEPRINTS=1 set; skipping blueprint imports/registration (useful for migrations).")
        else:
            print("🔧 Registering all blueprints...")
            # Import and register all blueprints
            from .routes import (
                admin,
                collections,
                dashboard,
                diagnostics,
                feedback,
                images,
                import_handler,
                links,
                metrics,
                milestones,
                notifications,
                variables,
                projects,
                publications,
                review_tokens,
                reviews,
                sequences,
                snippets,
                stakeholders,
                tags,
                tasks,
                topics,
                public_images,
                users,
            )

            app.register_blueprint(admin.admin_bp)
            app.register_blueprint(collections.collections_bp)
            app.register_blueprint(dashboard.bp)
            app.register_blueprint(diagnostics.diagnostics_bp)
            app.register_blueprint(feedback.feedback_bp)
            app.register_blueprint(images.images_bp)
            app.register_blueprint(import_handler.import_bp)
            app.register_blueprint(links.links_bp)
            app.register_blueprint(metrics.metrics_bp)
            app.register_blueprint(milestones.milestones_bp)
            app.register_blueprint(notifications.notifications_bp)
            app.register_blueprint(variables.variables_bp)
            app.register_blueprint(projects.projects_bp)
            app.register_blueprint(publications.pubs_bp)
            app.register_blueprint(review_tokens.review_tokens_bp)
            app.register_blueprint(reviews.reviews_bp)
            app.register_blueprint(sequences.sequences_bp)
            app.register_blueprint(stakeholders.stakeholders_bp)
            app.register_blueprint(snippets.snippets_bp)
            app.register_blueprint(tags.tags_bp)
            app.register_blueprint(tasks.tasks_bp)
            app.register_blueprint(topics.topics_bp)
            app.register_blueprint(public_images.public_images_bp)
            app.register_blueprint(users.users_bp)
            print("✅ All blueprints registered")
            # Alias legacy login path
            try:
                from backend.routes.users import login as users_login
                app.add_url_rule('/api/login', 'login', users_login, methods=['POST'])
                print("🔗 Alias route '/api/login' registered for users_login")
            except ImportError as _e:
                print(f"⚠️ Could not register alias route '/api/login': {_e}")

        @app.route('/', methods=['GET'])
        def root():
            print("🏠 Root endpoint requested at", datetime.now().isoformat())
            try:
                index_path = os.path.join(app.config['FRONTEND_FOLDER'], 'index.html')
                if os.path.exists(index_path):
                    print(f"✅ Serving frontend from: {index_path}")
                    return send_from_directory(app.config['FRONTEND_FOLDER'], 'index.html')
                else:
                    print(f"❌ Frontend index.html not found at: {index_path}")
                    return jsonify({
                        'status': 'error',
                        'message': 'Frontend not found',
                        'frontend_folder': app.config['FRONTEND_FOLDER'],
                        'files': os.listdir(app.config['FRONTEND_FOLDER']) if os.path.exists(app.config['FRONTEND_FOLDER']) else []
                    }), 404
            except Exception as e:
                print(f"❌ Error serving frontend: {e}")
                return jsonify({
                    'status': 'error',
                    'message': str(e),
                    'frontend_folder': app.config['FRONTEND_FOLDER']
                }), 500

        version_meta = _load_version_metadata()

        @app.route('/api/version', methods=['GET'])
        def version():
            return jsonify({
                'service': 'StructuredDocs',
                **{k: v for k, v in version_meta.items() if v}
            }), 200

        @app.route('/api/ping', methods=['GET'])
        def ping():
            print("🏓 Ping requested at", datetime.now().isoformat())
            return jsonify({
                'status': 'pong',
                'timestamp': datetime.now().isoformat(),
                'message': 'Flask app is responding',
                'port': os.environ.get('PORT', 'unknown')
            }), 200

        @app.route('/api/health', methods=['GET'])
        def health_check():
            uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
            if uri.startswith('sqlite'):
                db_kind = 'sqlite'
            else:
                parsed = urlparse(uri)
                db_kind = parsed.scheme or 'unknown'

            # Test actual DB connectivity
            db_status = 'ok'
            try:
                from sqlalchemy import text as _text
                db.session.execute(_text('SELECT 1'))
            except Exception as _db_e:
                db_status = 'error'
                current_app.logger.error("Health check DB probe failed: %s", _db_e)

            status_code = 200 if db_status == 'ok' else 503
            return jsonify({
                'status': 'ok' if db_status == 'ok' else 'degraded',
                'db': db_kind,
                'db_status': db_status,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
            }), status_code

        # --- Specific endpoint rate limits (post-registration) ---------------
        try:
            if limiter:
                applied = []
                def _apply(name: str, limit_val: str | None):
                    if not limit_val:
                        return
                    if name in app.view_functions:
                        try:
                            limiter.limit(limit_val)(app.view_functions[name])  # type: ignore
                            applied.append((name, limit_val))
                        except Exception as _a_e:
                            print(f"⚠️ Could not apply rate limit '{limit_val}' to {name}: {_a_e}")
                # Login endpoints
                _apply('login', rate_login)
                _apply('users.login', rate_login)
                # Auth/refresh
                _apply('users.refresh', rate_auth)
                # Representative write endpoints (best-effort; ignore if absent)
                for ep in ['collections.create_collection', 'publications.create_publication', 'reviews.create_review']:
                    _apply(ep, rate_write)
                if applied:
                    print(f"🚦 Applied specific rate limits: {applied}")
                else:
                    print("ℹ️ No specific rate limits applied (endpoints may differ or env vars unset)")
        except Exception as _spec_e:
            print(f"⚠️ Error applying specific limits: {_spec_e}")

        # Static file serving and other routes
        @app.route('/images/<path:filename>')
        def serve_image(filename):
            try:
                print(f"\n🖼️ IMAGE REQUEST: {filename}")
                print(f"   Raw filename param: {repr(filename)}")
                
                # Primary: built frontend dist images
                dist_images_dir = os.path.join(app.config['STATIC_FOLDER'], 'images')
                full_path = os.path.join(dist_images_dir, filename)
                print(f"🔍 Checking dist: {full_path}")
                print(f"   Exists: {os.path.exists(full_path)}")
                if os.path.exists(full_path):
                    print(f"   ✅ Found in dist, serving...")
                    return send_from_directory(dist_images_dir, filename)

                # Fallback 1: unbuilt public images (useful when images added post-build)
                public_images_dir = os.path.join(os.path.dirname(app.root_path), 'frontend', 'public', 'images')
                full_public_path = os.path.join(public_images_dir, filename)
                print(f"🔍 Checking public: {full_public_path}")
                print(f"   Exists: {os.path.exists(full_public_path)}")
                if os.path.exists(full_public_path):
                    print(f"   ✅ Found in public, serving...")
                    return send_from_directory(public_images_dir, filename)

                # Fallback 2: backend static images (ingestion backend path)
                backend_images_dir = os.path.join(app.root_path, 'static', 'images')
                full_backend_path = os.path.join(backend_images_dir, filename)
                print(f"🔍 Checking backend: {full_backend_path}")
                print(f"   Exists: {os.path.exists(full_backend_path)}")
                if os.path.exists(full_backend_path):
                    print(f"   ✅ Found in backend, serving...")
                    return send_from_directory(backend_images_dir, filename)

                # Debug: List what's actually in backend static images
                print(f"❌ Not found in any location")
                if os.path.exists(backend_images_dir):
                    print(f"📁 Contents of {backend_images_dir}:")
                    for root, dirs, files in os.walk(backend_images_dir):
                        level = root.replace(backend_images_dir, '').count(os.sep)
                        indent = ' ' * 2 * level
                        print(f"{indent}{os.path.basename(root)}/")
                        if level < 3:  # Limit depth to avoid spam
                            subindent = ' ' * 2 * (level + 1)
                            for file in files[:5]:  # Show first 5 files per dir
                                print(f"{subindent}{file}")

                print(f"❌ Image not found: {filename}")
                return "Image not found", 404
            except Exception as e:
                print(f"❌ Error serving image {filename}: {e}")
                import traceback
                traceback.print_exc()
                return "Image serving error", 500

        # Simple asset serving route
        @app.route('/assets/<path:filename>')
        def serve_assets(filename):
            print(f"🎯 Asset request for: '{filename}'")
            
            try:
                # Determine the correct MIME type
                if filename.endswith('.js'):
                    mimetype = 'application/javascript'
                elif filename.endswith('.css'):
                    mimetype = 'text/css'
                elif filename.endswith('.woff2'):
                    mimetype = 'font/woff2'
                elif filename.endswith('.woff'):
                    mimetype = 'font/woff'
                elif filename.endswith('.svg'):
                    mimetype = 'image/svg+xml'
                else:
                    mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
                
                # Serve the file from the built frontend assets directory
                assets_dir = os.path.join(app.config['FRONTEND_FOLDER'], 'assets')
                full_asset_path = os.path.join(assets_dir, filename)
                if os.path.exists(full_asset_path):
                    resp = send_from_directory(assets_dir, filename)
                    # Overwrite/ensure correct content type
                    resp.headers['Content-Type'] = mimetype
                    print(f"✅ Serving asset from {assets_dir} with MIME type: {mimetype}")
                    return resp
                
                # Fallback: if not in /assets, try the dist root (some files like logos live there)
                root_dir = app.config['FRONTEND_FOLDER']
                root_file = os.path.basename(filename)
                full_root_path = os.path.join(root_dir, root_file)
                if os.path.exists(full_root_path):
                    resp = send_from_directory(root_dir, root_file)
                    resp.headers['Content-Type'] = mimetype
                    print(f"🔁 Fallback: served '{root_file}' from dist root with MIME type: {mimetype}")
                    return resp
                
                print(f"❌ Asset not found in assets or root: {filename}")
                return (f"Not Found: {filename}", 404)
            except Exception as e:
                print(f"❌ Error serving asset {filename}: {e}")
                return f"Error: {str(e)}", 500

        @app.route('/<path:path>')
        def serve_frontend(path):
            print(f"🎯 Frontend request for path: {path}")
            
            try:
                # Determine the correct MIME type for static files
                if path.endswith('.js'):
                    mimetype = 'application/javascript'
                elif path.endswith('.css'):
                    mimetype = 'text/css'
                elif path.endswith('.woff2'):
                    mimetype = 'font/woff2'
                elif path.endswith('.woff'):
                    mimetype = 'font/woff'
                elif path.endswith('.png'):
                    mimetype = 'image/png'
                elif path.endswith('.jpg') or path.endswith('.jpeg'):
                    mimetype = 'image/jpeg'
                elif path.endswith('.svg'):
                    mimetype = 'image/svg+xml'
                elif path.endswith('.ico'):
                    mimetype = 'image/x-icon'
                else:
                    mimetype = mimetypes.guess_type(path)[0]
                
                # If it's a static asset extension, try explicit paths before SPA fallback
                static_exts = ('.js', '.css', '.woff2', '.woff', '.png', '.jpg', '.jpeg', '.svg', '.ico')
                if path.endswith(static_exts):
                    root_dir = app.config['FRONTEND_FOLDER']
                    assets_dir = os.path.join(root_dir, 'assets')

                    # Normalize path if it contains '/assets/' with extra prefix (e.g., '/sub/assets/file.js')
                    normalized_path = path
                    if '/assets/' in path:
                        normalized_path = path.split('/assets/', 1)[1]

                    # 1) Try dist root (for files like StructuredDocs_logo.svg)
                    full_root_path = os.path.join(root_dir, normalized_path)
                    if os.path.exists(full_root_path):
                        resp = send_from_directory(root_dir, normalized_path)
                        if mimetype:
                            resp.headers['Content-Type'] = mimetype
                        print(f"✅ Served static file from dist root: {normalized_path} ({mimetype})")
                        return resp

                    # 2) Try assets directory
                    full_asset_path = os.path.join(assets_dir, normalized_path)
                    if os.path.exists(full_asset_path):
                        resp = send_from_directory(assets_dir, normalized_path)
                        if mimetype:
                            resp.headers['Content-Type'] = mimetype
                        print(f"✅ Served static file from assets: {normalized_path} ({mimetype})")
                        return resp

                    # 3) If a static extension was requested but not found, return 404
                    print(f"❌ Static file not found: {path}")
                    return "Not Found", 404
                
                # If not a static file, serve index.html for SPA routing
                index_path = os.path.join(app.config['FRONTEND_FOLDER'], 'index.html')
                if os.path.exists(index_path):
                    print(f"✅ Serving index.html for SPA route: {path}")
                    return send_from_directory(app.config['FRONTEND_FOLDER'], 'index.html')
                else:
                    print(f"❌ index.html not found")
                    return "Frontend not found", 404
            except Exception as e:
                print(f"❌ Error serving frontend path {path}: {e}")
                return f"Error: {str(e)}", 500

    # Security headers middleware (toggle via ENABLE_SECURITY_HEADERS=0 to disable)
    if os.environ.get('ENABLE_SECURITY_HEADERS', '1') == '1':
        @app.after_request
        def _security_headers(resp):  # type: ignore
            try:
                resp.headers.setdefault('X-Content-Type-Options', 'nosniff')
                resp.headers.setdefault('X-Frame-Options', 'DENY')
                resp.headers.setdefault('Referrer-Policy', 'no-referrer-when-downgrade')
                resp.headers.setdefault('Permissions-Policy', os.environ.get('PERMISSIONS_POLICY', 'geolocation=(), microphone=(), camera=()'))
                # Build CSP with Spaces CDN support
                spaces_cdn = os.environ.get('SPACES_CDN_ENDPOINT', 'https://*.nyc3.digitaloceanspaces.com https://*.nyc3.cdn.digitaloceanspaces.com')
                default_csp = f"default-src 'self'; img-src 'self' data: blob: {spaces_cdn}; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; font-src 'self' data:; connect-src *; frame-ancestors 'none'; object-src 'none'"
                resp.headers.setdefault('Content-Security-Policy', os.environ.get('CSP_HEADER', default_csp))
            except Exception as e:
                print(f"⚠️  Security headers error: {e}")
            return resp
        print("🛡️ Security headers middleware active")
    else:
        print("🛡️ Security headers disabled via ENABLE_SECURITY_HEADERS=0")

    # Add error handlers
    @app.errorhandler(500)
    def internal_error(error):
        print(f"500 Internal Server Error: {error}")
        return "Internal Server Error", 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        print(f"Unhandled exception: {e}")
        if isinstance(e, HTTPException):
            return e
        return "Internal Server Error", 500

    # Apply rate limit to login if route imported
    if limiter:
        try:
            from backend.routes.users import login as _login
            limiter.limit("5 per minute")(_login)  # type: ignore
            print("✅ Rate limit applied to login endpoint")
        except Exception as e:
            print(f"⚠️  Could not attach rate limit to login: {e}")

    @app.route('/api/csp-report', methods=['POST'])
    def csp_report():
        """Receive Content-Security-Policy violation reports from browsers."""
        try:
            report = request.get_json(force=True, silent=True) or {}
            current_app.logger.warning("CSP violation: %s", report)
        except Exception:
            pass
        return '', 204

    print("✅ Flask app created successfully!")
    return app

if __name__ == '__main__':
    # Create app instance only when running directly
    application = create_app()
    # Use a production-ready server like Gunicorn or Waitress instead of app.run in production
    port = int(os.environ.get('PORT', 8080))  # Match the start.sh default
    application.run(debug=os.environ.get('FLASK_DEBUG', '0') == '1', host='0.0.0.0', port=port)
