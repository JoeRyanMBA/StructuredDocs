# backend/app.py

import sys
import os
from flask import Flask, jsonify, send_from_directory, send_file, request
from flask_cors import CORS
from .extensions import db, migrate, jwt
from urllib.parse import urlparse
from datetime import datetime

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def load_env_file():
    """Load environment variables from .env file"""
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

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
            return "Emergency mode: App starting but missing files", 200

        @app.route('/favicon.ico')
        def emergency_favicon():
            return "Favicon placeholder", 200

        @app.route('/api/health')
        def emergency_health():
            return {"status": "emergency", "message": "App in emergency mode"}, 200

        return app

    # Load environment variables from .env file
    load_env_file()

    app = Flask(__name__, instance_relative_config=True)
    print("📱 Flask instance created")
    print(f"Instance path: {app.instance_path}")
    print(f"Root path: {app.root_path}")    # Load configuration
    app.config.from_mapping(
        SECRET_KEY='your-flask-secret-key-change-in-production',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY='your-secret-key-change-in-production',
        STATIC_FOLDER=os.path.join(app.root_path, 'static'),
        FRONTEND_FOLDER=os.path.join(os.path.dirname(app.root_path), 'frontend', 'dist')
    )

    # Configure JWT cookie settings for cross-domain requests
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
                'Set DATABASE_URL in your environment (e.g., PythonAnywhere Web tab).' 
            )
        # Default local development database - use app root instead of instance for container compatibility
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

    # Initialize extensions
    print("🔧 Initializing extensions...")
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    print("✅ Extensions initialized")
    
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
            # Don't fail here, just log the error
        
        # Reload email service configuration with loaded environment variables
        from backend.utils.email_service import email_service
        email_service.reload_config()
        
        # Create admin user if it doesn't exist (for production deployment)
        try:
            from backend.models import User
            from werkzeug.security import generate_password_hash
            from sqlalchemy import func
            
            admin_email = 'admin@example.com'
            admin_password = 'Admin123!'
            
            # Check if admin user exists
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
        except Exception as e:
            print(f"⚠️ Could not create admin user: {e}")
        
        # Import and register blueprints (skippable for migrations/CLI)
        print("🔧 Starting blueprint registration...")
        # Support selective enabling via ENABLE_BLUEPRINTS env var (comma-separated short names)
        # or via a file path provided in ENABLE_BLUEPRINTS_FILE. Reading from a file
        # is more reliable when uWSGI runs multiple Python sub-interpreters.
        # - If ENABLE_BLUEPRINTS_FILE exists and contains a comma-separated list, use that.
        # - Else if ENABLE_BLUEPRINTS env var is set, use that.
        # - Else if SKIP_BLUEPRINTS=="1", skip all blueprint registration.
        enable_list = None
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
        if not enable_list:
            enable_list = os.environ.get('ENABLE_BLUEPRINTS')
            if enable_list:
                print(f"✅ Using ENABLE_BLUEPRINTS env var: {enable_list}")
        
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
                'projects': ('projects', 'projects_bp'),
                'publications': ('publications', 'pubs_bp'),
                'review_tokens': ('review_tokens', 'review_tokens_bp'),
                'reviews': ('reviews', 'reviews_bp'),
                'sequences': ('sequences', 'sequences_bp'),
                'stakeholders': ('stakeholders', 'stakeholders_bp'),
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
        elif os.environ.get('SKIP_BLUEPRINTS') == '1':
            print("\u23ed\ufe0f  SKIP_BLUEPRINTS=1 set; skipping blueprint imports/registration (useful for migrations).")
        else:
            print("🔧 Registering all blueprints...")
            # Import and register all blueprints
            from .routes import (
                admin,
                collections,
                dashboard,
                feedback,
                images,
                import_handler,
                links,
                metrics,
                milestones,
                notifications,
                projects,
                publications,
                review_tokens,
                reviews,
                sequences,
                stakeholders,
                tags,
                tasks,
                topics,
                users,
            )

            app.register_blueprint(admin.admin_bp)
            app.register_blueprint(collections.collections_bp)
            app.register_blueprint(dashboard.bp)
            app.register_blueprint(feedback.feedback_bp)
            app.register_blueprint(images.images_bp)
            app.register_blueprint(import_handler.import_bp)
            app.register_blueprint(links.links_bp)
            app.register_blueprint(metrics.metrics_bp)
            app.register_blueprint(milestones.milestones_bp)
            app.register_blueprint(notifications.notifications_bp)
            app.register_blueprint(projects.projects_bp)
            app.register_blueprint(publications.pubs_bp)
            app.register_blueprint(review_tokens.review_tokens_bp)
            app.register_blueprint(reviews.reviews_bp)
            app.register_blueprint(sequences.sequences_bp)
            app.register_blueprint(stakeholders.stakeholders_bp)
            app.register_blueprint(tags.tags_bp)
            app.register_blueprint(tasks.tasks_bp)
            app.register_blueprint(topics.topics_bp)
            app.register_blueprint(users.users_bp)
            print("✅ All blueprints registered")

        @app.route('/api/ping', methods=['GET'])
        def ping():
            print("🏓 Ping requested at", datetime.now().isoformat())
            return jsonify({
                'status': 'pong',
                'timestamp': datetime.now().isoformat(),
                'message': 'Flask app is responding'
            }), 200
        def health_check():
            print("🏥 Health check requested at", datetime.now().isoformat())
            print(f"🏥 Request method: {request.method}")
            print(f"🏥 Request URL: {request.url}")
            print(f"🏥 Request headers: {dict(request.headers)}")
            
            uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
            if uri.startswith('sqlite'):
                db_kind = 'sqlite'
            else:
                parsed = urlparse(uri)
                db_kind = parsed.scheme or 'unknown'

            # Use same frontend URL logic as CORS
            frontend_origin = os.environ.get('FRONTEND_URL')
            if not frontend_origin:
                if os.environ.get('PORT'):  # DigitalOcean sets PORT in production
                    # For production, construct the URL from environment
                    host = os.environ.get('HOST', 'localhost')
                    port = os.environ.get('PORT', '8000')
                    protocol = 'https' if os.environ.get('HTTPS') == 'on' else 'http'
                    if host == 'localhost':
                        frontend_origin = f"{protocol}://{host}:{port}"
                    else:
                        frontend_origin = f"{protocol}://{host}"
                else:
                    frontend_origin = 'http://localhost:5173'  # Local development

            print(f"🏥 Health check response: status=ok, db={db_kind}, frontend={frontend_origin}")
            response_data = {
                'status': 'ok',
                'db': db_kind,
                'frontend_origin': frontend_origin,
                'timestamp': datetime.now().isoformat(),
                'request_info': {
                    'method': request.method,
                    'url': request.url,
                    'remote_addr': request.remote_addr
                }
            }
            print(f"🏥 Sending response: {response_data}")
            return jsonify(response_data), 200

        @app.route('/debug-routes')
        def debug_routes():
            import urllib.parse
            output = []
            for rule in app.url_map.iter_rules():
                options = {}
                for arg in rule.arguments:
                    options[arg] = f"[{arg}]"

                methods = ','.join(rule.methods or [])
                url = urllib.parse.unquote(rule.endpoint)
                line = f"{url:50s} {methods:20s} {str(rule)}"
                output.append(line)
            
            response = "<pre>" + "\n".join(sorted(output)) + "</pre>"
            return response

        # Static file serving and other routes
        @app.route('/images/<path:filename>')
        def serve_image(filename):
            try:
                return send_from_directory(os.path.join(app.config['STATIC_FOLDER'], 'images'), filename)
            except Exception as e:
                print(f"Error serving image {filename}: {e}")
                return "Image not found", 404

        @app.route('/', defaults={'path': ''})
        @app.route('/<path:path>')
        def serve_frontend(path):
            try:
                if path != "" and os.path.exists(os.path.join(app.config['FRONTEND_FOLDER'], path)):
                    return send_from_directory(app.config['FRONTEND_FOLDER'], path)
                else:
                    index_path = os.path.join(app.config['FRONTEND_FOLDER'], 'index.html')
                    if os.path.exists(index_path):
                        return send_from_directory(app.config['FRONTEND_FOLDER'], 'index.html')
                    else:
                        return "Frontend not found", 404
            except Exception as e:
                print(f"Error serving frontend path {path}: {e}")
                return f"Error: {str(e)}", 500

    # Add error handlers
    @app.errorhandler(500)
    def internal_error(error):
        print(f"500 Internal Server Error: {error}")
        return "Internal Server Error", 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        print(f"Unhandled exception: {e}")
        return "Internal Server Error", 500

    # Add debug endpoint
    @app.route('/api/debug')
    def debug_info():
        print("🐛 Debug info requested")
        return {
            "status": "debug",
            "working_directory": os.getcwd(),
            "files": os.listdir('.')[:10],  # First 10 files
            "python_path": sys.path[:5],  # First 5 paths
            "database_uri": app.config.get('SQLALCHEMY_DATABASE_URI', 'not set')[:50] + "..." if app.config.get('SQLALCHEMY_DATABASE_URI') else 'not set'
        }, 200

    print("✅ Flask app created successfully!")
    return app

if __name__ == '__main__':
    # Create app instance only when running directly
    application = create_app()
    # Use a production-ready server like Gunicorn or Waitress instead of app.run in production
    application.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5050)))
