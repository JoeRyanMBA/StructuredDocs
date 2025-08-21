# backend/routes/topics.py

from flask import Blueprint, request, jsonify, current_app
from models import db, Topic

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
            title=data.get('title'),
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