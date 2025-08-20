# backend/app.py

import sys
import os
# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, send_from_directory, send_file
from flask_cors import CORS
from flask_migrate import Migrate

def create_app():

    print("🚀 Creating Flask app...")
    app = Flask(__name__)
    print("📱 Flask instance created")
    
    try:
        # enable CORS and debug mode with comprehensive settings
        CORS(app, 
             origins="*", 
             allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin"], 
             methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"], 
             supports_credentials=False,
             send_wildcard=True,
             vary_header=False)
        
        # Configure SQLAlchemy database URI - environment aware
        if os.environ.get('PYTHONANYWHERE_ENVIRONMENT'):
            # PythonAnywhere PostgreSQL configuration
            app.config['SQLALCHEMY_DATABASE_URI'] = (
                'postgresql://super:Picklehead1!@JoeRyanMBA-4757.postgres.pythonanywhere-services.com:14757/structured_docs'
            )
            print("🐘 Using PostgreSQL database for PythonAnywhere")
        else:
            # Local development SQLite configuration
            db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'instance', 'structured_docs.db')
            app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
            print(f"🗄️ Using SQLite database for local development: {db_path}")
        
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False        # Local SQLite fallback for development (uncomment if PostgreSQL not accessible)
        # sqlite_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'structured_docs.db')
        # app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{sqlite_path}'
        
        # Configure JWT secret key (required for Flask-JWT-Extended)
        app.config['JWT_SECRET_KEY'] = 'your-secret-key-change-in-production'  # Change this in production!
        
        # Additional Flask configurations
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SECRET_KEY'] = 'your-flask-secret-key-change-in-production'  # Change this in production!
        
        # Configure static files for image serving
        app.config['STATIC_FOLDER'] = os.path.join(app.root_path, 'static')
        
        # Configure frontend files path (adjust this path on PythonAnywhere)
        app.config['FRONTEND_FOLDER'] = '/home/JoeRyanMBA/StructuredDocs/frontend/dist'
        
        # Initialize SQLAlchemy
        from models import db
        db.init_app(app)
        print("📊 Database initialized")

        # Register Flask-Migrate
        from flask_migrate import Migrate
        migrate = Migrate(app, db)
        print("🔄 Flask-Migrate configured")
        
        # Initialize JWT
        from flask_jwt_extended import JWTManager
        jwt = JWTManager(app)
        print("🔐 JWT Manager initialized")
        
        # Register API blueprints
        print("📋 Registering API blueprints...")
        
        # Import and register metrics blueprint
        try:
            from routes.metrics import metrics_bp
            app.register_blueprint(metrics_bp)
            print("✅ Metrics blueprint registered")
        except Exception as e:
            print(f"⚠️ Error registering metrics blueprint: {e}")
        
        # Import and register admin blueprint
        try:
            from routes.admin import admin_bp
            app.register_blueprint(admin_bp)
            print("✅ Admin blueprint registered")
        except Exception as e:
            print(f"⚠️ Error registering admin blueprint: {e}")
        
        # Import and register other blueprints
        try:
            from routes.stakeholders import stakeholders_bp
            app.register_blueprint(stakeholders_bp)
            print("✅ Stakeholders blueprint registered")
        except Exception as e:
            print(f"⚠️ Error registering stakeholders blueprint: {e}")
            
        try:
            from routes.projects import projects_bp
            app.register_blueprint(projects_bp)
            print("✅ Projects blueprint registered")
        except Exception as e:
            print(f"⚠️ Error registering projects blueprint: {e}")
            
        try:
            from routes.collections import collections_bp
            app.register_blueprint(collections_bp)
            print("✅ Collections blueprint registered")
        except Exception as e:
            print(f"⚠️ Error registering collections blueprint: {e}")
            
        try:
            from routes.tasks import tasks_bp
            app.register_blueprint(tasks_bp)
            print("✅ Tasks blueprint registered")
        except Exception as e:
            print(f"⚠️ Error registering tasks blueprint: {e}")
            
        try:
            from routes.topics import topics_bp
            app.register_blueprint(topics_bp)
            print("✅ Topics blueprint registered")
        except Exception as e:
            print(f"⚠️ Error registering topics blueprint: {e}")
            
        try:
            from routes.users import users_bp
            app.register_blueprint(users_bp)
            print("✅ Users blueprint registered")
        except Exception as e:
            print(f"⚠️ Error registering users blueprint: {e}")
            
        try:
            from routes.notifications import notifications_bp
            app.register_blueprint(notifications_bp)
            print("✅ Notifications blueprint registered")
        except Exception as e:
            print(f"⚠️ Error registering notifications blueprint: {e}")
            
        try:
            from routes.reviews import reviews_bp
            app.register_blueprint(reviews_bp)
            print("✅ Reviews blueprint registered")
        except Exception as e:
            print(f"⚠️ Error registering reviews blueprint: {e}")
            
        print("📋 Blueprint registration complete")
        
    except Exception as e:
        print(f"❌ Configuration error: {str(e)}")
        raise

    # Add explicit CORS handling middleware
    @app.before_request
    def handle_preflight():
        from flask import request
        if request.method == "OPTIONS":
            print(f"🔍 OPTIONS request from origin: {request.headers.get('Origin')}")
            response = jsonify({})
            response.headers.add("Access-Control-Allow-Origin", "*")
            response.headers.add('Access-Control-Allow-Headers', "*")
            response.headers.add('Access-Control-Allow-Methods', "*")
            return response

    @app.after_request
    def after_request(response):
        from flask import request
        print(f"🔍 Request from origin: {request.headers.get('Origin')} - Response: {response.status_code}")
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
        return response

    @app.route('/ping', methods=['GET'])
    def ping():
        print("🏓 Ping endpoint called")
        return jsonify({"status": "ok"}), 200

    @app.route('/test', methods=['GET'])
    def test():
        print("🧪 Test endpoint called")
        return jsonify({"message": "test successful"}), 200

    # Static file serving for imported images
    @app.route('/images/<path:filename>')
    def serve_image(filename):
        """Serve imported images from static directory"""
        try:
            static_images_dir = os.path.join(app.config['STATIC_FOLDER'], 'images')
            return send_from_directory(static_images_dir, filename)
        except Exception as e:
            app.logger.error(f"Error serving image {filename}: {str(e)}")
            return jsonify({'error': 'Image not found'}), 404

    # Frontend static file serving
    @app.route('/assets/<path:filename>')
    def serve_frontend_assets(filename):
        """Serve frontend assets (CSS, JS, etc.)"""
        try:
            assets_dir = os.path.join(app.config['FRONTEND_FOLDER'], 'assets')
            return send_from_directory(assets_dir, filename)
        except Exception as e:
            return jsonify({'error': 'Asset not found'}), 404

    # API Routes - all under /api prefix
    @app.route('/api/ping', methods=['GET'])
    def api_ping():
        return jsonify({"status": "ok"}), 200

    @app.route('/api/test', methods=['GET'])
    def api_test():
        return jsonify({
            "message": "test successful", 
            "version": "2025-08-19-v2",
            "timestamp": "2025-08-19 20:45:00"
        }), 200

    @app.route('/api/debug', methods=['GET'])
    def api_debug():
        return jsonify({
            "message": "debug endpoint working",
            "version": "2025-08-19-v2",
            "app_config": {
                "database_configured": bool(app.config.get('SQLALCHEMY_DATABASE_URI')),
                "jwt_configured": bool(app.config.get('JWT_SECRET_KEY')),
                "cors_enabled": True
            }
        }), 200

    @app.route('/api/topics', methods=['GET'])
    @app.route('/api/topics/', methods=['GET'])
    def api_list_topics():
        try:
            from models import Topic
            topics = Topic.query.limit(50).all()
            return jsonify([{
                'id': t.id,
                'title': t.title,
                'content': t.content[:200] if t.content else '',
                'created_at': t.created_at.isoformat() if hasattr(t, 'created_at') and t.created_at else None
            } for t in topics])
        except Exception as e:
            return jsonify({'error': str(e), 'message': 'Error fetching topics'}), 500

    @app.route('/api/projects', methods=['GET'])
    @app.route('/api/projects/', methods=['GET'])
    def api_list_projects():
        try:
            from models import Project
            projects = Project.query.limit(50).all()
            return jsonify([{
                'id': p.id,
                'name': p.name,
                'description': p.description,
                'created_at': p.created_at.isoformat() if hasattr(p, 'created_at') and p.created_at else None
            } for p in projects])
        except Exception as e:
            return jsonify({'error': str(e), 'message': 'Error fetching projects'}), 500

    @app.route('/api/collections', methods=['GET'])
    @app.route('/api/collections/', methods=['GET'])
    def api_list_collections():
        try:
            from models import Collection
            collections = Collection.query.limit(50).all()
            return jsonify([{
                'id': c.id,
                'name': c.name,
                'description': c.description,
                'created_at': c.created_at.isoformat() if hasattr(c, 'created_at') and c.created_at else None
            } for c in collections])
        except Exception as e:
            return jsonify({'error': str(e), 'message': 'Error fetching collections'}), 500

    @app.route('/api/users', methods=['GET'])
    def api_list_users():
        try:
            from models import User
            users = User.query.limit(50).all()
            return jsonify([{
                'id': u.id,
                'name': u.name,
                'email': u.email,
                'role': u.role,
                'active': u.active
            } for u in users])
        except Exception as e:
            return jsonify({'error': str(e), 'message': 'Error fetching users'}), 500

    @app.route('/api/stakeholders', methods=['GET'])
    @app.route('/api/stakeholders/', methods=['GET'])
    def api_list_stakeholders():
        try:
            from models import Stakeholder
            stakeholders = Stakeholder.query.limit(50).all()
            return jsonify([{
                'id': s.id,
                'name': s.name,
                'email': s.email,
                # Remove 'role' since it doesn't exist in the model
                'project_id': getattr(s, 'project_id', None),
                'created_at': s.created_at.isoformat() if hasattr(s, 'created_at') and s.created_at else None
            } for s in stakeholders])
        except Exception as e:
            return jsonify({'error': str(e), 'message': 'Error fetching stakeholders'}), 500

    # Additional API endpoints your frontend needs
    @app.route('/api/notifications', methods=['GET'])
    def api_list_notifications():
        try:
            from models import Notification
            notifications = Notification.query.limit(50).all()
            return jsonify([{
                'id': n.id,
                'message': n.message,
                'type': getattr(n, 'type', 'info'),
                'created_at': n.date.isoformat() if hasattr(n, 'date') and n.date else None
            } for n in notifications])
        except Exception as e:
            # Return empty array if no notifications table
            return jsonify([])

    @app.route('/api/dashboard/stats', methods=['GET'])
    def api_dashboard_stats():
        try:
            from models import Project, Topic, User, Task, Stakeholder
            
            # Safely get counts with fallbacks
            projects_count = 0
            topics_count = 0
            users_count = 0
            tasks_count = 0
            stakeholders_count = 0
            
            try:
                projects_count = Project.query.count()
            except:
                projects_count = 0
                
            try:
                topics_count = Topic.query.count()
            except:
                topics_count = 0
                
            try:
                users_count = User.query.count()
            except:
                users_count = 0
                
            try:
                tasks_count = Task.query.count()
            except:
                tasks_count = 0
                
            try:
                stakeholders_count = Stakeholder.query.count()
            except:
                stakeholders_count = 0
            
            stats = {
                'projects': {'total': projects_count},
                'topics': {'total': topics_count},
                'users': {'total': users_count},
                'tasks': {'total': tasks_count},
                'stakeholders': {'total': stakeholders_count}
            }
            return jsonify(stats)
        except Exception as e:
            # Return safe fallback data
            return jsonify({
                'projects': {'total': 0},
                'topics': {'total': 0},
                'users': {'total': 0},
                'tasks': {'total': 0},
                'stakeholders': {'total': 0}
            })

    @app.route('/api/dashboard/pending-actions', methods=['GET'])
    def api_dashboard_pending_actions():
        return jsonify([])  # Return empty array for now

    @app.route('/api/import/history', methods=['GET'])
    def api_import_history():
        return jsonify([])  # Return empty array for now

    # Catch-all route to serve the frontend - TEMPORARILY DISABLED
    # @app.route('/')
    # @app.route('/<path:path>')
    # def serve_frontend(path=''):
    #     """Serve the Vue.js frontend application"""
    #     try:
    #         # If path is a file request, try to serve it
    #         if path and '.' in path:
    #             return send_from_directory(app.config['FRONTEND_FOLDER'], path)
    #         # Otherwise serve index.html for Vue router
    #         return send_file(os.path.join(app.config['FRONTEND_FOLDER'], 'index.html'))
    #     except Exception as e:
    #         return jsonify({'error': 'Frontend not found', 'details': str(e)}), 404

    # Root route and catch-all for frontend routing
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path=''):
        """Serve the frontend application for all non-API routes"""
        # API routes should be handled by their specific endpoints
        if path.startswith('api/'):
            return jsonify({"error": "API endpoint not found"}), 404
            
        # For any other route, serve the frontend index.html
        frontend_index = os.path.join(app.config['FRONTEND_FOLDER'], 'index.html')
        if os.path.exists(frontend_index):
            return send_file(frontend_index)
        else:
            # Fallback if frontend files aren't deployed yet
            return jsonify({
                "message": "StructuredDocs API is running!",
                "status": "online",
                "note": "Frontend files not yet deployed. Upload frontend/dist/* to /home/JoeRyanMBA/StructuredDocs/frontend/dist/",
                "database": "PostgreSQL connected",
                "endpoints": {
                    "ping": "/api/ping",
                    "test": "/api/test",
                    "topics": "/api/topics", 
                    "projects": "/api/projects",
                    "stakeholders": "/api/stakeholders",
                    "dashboard_stats": "/api/dashboard/stats"
                }
            })
    
    # Error handler for JWT errors
    from flask_jwt_extended.exceptions import NoAuthorizationError, InvalidHeaderError

    @app.errorhandler(NoAuthorizationError)
    def handle_no_auth_error(e):
        return jsonify({"error": "Missing or invalid JWT token."}), 401

    @app.errorhandler(InvalidHeaderError)
    def handle_invalid_header_error(e):
        return jsonify({"error": "Invalid JWT header."}), 422
        
    return app

# instantiate Flask app only when running directly
if __name__ == '__main__':
    print("🏗️ Creating app instance for development...")
    app = create_app()
    print("✅ App instance created successfully!")
    print("🚀 Starting Flask development server...")
    app.run(host='0.0.0.0', port=5050, debug=True)
else:
    # For WSGI and imports, don't create the app instance here
    print("📝 Module imported - app instance will be created by WSGI or caller")