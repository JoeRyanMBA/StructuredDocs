# backend/app.py

from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from backend.models import db
from backend.routes.topics         import topics  as topics_bp
from backend.routes.import_handler import imports as imports_bp
from backend.routes.publications   import pubs_bp
from backend.routes.collections    import collections_bp
from backend.routes.reviews        import reviews_bp
from backend.routes.projects       import projects_bp
from backend.routes.users          import users_bp
from backend.routes.metrics        import metrics_bp
from backend.routes.notifications import notifications_bp

def create_app():
    print("🚀 Creating Flask app...")
    app = Flask(__name__)
    print("📱 Flask instance created")
    
    # enable CORS and debug mode
    CORS(app)
    print("🌐 CORS enabled")
    
    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////workspaces/StructuredDocs/backend/instance/structured_docs.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True
    print('💾 Connected DB URI:', app.config['SQLALCHEMY_DATABASE_URI'])

    db.init_app(app)
    print("🗄️ Database initialized")
    
    Migrate(app, db)
    print("🔄 Migration setup complete")

    @app.route('/ping', methods=['GET'])
    def ping():
        print("🏓 Ping endpoint called")
        return jsonify({"status": "ok"}), 200

    @app.route('/test', methods=['GET'])
    def test():
        print("🧪 Test endpoint called")
        return jsonify({"message": "test successful"}), 200

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

    print("🎉 Flask app creation complete!")
    return app

# instantiate Flask app
print("🏗️ Creating app instance...")
app = create_app()
print("✅ App instance created successfully!")

if __name__ == '__main__':
    print("🚀 Starting Flask development server...")
    # only used when launching via `python backend/app.py`
    app.run(host='0.0.0.0', port=5000, debug=True)