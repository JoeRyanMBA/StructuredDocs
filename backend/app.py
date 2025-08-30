# backend/app.py

import sys
import os
from flask import Flask, jsonify, send_from_directory, send_file
from flask_cors import CORS
from .extensions import db, migrate, jwt
from urllib.parse import urlparse

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

def create_app():
    print("🚀 Creating Flask app...")
    
    # Load environment variables from .env file
    load_env_file()
    
    app = Flask(__name__, instance_relative_config=True)
    print("📱 Flask instance created")
    
    # Load configuration
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
        # Default local development database
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(app.instance_path, 'structured_docs.db')}"

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

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # Configure CORS
    frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
    CORS(app, resources={r"/*": {"origins": frontend_url}}, supports_credentials=True)

    with app.app_context():
        # Import models to ensure they are registered with SQLAlchemy
        from backend import models
        # Force mapper configuration
        from sqlalchemy.orm import configure_mappers
        configure_mappers()
        
        # Reload email service configuration with loaded environment variables
        from backend.utils.email_service import email_service
        email_service.reload_config()
        
        # Import and register blueprints (skippable for migrations/CLI)
        # Support selective enabling via ENABLE_BLUEPRINTS env var (comma-separated short names)
        # or via a file path provided in ENABLE_BLUEPRINTS_FILE. Reading from a file
        # is more reliable when uWSGI runs multiple Python sub-interpreters.
        # - If ENABLE_BLUEPRINTS_FILE exists and contains a comma-separated list, use that.
        # - Else if ENABLE_BLUEPRINTS env var is set, use that.
        # - Else if SKIP_BLUEPRINTS=="1", skip all blueprint registration.
        enable_list = None
        eb_file = os.environ.get('ENABLE_BLUEPRINTS_FILE')
        if eb_file and os.path.exists(eb_file):
            try:
                with open(eb_file, 'r') as _f:
                    enable_list = _f.read().strip()
            except Exception as _e:
                print(f"⚠️ Could not read ENABLE_BLUEPRINTS_FILE '{eb_file}': {_e}")
        # Diagnostic: print which source we're reading so logs indicate visibility
        try:
            print(f"DEBUG: ENABLE_BLUEPRINTS_FILE env -> {os.environ.get('ENABLE_BLUEPRINTS_FILE')}")
            exists = eb_file and os.path.exists(eb_file)
            print(f"DEBUG: ENABLE_BLUEPRINTS_FILE exists -> {exists}")
            if exists:
                try:
                    with open(eb_file, 'r') as _f2:
                        print(f"DEBUG: ENABLE_BLUEPRINTS_FILE contents -> '{_f2.read().strip()}'")
                except Exception as _e2:
                    print(f"DEBUG: error reading file for debug: {_e2}")
        except Exception:
            pass
        if not enable_list:
            enable_list = os.environ.get('ENABLE_BLUEPRINTS')
        if enable_list:
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
            import importlib
            for name in requested:
                if name not in blueprint_map:
                    print(f"\u26a0\ufe0f ENABLE_BLUEPRINTS: unknown blueprint '{name}' - skipping")
                    continue
                module_name, attr = blueprint_map[name]
                try:
                    mod = importlib.import_module(f'backend.routes.{module_name}')
                    bp = getattr(mod, attr)
                    app.register_blueprint(bp)
                    print(f"\u2705 Registered blueprint '{name}' from backend.routes.{module_name}.{attr}")
                except Exception as _e:
                    print(f"\u274c Error registering blueprint '{name}': {_e}")
        elif os.environ.get('SKIP_BLUEPRINTS') == '1':
            print("\u23ed\ufe0f  SKIP_BLUEPRINTS=1 set; skipping blueprint imports/registration (useful for migrations).")
        else:
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

        @app.route('/api/health', methods=['GET'])
        def health_check():
            uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
            if uri.startswith('sqlite'):
                db_kind = 'sqlite'
            else:
                parsed = urlparse(uri)
                db_kind = parsed.scheme or 'unknown'
            return jsonify({
                'status': 'ok',
                'db': db_kind,
                'frontend_origin': os.environ.get('FRONTEND_URL', 'http://localhost:5173')
            }), 200

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
            return send_from_directory(os.path.join(app.config['STATIC_FOLDER'], 'images'), filename)

        @app.route('/', defaults={'path': ''})
        @app.route('/<path:path>')
        def serve_frontend(path):
            if path != "" and os.path.exists(os.path.join(app.config['FRONTEND_FOLDER'], path)):
                return send_from_directory(app.config['FRONTEND_FOLDER'], path)
            else:
                return send_from_directory(app.config['FRONTEND_FOLDER'], 'index.html')

    return app

if __name__ == '__main__':
    # Create app instance only when running directly
    application = create_app()
    # Use a production-ready server like Gunicorn or Waitress instead of app.run in production
    application.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5050)))
