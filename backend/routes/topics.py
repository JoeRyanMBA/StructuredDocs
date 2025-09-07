# backend/routes/topics.py

from flask import Blueprint, request, jsonify, current_app
from ..models import db, Topic, Link, TopicLink, User, Review, Stakeholder, ReviewToken
from datetime import datetime, timedelta
from ..utils.email_service import email_service
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

# POST /api/topics/<id>/review → Convenience wrapper to create a review request
@topics_bp.route('/<int:topic_id>/review', methods=['POST'])
def create_topic_review(topic_id):
    """Create a simple review request for a topic.

    Accepts JSON body (all optional for quick path):
      reviewer_id: Stakeholder ID of reviewer
      requested_by: Stakeholder ID of requester
      priority: low|medium|high|urgent (default medium)
      message: author message
      due_in_days: int (default 7)

    If reviewer_id or requested_by missing, attempts to auto-select the first Stakeholder with can_review.
    Returns 400 if no stakeholders available and not provided explicitly.
    """
    data = request.get_json(silent=True) or {}
    topic = Topic.query.get(topic_id)
    if not topic:
        return jsonify({'error': 'Topic not found'}), 404

    try:
        reviewer_id = data.get('reviewer_id')
        requested_by = data.get('requested_by')

        if not reviewer_id or not requested_by:
            # Try to locate any existing active reviewer-capable stakeholder
            first = Stakeholder.query.filter(Stakeholder.can_review == True, Stakeholder.active == True).first()  # noqa: E712
            if not first:
                # Auto-provision a default reviewer to keep UX simple for first-time deployments
                import os
                default_email = os.environ.get('DEFAULT_REVIEWER_EMAIL', 'reviewer@example.com')
                default_name = os.environ.get('DEFAULT_REVIEWER_NAME', 'Auto Reviewer')
                # Re-check by email in case created concurrently
                existing = Stakeholder.query.filter(Stakeholder.email == default_email).first()
                if existing:
                    first = existing
                else:
                    try:
                        first = Stakeholder()  # type: ignore[call-arg]
                        # Manually assign fields (avoids strict type stubs complaining about signature)
                        first.name = default_name
                        first.email = default_email
                        first.can_review = True
                        first.active = True
                        db.session.add(first)
                        db.session.flush()  # Assign ID within current txn
                        current_app.logger.info('Auto-provisioned default reviewer stakeholder (%s)', default_email)
                    except Exception:
                        # If creation fails, abort with guidance
                        current_app.logger.warning('Failed to auto-provision default reviewer stakeholder')
                        return jsonify({'error': 'No reviewer/requester supplied and no stakeholders exist. Create a stakeholder or pass reviewer_id & requested_by.'}), 400
            if not reviewer_id:
                reviewer_id = first.id
            if not requested_by:
                requested_by = first.id

        reviewer = Stakeholder.query.get(reviewer_id)
        requester = Stakeholder.query.get(requested_by)
        if not reviewer or not requester:
            return jsonify({'error': 'Invalid reviewer_id or requested_by'}), 400
        if not reviewer.can_review:
            return jsonify({'error': 'Selected reviewer cannot review'}), 400

        priority = data.get('priority', 'medium')
        if priority not in ('low','medium','high','urgent'):
            priority = 'medium'
        due_in_days = data.get('due_in_days')
        try:
            due_in_days = int(due_in_days) if due_in_days is not None else 7
        except Exception:
            due_in_days = 7
        due_date = datetime.utcnow() + timedelta(days=max(1, min(due_in_days, 30)))

        review = Review(
            topic_id=topic.id,
            requested_by=requester.id,
            reviewer_id=reviewer.id,
            priority=priority,
            due_date=due_date,
            author_message=data.get('message','')
        )
        topic.status = 'pending_review'
        topic.updated_at = datetime.utcnow()
        db.session.add(review)
        db.session.flush()

        # Create token for external access
        token = ReviewToken(
            token=__import__('secrets').token_urlsafe(32),
            review_id=review.id,
            reviewer_email=reviewer.email,
            expires_at=due_date + timedelta(days=7)
        )
        db.session.add(token)
        db.session.commit()

        # Best-effort email (non-fatal on failure)
        try:
            if email_service:
                email_service.send_review_notification(
                    reviewer_email=reviewer.email,
                    reviewer_name=reviewer.name,
                    topic_title=topic.title,
                    topic_id=topic.id,
                    author_message=review.author_message,
                    due_date=due_date,
                    priority=priority,
                    review_token=token.token
                )
        except Exception:
            current_app.logger.warning('Email dispatch failed for review %s', review.id)

        return jsonify({'message':'Review requested','review': review.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception('Failed to create review via topic convenience endpoint')
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