from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from backend.extensions import db
from backend.models import Snippet, EntityTag, Tag, Topic

snippets_bp = Blueprint('snippets', __name__, url_prefix='/api/snippets')


def _attach_tags(snippet_dict, snippet_id):
    """Attach tag list and usage count to a snippet dict."""
    entity_tags = EntityTag.query.filter_by(entity_type='snippet', entity_id=snippet_id).all()
    snippet_dict['tags'] = [et.to_dict() for et in entity_tags]
    snippet_dict['usage_count'] = _count_usage(snippet_id)
    return snippet_dict


def _count_usage(snippet_id):
    """Count topics whose content references this snippet."""
    return Topic.query.filter(
        Topic.content.like(f'%data-snippet-id="{snippet_id}"%')
    ).count()


def _get_usage_topics(snippet_id):
    """Return list of topics that reference this snippet."""
    from backend.models import Collection, Project
    topics = Topic.query.filter(
        Topic.content.like(f'%data-snippet-id="{snippet_id}"%')
    ).all()
    result = []
    for t in topics:
        entry = {'id': t.id, 'title': t.title}
        # Try to attach collection/project breadcrumb
        try:
            if t.collection_id:
                col = Collection.query.get(t.collection_id)
                if col:
                    entry['collection'] = col.name
                    if col.project_id:
                        proj = Project.query.get(col.project_id)
                        if proj:
                            entry['project'] = proj.name
        except Exception:
            pass
        result.append(entry)
    return result


@snippets_bp.route('', methods=['GET'])
@jwt_required()
def list_snippets():
    snippets = Snippet.query.order_by(Snippet.title).all()
    return jsonify([_attach_tags(s.to_dict(), s.id) for s in snippets])


@snippets_bp.route('', methods=['POST'])
@jwt_required()
def create_snippet():
    data = request.get_json() or {}
    if not data.get('title', '').strip():
        return jsonify({'error': 'title is required'}), 400
    snippet = Snippet(title=data['title'].strip(), content=data.get('content', ''))
    db.session.add(snippet)
    db.session.commit()
    return jsonify(_attach_tags(snippet.to_dict(), snippet.id)), 201


@snippets_bp.route('/<int:snippet_id>', methods=['GET'])
@jwt_required()
def get_snippet(snippet_id):
    snippet = Snippet.query.get_or_404(snippet_id)
    return jsonify(_attach_tags(snippet.to_dict(), snippet_id))


@snippets_bp.route('/<int:snippet_id>', methods=['PUT'])
@jwt_required()
def update_snippet(snippet_id):
    snippet = Snippet.query.get_or_404(snippet_id)
    data = request.get_json() or {}
    if 'title' in data:
        if not data['title'].strip():
            return jsonify({'error': 'title cannot be empty'}), 400
        snippet.title = data['title'].strip()
    if 'content' in data:
        snippet.content = data['content']
    db.session.commit()
    return jsonify(_attach_tags(snippet.to_dict(), snippet_id))


@snippets_bp.route('/<int:snippet_id>', methods=['DELETE'])
@jwt_required()
def delete_snippet(snippet_id):
    snippet = Snippet.query.get_or_404(snippet_id)
    if _count_usage(snippet_id) > 0:
        return jsonify({'error': 'Cannot delete: snippet is used in one or more topics.'}), 409
    EntityTag.query.filter_by(entity_type='snippet', entity_id=snippet_id).delete()
    db.session.delete(snippet)
    db.session.commit()
    return jsonify({'message': 'Snippet deleted'}), 200


@snippets_bp.route('/<int:snippet_id>/usage', methods=['GET'])
@jwt_required()
def snippet_usage(snippet_id):
    Snippet.query.get_or_404(snippet_id)
    return jsonify(_get_usage_topics(snippet_id))


@snippets_bp.route('/<int:snippet_id>/tags', methods=['PUT'])
@jwt_required()
def set_snippet_tags(snippet_id):
    """Replace all tags on a snippet (bulk assign)."""
    Snippet.query.get_or_404(snippet_id)
    data = request.get_json() or {}
    tag_ids = data.get('tag_ids', [])

    EntityTag.query.filter_by(entity_type='snippet', entity_id=snippet_id).delete()
    for tag_id in tag_ids:
        if Tag.query.get(tag_id):
            db.session.add(EntityTag(entity_type='snippet', entity_id=snippet_id, tag_id=tag_id))
    db.session.commit()
    return jsonify(_attach_tags(Snippet.query.get(snippet_id).to_dict(), snippet_id))
