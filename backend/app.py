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

    # WORKAROUND: Create placeholder assets if missing
    print("🔧 Starting placeholder creation workaround...")
    # Use the same path as STATIC_FOLDER configuration
    assets_dir = os.path.join(os.getcwd(), 'frontend', 'dist', 'assets')
    print(f"🔧 Assets directory: {assets_dir}")
    print(f"🔧 Assets directory exists: {os.path.exists(assets_dir)}")
    
    os.makedirs(assets_dir, exist_ok=True)
    
    print(f"🎯 Creating placeholders in: {assets_dir}")
    print(f"🎯 Current working directory: {os.getcwd()}")
    
    # Create minimal placeholder for missing index.js
    index_js_path = os.path.join(assets_dir, 'index-C_NHaPTA.js')
    print(f"🔧 Index JS path: {index_js_path}")
    print(f"🔧 Index JS exists: {os.path.exists(index_js_path)}")
    
    if not os.path.exists(index_js_path):
        print("⚠️ Creating placeholder for missing index-C_NHaPTA.js")
        try:
            with open(index_js_path, 'w') as f:
                f.write("""
console.log('Placeholder JavaScript loaded - main app bundle missing from Docker container');
console.log('This is a workaround for Docker file copying issues');
// Minimal Vue.js placeholder
window.Vue = { createApp: () => ({ mount: () => console.log('App mounted (placeholder)') }) };
""")
            print(f"✅ Created placeholder JS at: {index_js_path}")
            print(f"🔧 File created successfully: {os.path.exists(index_js_path)}")
        except Exception as e:
            print(f"❌ Failed to create placeholder JS: {e}")
    
    # Create minimal placeholder for missing index.css
    index_css_path = os.path.join(assets_dir, 'index-CiVy6UYJ.css')
    print(f"🔧 Index CSS path: {index_css_path}")
    print(f"🔧 Index CSS exists: {os.path.exists(index_css_path)}")
    
    if not os.path.exists(index_css_path):
        print("⚠️ Creating placeholder for missing index-CiVy6UYJ.css")
        try:
            with open(index_css_path, 'w') as f:
                f.write("""
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
""")
            print(f"✅ Created placeholder CSS at: {index_css_path}")
            print(f"🔧 File created successfully: {os.path.exists(index_css_path)}")
        except Exception as e:
            print(f"❌ Failed to create placeholder CSS: {e}")
    
    print("🔧 Placeholder creation workaround completed")    # Load environment variables from .env file
    load_env_file()

    app = Flask(__name__, instance_relative_config=True)
    print("📱 Flask instance created")
    print(f"Instance path: {app.instance_path}")
    print(f"Root path: {app.root_path}")    # Load configuration
    app.config.from_mapping(
        SECRET_KEY='your-flask-secret-key-change-in-production',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY='your-secret-key-change-in-production',
        STATIC_FOLDER=os.path.join(os.getcwd(), 'frontend', 'dist'),
        STATIC_URL_PATH='/',
        FRONTEND_FOLDER=os.path.join(os.getcwd(), 'frontend', 'dist')
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
            print(f"Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'not set')}")
            print("ℹ️ This might be normal during first deployment if tables don't exist yet")
            # Don't fail here, just log the error
        
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
                        username=admin_email,
                        password_hash=generate_password_hash(admin_password),
                        role='admin'
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

        @app.route('/favicon.ico')
        def favicon():
            return send_from_directory(app.config['FRONTEND_FOLDER'], 'favicon.ico')

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

        # Simple asset serving route
        @app.route('/assets/<path:filename>')
        def serve_assets(filename):
            print(f"🎯 Asset request for: '{filename}' (type: {type(filename)})")
            try:
                # First try the configured static folder
                assets_dir = os.path.join(app.config['STATIC_FOLDER'], 'assets')
                file_path = os.path.join(assets_dir, filename)
                
                print(f"🎯 Primary assets dir: {assets_dir}")
                print(f"🎯 File exists in primary: {os.path.exists(file_path)}")
                print(f"🎯 Current working directory: {os.getcwd()}")
                
                if os.path.exists(file_path):
                    print(f"✅ Serving from primary: {filename}")
                    response = send_from_directory(assets_dir, filename)
                    # Ensure correct MIME type
                    if filename.endswith('.js'):
                        response.headers['Content-Type'] = 'application/javascript'
                    elif filename.endswith('.css'):
                        response.headers['Content-Type'] = 'text/css'
                    return response
                
                # Fallback: try direct path from app root
                app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                fallback_dir = os.path.join(app_root, 'frontend', 'dist', 'assets')
                fallback_path = os.path.join(fallback_dir, filename)
                
                print(f"🎯 Fallback assets dir: {fallback_dir}")
                print(f"🎯 File exists in fallback: {os.path.exists(fallback_path)}")
                
                if os.path.exists(fallback_path):
                    print(f"✅ Serving from fallback: {filename}")
                    response = send_from_directory(fallback_dir, filename)
                    # Ensure correct MIME type
                    if filename.endswith('.js'):
                        response.headers['Content-Type'] = 'application/javascript'
                    elif filename.endswith('.css'):
                        response.headers['Content-Type'] = 'text/css'
                    return response
                
                # ON-DEMAND PLACEHOLDER: Return placeholder content for missing critical files
                print(f"🔍 Checking if '{filename}' is a critical file...")
                if filename == 'index-C_NHaPTA.js':
                    print(f"✅ MATCH: Returning placeholder for {filename}")
                    return "console.log('TEST: Placeholder JS loaded');", 200, {'Content-Type': 'application/javascript'}
                
                elif filename == 'index-CiVy6UYJ.css':
                    print(f"✅ MATCH: Returning placeholder for {filename}")
                    return "/* TEST: Placeholder CSS */ body { background: red; }", 200, {'Content-Type': 'text/css'}
                
                print(f"🔍 '{filename}' is not a critical file")
                
                print(f"🔍 '{filename}' is not a critical file, proceeding with not found")
                
                print(f"❌ Asset not found: {filename}")
                print(f"❌ Searched in: {assets_dir} and {fallback_dir}")
                return f"Asset not found: {filename}", 404
            except Exception as e:
                print(f"❌ Error serving asset {filename}: {e}")
                return f"Error: {str(e)}", 500

        @app.route('/<path:path>')
        def serve_frontend(path):
            print(f"🎯 Frontend request for path: {path}")
            
            try:
                # Try to serve as static file first
                try:
                    return app.send_static_file(path)
                except:
                    pass
                
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
        static_folder = app.config.get('STATIC_FOLDER', 'not set')
        frontend_folder = app.config.get('FRONTEND_FOLDER', 'not set')
        
        # Check if directories exist
        static_exists = os.path.exists(static_folder) if static_folder != 'not set' else False
        frontend_exists = os.path.exists(frontend_folder) if frontend_folder != 'not set' else False
        
        # Check assets directory
        assets_dir = os.path.join(static_folder, 'assets') if static_folder != 'not set' else 'not set'
        assets_exists = os.path.exists(assets_dir) if assets_dir != 'not set' else False
        
        # List files if directories exist
        static_files = os.listdir(static_folder) if static_exists else []
        assets_files = os.listdir(assets_dir) if assets_exists else []
        
        return {
            "status": "debug",
            "working_directory": os.getcwd(),
            "static_folder": static_folder,
            "static_exists": static_exists,
            "static_files": static_files[:10],  # First 10 files
            "frontend_folder": frontend_folder,
            "frontend_exists": frontend_exists,
            "assets_dir": assets_dir,
            "assets_exists": assets_exists,
            "assets_files": assets_files[:5] if len(assets_files) > 0 else [],  # First 5 asset files
            "python_path": sys.path[:5],  # First 5 paths
            "database_uri": app.config.get('SQLALCHEMY_DATABASE_URI', 'not set')[:50] + "..." if app.config.get('SQLALCHEMY_DATABASE_URI') else 'not set'
        }, 200

    print("✅ Flask app created successfully!")
    return app

if __name__ == '__main__':
    # Create app instance only when running directly
    application = create_app()
    # Use a production-ready server like Gunicorn or Waitress instead of app.run in production
    port = int(os.environ.get('PORT', 8080))  # Match the start.sh default
    application.run(debug=True, host='0.0.0.0', port=port)
