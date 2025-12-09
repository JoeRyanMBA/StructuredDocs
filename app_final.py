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
        
        # Configure SQLAlchemy database URI for PostgreSQL
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
            'DATABASE_URL',
            'postgresql://user:password@host:5432/structured_docs'
        )
        
        # Configure JWT secret key (required for Flask-JWT-Extended)
        app.config['JWT_SECRET_KEY'] = 'your-secret-key-change-in-production'  # Change this in production!
        
        # Additional Flask configurations
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SECRET_KEY'] = 'your-flask-secret-key-change-in-production'  # Change this in production!
        
        # Configure static files for image serving
        app.config['STATIC_FOLDER'] = os.path.join(app.root_path, 'static')
        
        # Configure frontend files path (override via FRONTEND_DIST if needed)
        app.config['FRONTEND_FOLDER'] = os.environ.get(
            'FRONTEND_DIST',
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend', 'dist')
        )
        
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
    def api_list_stakeholders():
        try:
            try:
                from models import Stakeholder
            except Exception:
                from backend.models import Stakeholder
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

    @app.route('/api/projects/<int:project_id>/stakeholders', methods=['GET'])
    def api_get_project_stakeholders(project_id: int):
        try:
            try:
                from models import ProjectStakeholder
            except Exception:
                from backend.models import ProjectStakeholder

            items = (ProjectStakeholder.query
                     .filter(ProjectStakeholder.project_id == project_id)
                     .all())
            return jsonify([i.to_dict() for i in items]), 200
        except Exception as e:
            return jsonify({'error': str(e), 'message': 'Error fetching project stakeholders'}), 500

    @app.route('/api/projects/<int:project_id>/stakeholders', methods=['POST'])
    def api_add_project_stakeholder(project_id: int):
        from flask import request
        try:
            try:
                from models import db, Stakeholder, ProjectStakeholder
            except Exception:
                from backend.models import db, Stakeholder, ProjectStakeholder

            data = request.get_json(force=True) or {}
            name = data.get('name')
            email = data.get('email')
            role_input = (data.get('role') or 'stakeholder')
            # Normalize role to backend enum values
            role_map = {
                'project manager': 'project_manager',
                'pm': 'project_manager',
                'sponsor': 'sponsor',
                'subject matter expert': 'subject_matter_expert',
                'sme': 'subject_matter_expert',
                'reviewer': 'reviewer',
                'stakeholder': 'stakeholder'
            }
            normalized = role_input.strip().lower().replace('-', ' ').replace('_', ' ')
            role = role_map.get(normalized, normalized.replace(' ', '_'))
            can_review = bool(data.get('can_review', True))
            notes = data.get('notes')

            if not name or not email:
                return jsonify({'error': 'name and email are required'}), 400

            stakeholder = Stakeholder.query.filter(Stakeholder.email == email).first()
            if not stakeholder:
                stakeholder = Stakeholder(name=name, email=email, can_review=can_review)
                db.session.add(stakeholder)
                db.session.flush()  # ensure id

            # Check for existing association
            existing = (ProjectStakeholder.query
                        .filter(ProjectStakeholder.project_id == project_id,
                                ProjectStakeholder.stakeholder_id == stakeholder.id)
                        .first())
            if existing:
                # Update fields if provided
                existing.role = role or existing.role
                existing.can_review = can_review
                existing.notes = notes or existing.notes
                db.session.commit()
                return jsonify(existing.to_dict()), 200

            assoc = ProjectStakeholder(
                project_id=project_id,
                stakeholder_id=stakeholder.id,
                role=role,
                can_review=can_review,
                notes=notes
            )
            db.session.add(assoc)
            db.session.commit()
            return jsonify(assoc.to_dict()), 201
        except Exception as e:
            try:
                from backend.models import db as _db
                _db.session.rollback()
            except Exception:
                pass
            return jsonify({'error': str(e), 'message': 'Error adding project stakeholder'}), 500

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
                'created_at': n.created_at.isoformat() if hasattr(n, 'created_at') and n.created_at else None
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

    @app.route('/api/projects/', methods=['GET'])
    def api_projects_with_slash():
        return api_list_projects()  # Redirect to main projects endpoint

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