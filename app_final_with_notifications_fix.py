# backend/app.py

import sys
import os
# Add the backend directory to Python path  
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_dir)

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
        app.config['SQLALCHEMY_DATABASE_URI'] = (
            'postgresql://super:Picklehead1!@JoeRyanMBA-4757.postgres.pythonanywhere-services.com:14757/structured_docs'
        )
        
        # Local SQLite fallback for development (uncomment if PostgreSQL not accessible)
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
        from backend.models import db
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
            from backend.models import Topic
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
            from backend.models import Project
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
            from backend.models import Collection
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
            from backend.models import User
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

    # Login endpoint
    @app.route('/api/users/login', methods=['POST'])
    def api_login():
        try:
            from backend.models import User, Tag
            from werkzeug.security import check_password_hash
            from flask_jwt_extended import create_access_token
            
            data = request.get_json()
            # Normalize input to avoid case/whitespace mismatches
            email = (data.get('email') or '').strip().lower()
            password = data.get('password', None)

            user = User.query.filter_by(email=email).first()
            # Fail fast if no user or no password set
            if not user or not user.password_hash:
                return jsonify({"msg": "Bad email or password"}), 401

            try:
                if check_password_hash(user.password_hash, password):
                    access_token = create_access_token(identity=user.id)
                    return jsonify(access_token=access_token, user=user.to_dict())
            except Exception as e:
                # Avoid 500s on malformed hashes; treat as invalid credentials
                print(f"❌ Login error for {email}: {e}")
            return jsonify({"msg": "Bad email or password"}), 401
        except Exception as e:
            return jsonify({'error': str(e), 'message': 'Login failed'}), 500

    @app.route('/api/stakeholders', methods=['GET'])
    @app.route('/api/stakeholders/', methods=['GET'])
    def api_list_stakeholders():
        try:
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

    # Additional API endpoints your frontend needs
    @app.route('/api/notifications', methods=['GET'])
    def api_list_notifications():
        try:
            from backend.models import Notification
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
            from backend.models import Project, Topic, User, Task, Stakeholder, Tag
            
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

    # Tags endpoints
    @app.route('/api/tags', methods=['GET'])
    def api_tags():
        """Get all tags"""
        try:
            from backend.models import Tag
            tags = Tag.query.order_by(Tag.name).all()
            return jsonify([tag.to_dict() for tag in tags])
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/tags', methods=['POST'])
    def api_create_tag():
        """Create a new tag"""
        try:
            from backend.models import Tag
            data = request.get_json()
            
            if not data.get('name'):
                return jsonify({"error": "Tag name is required"}), 400
                
            name = data['name'].strip()
            if not name:
                return jsonify({"error": "Tag name cannot be empty"}), 400
                
            # Check if tag already exists
            existing_tag = Tag.query.filter_by(name=name).first()
            if existing_tag:
                return jsonify({"error": "Tag already exists"}), 400
                
            tag = Tag(name=name)
            db.session.add(tag)
            db.session.commit()
            
            return jsonify(tag.to_dict()), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    @app.route('/api/tags/<int:tag_id>', methods=['PUT'])
    def api_update_tag(tag_id):
        """Update a tag"""
        try:
            from backend.models import Tag
            tag = Tag.query.get_or_404(tag_id)
            data = request.get_json()
            
            if not data.get('name'):
                return jsonify({"error": "Tag name is required"}), 400
                
            name = data['name'].strip()
            if not name:
                return jsonify({"error": "Tag name cannot be empty"}), 400
                
            # Check if another tag with this name exists
            existing_tag = Tag.query.filter_by(name=name).first()
            if existing_tag and existing_tag.id != tag_id:
                return jsonify({"error": "Tag already exists"}), 400
                
            tag.name = name
            db.session.commit()
            
            return jsonify(tag.to_dict())
            
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    @app.route('/api/tags/<int:tag_id>', methods=['DELETE'])
    def api_delete_tag(tag_id):
        """Delete a tag"""
        try:
            from backend.models import Tag
            tag = Tag.query.get_or_404(tag_id)
            db.session.delete(tag)
            db.session.commit()
            
            return jsonify({"message": "Tag deleted successfully"})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    @app.route('/api/import/history', methods=['GET'])
    def api_import_history():
        return jsonify([])  # Return empty array for now

    # Feedback API endpoints
    @app.route('/api/feedback', methods=['GET'])
    def api_get_feedback():
        """Get all feedback reports"""
        try:
            from backend.models import FeedbackReport
            feedback_reports = FeedbackReport.query.order_by(FeedbackReport.created_at.desc()).all()
            return jsonify([report.to_dict() for report in feedback_reports])
        except Exception as e:
            return jsonify({'error': str(e), 'message': 'Error fetching feedback'}), 500

    @app.route('/api/feedback', methods=['POST'])
    def api_create_feedback():
        """Create a new feedback report"""
        from backend.models import db
        
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
                
            # Map frontend fields to database fields
            feedback_type = data.get('type', 'other')
            if feedback_type == 'general':
                feedback_type = 'other'  # Map general to other
            elif feedback_type == 'praise':
                feedback_type = 'other'  # Map praise to other
            elif feedback_type not in ['suggestion', 'bug', 'other']:
                feedback_type = 'other'  # Default to other for unknown types
            
            # Use raw SQL to insert the feedback report
            from sqlalchemy import text
            with db.engine.connect() as connection:
                sql = text("""
                INSERT INTO feedback_reports (report_type, page, message, status)
                VALUES (:report_type, :page, :message, :status)
                RETURNING id
                """)
                
                result = connection.execute(sql, {
                    'report_type': feedback_type,
                    'page': data.get('page', ''),
                    'message': data.get('message', ''),
                    'status': 'new'
                })
                
                feedback_id = result.fetchone()[0]
                connection.commit()
            
            return jsonify({
                'message': 'Feedback submitted successfully',
                'id': feedback_id
            }), 201
            
        except Exception as e:
            # Note: We don't use db.session.rollback() here since we're using raw SQL
            return jsonify({'error': str(e), 'message': 'Error creating feedback'}), 500

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
    import argparse
    parser = argparse.ArgumentParser(description='Run Flask app')
    parser.add_argument('--port', type=int, default=5050, help='Port to run the app on')
    args = parser.parse_args()
    
    print("🏗️ Creating app instance for development...")
    app = create_app()
    print("✅ App instance created successfully!")
    print(f"🚀 Starting Flask development server on port {args.port}...")
    app.run(host='0.0.0.0', port=args.port, debug=True)
else:
    # For WSGI and imports, don't create the app instance here
    print("📝 Module imported - app instance will be created by WSGI or caller")