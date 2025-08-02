# backend/app.py

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_migrate import Migrate
import os

def create_app():

    print("  ✅ Reviews blueprint registered")
    print("🚀 Creating Flask app...")
    app = Flask(__name__)
    print("📱 Flask instance created")
    # enable CORS and debug mode
    # Configure SQLAlchemy database URI
    import os
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'structured_docs.db')
    
    # Configure static files for image serving
    app.config['STATIC_FOLDER'] = os.path.join(app.root_path, 'static')
    
    # Initialize SQLAlchemy
    from . import db
    db.init_app(app)

    # Register Flask-Migrate
    from flask_migrate import Migrate
    migrate = Migrate(app, db)

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
    from .routes.topics         import topics  as topics_bp
    from .routes.import_handler import imports as imports_bp
    from .routes.publications   import pubs_bp
    from .routes.collections    import collections_bp
    from .routes.reviews        import reviews_bp
    from .routes.projects       import projects_bp
    from .routes.users          import users_bp
    from .routes.metrics        import metrics_bp
    from .routes.notifications  import notifications_bp
    from .routes.links          import links_bp
    from .routes.stakeholders   import stakeholders_bp

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