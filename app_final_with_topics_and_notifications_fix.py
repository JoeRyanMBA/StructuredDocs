# backend/app.py

import sys
import os
# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, send_from_directory, send_file, request
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

    # Task API endpoints
    @app.route('/api/tasks', methods=['GET'])
    @app.route('/api/tasks/', methods=['GET'])
    def api_list_tasks():
        try:
            from models import Task
            # Query parameters for filtering
            status = request.args.get('status')
            priority = request.args.get('priority')
            project_id = request.args.get('project_id', type=int)
            collection_id = request.args.get('collection_id', type=int)
            topic_id = request.args.get('topic_id', type=int)
            assigned_to = request.args.get('assigned_to')
            search = request.args.get('search', '').strip()
            page = request.args.get('page', 1, type=int)
            per_page = min(request.args.get('per_page', 50, type=int), 100)

            # Build query
            query = Task.query

            # Apply filters
            if status:
                query = query.filter(Task.status == status)
            if priority:
                query = query.filter(Task.priority == priority)
            if project_id:
                query = query.filter(Task.project_id == project_id)
            if collection_id:
                query = query.filter(Task.collection_id == collection_id)
            if topic_id:
                query = query.filter(Task.topic_id == topic_id)
            if assigned_to:
                query = query.filter(Task.assigned_to.contains(assigned_to))
            if search:
                query = query.filter(Task.title.contains(search) | Task.description.contains(search))

            # Paginate results
            tasks = query.order_by(Task.created_at.desc()).limit(per_page).offset((page - 1) * per_page).all()
            
            return jsonify([{
                'id': t.id,
                'title': t.title,
                'description': t.description,
                'status': t.status,
                'priority': t.priority,
                'project_id': t.project_id,
                'collection_id': t.collection_id,
                'topic_id': t.topic_id,
                'assigned_to': t.assigned_to,
                'due_date': t.due_date.isoformat() if hasattr(t, 'due_date') and t.due_date else None,
                'created_at': t.created_at.isoformat() if hasattr(t, 'created_at') and t.created_at else None,
                'updated_at': t.updated_at.isoformat() if hasattr(t, 'updated_at') and t.updated_at else None
            } for t in tasks])
        except Exception as e:
            return jsonify({'error': str(e), 'message': 'Error fetching tasks'}), 500

    @app.route('/api/tasks/summary', methods=['GET'])
    def api_tasks_summary():
        try:
            from models import Task
            
            # Get task counts by status
            pending = Task.query.filter_by(status='pending').count()
            in_progress = Task.query.filter_by(status='in_progress').count()
            completed = Task.query.filter_by(status='completed').count()
            on_hold = Task.query.filter_by(status='on_hold').count()
            
            # Get priority counts
            high_priority = Task.query.filter_by(priority='high').count()
            medium_priority = Task.query.filter_by(priority='medium').count()
            low_priority = Task.query.filter_by(priority='low').count()
            
            return jsonify({
                'status_counts': {
                    'pending': pending,
                    'in_progress': in_progress,
                    'completed': completed,
                    'on_hold': on_hold
                },
                'priority_counts': {
                    'high': high_priority,
                    'medium': medium_priority,
                    'low': low_priority
                },
                'total': pending + in_progress + completed + on_hold
            })
        except Exception as e:
            return jsonify({'error': str(e), 'message': 'Error fetching task summary'}), 500

    @app.route('/api/tasks/tags', methods=['GET'])
    def api_list_task_tags():
        try:
            from models import Tag
            tags = Tag.query.limit(100).all()
            return jsonify([{
                'id': t.id,
                'name': t.name,
                'color': getattr(t, 'color', '#3498db'),
                'description': getattr(t, 'description', ''),
                'created_at': t.created_at.isoformat() if hasattr(t, 'created_at') and t.created_at else None
            } for t in tags])
        except Exception as e:
            return jsonify({'error': str(e), 'message': 'Error fetching tags'}), 500

    @app.route('/api/tasks/associations', methods=['GET'])
    def api_task_associations():
        try:
            from models import Task, Project, Collection, Topic
            
            # Get associations count
            tasks_with_projects = Task.query.filter(Task.project_id.isnot(None)).count()
            tasks_with_collections = Task.query.filter(Task.collection_id.isnot(None)).count()
            tasks_with_topics = Task.query.filter(Task.topic_id.isnot(None)).count()
            
            return jsonify({
                'projects': tasks_with_projects,
                'collections': tasks_with_collections,
                'topics': tasks_with_topics,
                'total_tasks': Task.query.count()
            })
        except Exception as e:
            return jsonify({'error': str(e), 'message': 'Error fetching task associations'}), 500

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