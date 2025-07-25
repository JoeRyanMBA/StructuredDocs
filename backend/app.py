# backend/app.py

from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from backend.models import db
from backend.routes.topics       import topics  as topics_bp
from backend.routes.imports      import imports as imports_bp
from backend.routes.publications import pubs    as pubs_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(pubs_bp)

    # enable CORS and debug mode
    CORS(app)
    app.config['DEBUG'] = True

    # database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///structured_docs.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True
    print('Connected DB URI:', app.config['SQLALCHEMY_DATABASE_URI'])

    # bind SQLAlchemy + Alembic
    db.init_app(app)
    Migrate(app, db)

    # health‐check endpoint
    @app.route('/ping', methods=['GET'])
    def ping():
        return jsonify({"status": "ok"}), 200

    # register blueprints
    app.register_blueprint(topics_bp,  url_prefix='/api/topics')
    app.register_blueprint(imports_bp, url_prefix='/api/import')

    return app

# instantiate Flask app
app = create_app()

if __name__ == '__main__':
    # only used when launching via `python backend/app.py`
    app.run(host='0.0.0.0', port=5000, debug=True)