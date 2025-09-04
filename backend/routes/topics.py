# backend/routes/topics.py

from flask import Blueprint, request, jsonify, current_app
from ..models import db, Topic, Link, TopicLink, User
from flask_jwt_extended import jwt_required, get_jwt_identity

topics_bp = Blueprint('topics', __name__, url_prefix='/api/topics')

# GET /api/topics → List all topics
@topics_bp.route('', methods=['GET'])
@topics_bp.route('/', methods=['GET'])
def list_topics():
    try:
        all_topics = Topic.query.order_by(Topic.created_at.desc()).all()
        return jsonify([t.to_dict() for t in all_topics]), 200
    except Exception as e:
        current_app.logger.exception("Failed to list topics")
        return jsonify({'error': str(e)}), 500

# POST /api/topics → Create a new topic (defaults to draft)
@topics_bp.route('', methods=['POST'])
@topics_bp.route('/', methods=['POST'])
def create_topic():
    data = request.get_json() or {}
    try:
        topic = Topic(
            title=(data.get('title') or 'Untitled'),
            content=data.get('content'),
            frontmatter=data.get('frontmatter'),
            status=data.get('status', 'draft')
        )
        db.session.add(topic)
        db.session.commit()
        return jsonify(topic.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Failed to create topic")
        return jsonify({'error': str(e)}), 500

# GET /api/topics/<id> → Fetch a single topic
@topics_bp.route('/<int:topic_id>', methods=['GET'])
def get_topic(topic_id):
    topic = Topic.query.get(topic_id)
    if topic:
        return jsonify(topic.to_dict()), 200
    return jsonify({'error': 'Topic not found'}), 404

# PUT /api/topics/<id> → Update a topic
@topics_bp.route('/<int:topic_id>', methods=['PUT'])
def update_topic(topic_id):
    data = request.get_json() or {}
    topic = Topic.query.get(topic_id)
    if not topic:
        return jsonify({'error': 'Topic not found'}), 404

    try:
        topic.title   = data.get('title', topic.title)
        topic.content = data.get('content', topic.content)
        topic.frontmatter = data.get('frontmatter', topic.frontmatter)
        if 'status' in data:
            topic.status = data['status']
        db.session.commit()
        return jsonify(topic.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Failed to update topic")
        return jsonify({'error': str(e)}), 500

# POST /api/topics/<id>/publish → Publish a draft
@topics_bp.route('/<int:topic_id>/publish', methods=['POST'])
def publish_topic(topic_id):
    topic = Topic.query.get(topic_id)
    if not topic:
        return jsonify({'error': 'Topic not found'}), 404

    if topic.status == 'published':
        return jsonify({'error': 'Already published'}), 400

    try:
        topic.status = 'published'
        db.session.commit()
        return jsonify(topic.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Failed to publish topic")
        return jsonify({'error': str(e)}), 500

# DELETE /api/topics/bulk → Delete multiple topics by IDs
@topics_bp.route('/bulk', methods=['DELETE'])
@topics_bp.route('/bulk/delete', methods=['POST'])
@jwt_required()
def bulk_delete_topics():
    try:
        payload = request.get_json(silent=True) or {}
        ids = payload.get('ids')
        if not ids or not isinstance(ids, list):
            return jsonify({'error': 'Provide body { "ids": [1,2,3] }'}), 400

        # Convert IDs to integers and de-dup
        try:
            id_list = sorted({int(x) for x in ids})
        except Exception:
            return jsonify({'error': 'All ids must be integers'}), 400

        if not id_list:
            return jsonify({'deleted': 0, 'not_found': []}), 200

        # Enforce admin authorization
        user_id = get_jwt_identity()
        # Token identity may be a string; cast to int for DB lookup when possible
        try:
            user_pk = int(user_id) if user_id is not None else None
        except (TypeError, ValueError):
            user_pk = None
        current_user = User.query.get(user_pk) if user_pk is not None else None
        if not current_user:
            return jsonify({'error': 'Unauthorized'}), 401
        # Accept roles: admin or superadmin (fallback to role string) or boolean is_admin
        is_admin = False
        try:
            if hasattr(current_user, 'is_admin') and current_user.is_admin:
                is_admin = True
            elif hasattr(current_user, 'role') and str(current_user.role).lower() in ('admin', 'superadmin'):
                is_admin = True
        except Exception:
            is_admin = False
        if not is_admin:
            return jsonify({'error': 'Admin role required for bulk deletion'}), 403

        # Fetch existing topics
        existing = Topic.query.filter(Topic.id.in_(id_list)).all()
        existing_ids = {t.id for t in existing}
        missing = [i for i in id_list if i not in existing_ids]

        # Delete in a transaction
        deleted_count = 0
        try:
            for t in existing:
                db.session.delete(t)
            db.session.commit()
            deleted_count = len(existing)
        except Exception as e:
            db.session.rollback()
            current_app.logger.exception('Bulk delete failed')
            return jsonify({'error': str(e)}), 500

        return jsonify({
            'deleted': deleted_count,
            'not_found': missing
        }), 200

    except Exception as e:
        current_app.logger.exception('Bulk delete endpoint error')
        return jsonify({'error': str(e)}), 500