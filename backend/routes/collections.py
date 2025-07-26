from flask import Blueprint, request, jsonify
from backend.models import db, Collection, collection_topic_tree

collections_bp = Blueprint('collections', __name__, url_prefix='/api/collections')

@collections_bp.route('', methods=['GET'])
def list_collections():
    roots = Collection.query.filter_by(parent_id=None)\
              .order_by(Collection.position).all()
    tree = [c.to_dict() for c in roots]
    return jsonify(tree), 200

@collections_bp.route('', methods=['PUT'])
def update_collections():
    """
    Expect payload: an array of nested nodes:
    [
      { id, parentId, position, children:[ ... ], topics: [...] },
      …
    ]
    """
    payload = request.get_json()

    def walk(nodes):
      for node in nodes:
        col = Collection.query.get(node['id'])
        if not col:
            continue  # or log a warning, or raise an error
        col.parent_id = node.get('parentId')
        col.position  = node.get('position', 0)
        # Update topics ordering if provided
        if 'topics' in node:
          for idx, t in enumerate(node['topics']):
            db.session.execute(collection_topic_tree.update()
              .where(
                (collection_topic_tree.c.collection_id==col.id) &
                (collection_topic_tree.c.topic_id==t['id'])
              )
              .values(position=idx)
            )
        # recurse children
        if node.get('children'):
          walk(node['children'])

    walk(payload)
    db.session.commit()
    return jsonify({'message': 'collection tree updated'}), 200

@collections_bp.route('', methods=['POST'])
def create_collection():
    """
    Create a new collection.
    Expects JSON payload: { "name": str, "parentId": int (optional), "position": int (optional) }
    """
    data = request.get_json()
    name = data.get('name')
    parent_id = data.get('parentId')
    position = data.get('position', 0)

    if not name:
        return jsonify({'error': 'Collection name is required'}), 400

    new_collection = Collection(name=name, parent_id=parent_id, position=position)
    db.session.add(new_collection)
    db.session.commit()
    return jsonify(new_collection.to_dict()), 201