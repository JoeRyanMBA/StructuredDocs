# backend/app.py

import sys
import os
# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_migrate import Migrate

def create_app():

    print("🚀 Creating Flask app...")
    app = Flask(__name__)
    print("📱 Flask instance created")
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
    
    # Configure static files for image serving
    app.config['STATIC_FOLDER'] = os.path.join(app.root_path, 'static')
    
    # Initialize SQLAlchemy
    from models import db
    db.init_app(app)

    # Register Flask-Migrate
    from flask_migrate import Migrate
    migrate = Migrate(app, db)

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

    # Import blueprints before registration
    from routes.topics         import topics  as topics_bp
    from routes.import_handler import imports as imports_bp
    from routes.publications   import pubs_bp
    from routes.collections    import collections_bp
    from routes.reviews        import reviews_bp
    from routes.projects       import projects_bp
    from routes.users          import users_bp
    from routes.metrics        import metrics_bp
    from routes.notifications  import notifications_bp
    from routes.links          import links_bp
    from routes.stakeholders   import stakeholders_bp
    from routes.tasks          import tasks_bp
    from routes.tags           import tags_bp
    from routes.milestones     import milestones_bp
    from routes.images         import images_bp
    from routes.dashboard      import bp as dashboard_bp
    from routes.admin          import admin_bp
    from routes.review_tokens  import review_tokens_bp
    from routes.sequences      import sequences_bp

    # Register all blueprints once
    print("📋 Registering blueprints...")
    app.register_blueprint(topics_bp)
    print("  ✅ Topics blueprint registered")
    app.register_blueprint(imports_bp)
    print("  ✅ Imports blueprint registered")
    app.register_blueprint(pubs_bp)
    print("  ✅ Publications blueprint registered")
    app.register_blueprint(collections_bp)
    print("  ✅ Collections blueprint registered")
    app.register_blueprint(reviews_bp)
    print("  ✅ Reviews blueprint registered")
    app.register_blueprint(projects_bp)
    print("  ✅ Projects blueprint registered")
    app.register_blueprint(users_bp)
    print("  ✅ Users blueprint registered")
    app.register_blueprint(metrics_bp)
    print("  ✅ Metrics blueprint registered")
    app.register_blueprint(notifications_bp)
    print("  ✅ Notifications blueprint registered")
    app.register_blueprint(links_bp)
    print("  ✅ Links blueprint registered")
    app.register_blueprint(stakeholders_bp)
    print("  ✅ Stakeholders blueprint registered")
    app.register_blueprint(tasks_bp)
    print("  ✅ Tasks blueprint registered")
    app.register_blueprint(tags_bp)
    print("  ✅ Tags blueprint registered")
    app.register_blueprint(milestones_bp)
    print("  ✅ Milestones blueprint registered")

    app.register_blueprint(images_bp)
    print("  ✅ Images blueprint registered")
    app.register_blueprint(dashboard_bp)
    print("  ✅ Dashboard blueprint registered")
    app.register_blueprint(admin_bp)
    print("  ✅ Admin blueprint registered")
    app.register_blueprint(review_tokens_bp)
    print("  ✅ Review tokens blueprint registered")
    app.register_blueprint(sequences_bp)
    print("  ✅ Sequences blueprint registered")

    print("🎉 Flask app creation complete!")
    # Error handler for JWT errors
    from flask_jwt_extended.exceptions import NoAuthorizationError, InvalidHeaderError
    from flask_jwt_extended import JWTManager
    jwt = JWTManager(app)

    @app.errorhandler(NoAuthorizationError)
    def handle_no_auth_error(e):
        return jsonify({"error": "Missing or invalid JWT token."}), 401

    @app.errorhandler(InvalidHeaderError)
    def handle_invalid_header_error(e):
        return jsonify({"error": "Invalid JWT header."}), 422
    return app

# instantiate Flask app
print("🏗️ Creating app instance...")
app = create_app()
print("✅ App instance created successfully!")

if __name__ == '__main__':
    print("🚀 Starting Flask development server...")
    app.run(host='0.0.0.0', port=5050, debug=True)