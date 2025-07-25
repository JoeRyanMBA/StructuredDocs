from flask import Blueprint, Flask, request, jsonify
from backend.models import db, Publication, PublicationNode


# Pass strict_slashes here so both /api/publications and /api/publications/ match
pubs = Blueprint(
    'publications',
    __name__,
    url_prefix='/api/publications',
)

def create_app():
    app = Flask(__name__)
    # initialize your DB, config, etc.
    app.register_blueprint(pubs)
    return app

@pubs.route('', methods=['GET'])
def list_pubs():
    all_pubs = Publication.query.order_by(Publication.created_at.desc()).all()
    return jsonify([{'id': p.id, 'title': p.title} for p in all_pubs]), 200

@pubs.route('/<int:pub_id>', methods=['GET'])
def get_pub(pub_id):
    p = Publication.query.get_or_404(pub_id)
    def serialize(node):
        return {
            'id': node.id,
            'topic': node.topic.to_dict(),
            'position': node.position,
            'children': sorted([serialize(c) for c in node.children],
                               key=lambda x: x['position'])
        }
    top_nodes = [n for n in p.nodes if n.parent_id is None]
    tree = sorted([serialize(n) for n in top_nodes],
                  key=lambda x: x['position'])
    return jsonify({'id': p.id, 'title': p.title, 'tree': tree}), 200

@pubs.route('/<int:pub_id>/nodes', methods=['POST'])
def save_nodes(pub_id):
    payload = request.get_json()  # expect {"tree": [...]}
    PublicationNode.query.filter_by(publication_id=pub_id).delete()

    def walk(nodes, parent_id=None):
        for idx, n in enumerate(nodes):
            node = PublicationNode(
                publication_id=pub_id,
                topic_id=n['topic_id'],
                parent_id=parent_id,
                position=idx
            )
            db.session.add(node)
            db.session.flush()  # assign node.id
            if n.get('children'):
                walk(n['children'], node.id)

    walk(payload['tree'])
    db.session.commit()
    return jsonify({'message': 'saved'}), 200