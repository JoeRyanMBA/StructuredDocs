# backend/routes/bulk_reviews.py
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from ..models import db, Topic, Review, Stakeholder, ReviewBatch, ReviewBatchToken, ReviewFeedback
from ..utils.email_service import email_service
from ..extensions import limiter
import secrets
import logging

logger = logging.getLogger(__name__)

bulk_reviews_bp = Blueprint('bulk_reviews', __name__)


# ---------------------------------------------------------------------------
# Author-facing: create a bulk review batch
# ---------------------------------------------------------------------------

@bulk_reviews_bp.route('/api/reviews/bulk-request', methods=['POST'])
@jwt_required()
def create_bulk_review():
    """Create a ReviewBatch for multiple topics assigned to a single reviewer.

    Body JSON:
      topic_ids      list[int]  required – IDs of topics to review (>=2)
      reviewer_id    int        required
      priority       str        optional (low/medium/high/urgent), default medium
      due_date       str        optional ISO-8601
      message        str        optional author message
      requested_by   int        optional stakeholder ID of the requester
    """
    try:
        data = request.get_json() or {}

        topic_ids = data.get('topic_ids', [])
        if not isinstance(topic_ids, list) or len(topic_ids) < 2:
            return jsonify({'error': 'topic_ids must be a list of at least 2 topic IDs'}), 400

        reviewer_id = data.get('reviewer_id')
        if not reviewer_id:
            return jsonify({'error': 'reviewer_id is required'}), 400

        reviewer = Stakeholder.query.get(reviewer_id)
        if not reviewer:
            return jsonify({'error': 'Reviewer not found'}), 404
        if not reviewer.can_review:
            return jsonify({'error': 'Selected stakeholder cannot perform reviews'}), 400

        # Resolve requester
        requester = None
        if data.get('requested_by'):
            requester = Stakeholder.query.get(data['requested_by'])
        if not requester:
            requester = Stakeholder.query.filter(Stakeholder.active == True).order_by(Stakeholder.id.asc()).first()
        if not requester:
            return jsonify({'error': 'No valid requester stakeholder found'}), 400

        # Validate all topics exist
        topics = Topic.query.filter(Topic.id.in_(topic_ids)).all()
        found_ids = {t.id for t in topics}
        missing = set(topic_ids) - found_ids
        if missing:
            return jsonify({'error': f'Topics not found: {sorted(missing)}'}), 404

        # Preserve caller-supplied ordering
        topic_map = {t.id: t for t in topics}
        ordered_topics = [topic_map[tid] for tid in topic_ids]

        due_date = None
        if data.get('due_date'):
            due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
        else:
            due_date = datetime.utcnow() + timedelta(days=7)

        # Create the batch
        batch = ReviewBatch(
            requester_id=requester.id,
            reviewer_id=reviewer.id,
            priority=data.get('priority', 'medium'),
            due_date=due_date,
            message=data.get('message', ''),
        )
        db.session.add(batch)
        db.session.flush()  # get batch.id before creating children

        # Create one Review per topic
        for position, topic in enumerate(ordered_topics):
            review = Review(
                topic_id=topic.id,
                requested_by=requester.id,
                reviewer_id=reviewer.id,
                priority=batch.priority,
                due_date=due_date,
                author_message=batch.message,
                batch_id=batch.id,
                batch_position=position,
            )
            topic.status = 'pending_review'
            topic.updated_at = datetime.utcnow()
            db.session.add(review)

        db.session.flush()

        # Create one shared token for the whole batch
        token_str = secrets.token_urlsafe(32)
        batch_token = ReviewBatchToken(
            token=token_str,
            batch_id=batch.id,
            reviewer_email=reviewer.email,
            expires_at=due_date + timedelta(days=7),
        )
        db.session.add(batch_token)
        db.session.commit()

        # Send a single digest email
        topic_titles = [t.title for t in ordered_topics]
        try:
            email_sent = email_service.send_bulk_review_notification(
                reviewer_email=reviewer.email,
                reviewer_name=reviewer.name,
                topic_titles=topic_titles,
                author_message=batch.message,
                due_date=due_date,
                priority=batch.priority,
                batch_token=token_str,
            )
            batch.email_delivery_unavailable = not email_sent
            db.session.commit()
            if email_sent:
                logger.info(f"Bulk review email sent to {reviewer.email} (batch {batch.id}, {len(topic_ids)} topics)")
            else:
                logger.warning(f"Bulk review email failed for {reviewer.email} (batch {batch.id})")
        except Exception as email_err:
            batch.email_delivery_unavailable = True
            db.session.commit()
            logger.error(f"Bulk review email error: {email_err}")

        return jsonify({
            'message': f'Bulk review requested for {len(topic_ids)} topics',
            'batch': batch.to_dict(),
            'portal_url': f'/bulk-review/{token_str}',
            'email_delivery_unavailable': batch.email_delivery_unavailable,
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.exception('create_bulk_review failed')
        return jsonify({'error': str(e)}), 500


# ---------------------------------------------------------------------------
# Reviewer-facing: token-gated portal endpoints (no JWT required)
# ---------------------------------------------------------------------------

def _resolve_batch_token(token_str):
    """Return (batch_token, error_response) — one of the two is None."""
    bt = ReviewBatchToken.query.filter_by(token=token_str).first()
    if not bt:
        return None, (jsonify({'error': 'Invalid token'}), 404)
    valid, msg = bt.is_valid()
    if not valid:
        return None, (jsonify({'error': msg}), 403)
    return bt, None


@bulk_reviews_bp.route('/api/bulk-review/<token>', methods=['GET'])
def get_bulk_review_portal(token):
    """Return all topics in the batch with their review state for the portal."""
    try:
        bt, err = _resolve_batch_token(token)
        if err:
            return err

        bt.access_count += 1
        if not bt.accessed_at:
            bt.accessed_at = datetime.now()
        db.session.commit()

        batch = bt.batch
        reviews = sorted(batch.reviews, key=lambda r: (r.batch_position or 0))

        topics_data = []
        for review in reviews:
            topic = review.topic
            feedback_items = [fi.to_dict() for fi in review.feedback_items]
            topics_data.append({
                'review_id': review.id,
                'position': review.batch_position,
                'topic_id': topic.id,
                'topic_title': topic.title,
                'topic_content': topic.content or '',
                'review_status': review.status,
                'recommendation': review.recommendation,
                'feedback': review.feedback,
                'feedback_items': feedback_items,
                'completed': review.status == 'completed',
            })

        return jsonify({
            'batch_id': batch.id,
            'reviewer_email': bt.reviewer_email,
            'reviewer_name': batch.reviewer.name if batch.reviewer else None,
            'priority': batch.priority,
            'due_date': batch.due_date.isoformat() if batch.due_date else None,
            'message': batch.message,
            'status': batch.status,
            'total': len(topics_data),
            'completed_count': sum(1 for t in topics_data if t['completed']),
            'topics': topics_data,
            'token_info': {
                'expires_at': bt.expires_at.isoformat(),
                'access_count': bt.access_count,
            },
        })

    except Exception as e:
        current_app.logger.exception('get_bulk_review_portal failed')
        return jsonify({'error': str(e)}), 500


@bulk_reviews_bp.route('/api/bulk-review/<token>/review/<int:review_id>/feedback', methods=['POST'])
def submit_bulk_topic_feedback(token, review_id):
    """Submit feedback for one topic within a bulk review batch."""
    try:
        bt, err = _resolve_batch_token(token)
        if err:
            return err

        # Confirm the review belongs to this batch
        review = Review.query.get(review_id)
        if not review or review.batch_id != bt.batch_id:
            return jsonify({'error': 'Review not found in this batch'}), 404

        data = request.get_json() or {}
        feedback_items_data = data.get('feedback_items', [])
        overall_recommendation = data.get('recommendation')
        overall_feedback = data.get('feedback')
        edited_content = data.get('edited_content')

        for item in feedback_items_data:
            fb = ReviewFeedback(
                review_id=review.id,
                feedback_type=item.get('feedback_type', 'general_comment'),
                section_title=item.get('section_title'),
                page_number=item.get('page_number'),
                paragraph_number=item.get('paragraph_number'),
                line_reference=item.get('line_reference'),
                original_text=item.get('original_text'),
                suggested_text=item.get('suggested_text'),
                comment=item.get('comment'),
                rationale=item.get('rationale'),
                priority=item.get('priority', 'medium'),
                impact=item.get('impact', 'moderate'),
            )
            db.session.add(fb)

        if overall_recommendation:
            review.recommendation = overall_recommendation
        if overall_feedback:
            review.feedback = overall_feedback

        if edited_content and overall_recommendation == 'approve_with_changes':
            review.topic.content = edited_content
            review.topic.updated_at = datetime.now()
        elif edited_content:
            review.edited_content = edited_content

        review.status = 'completed'
        review.completed_at = datetime.now()

        # Update batch status
        batch = bt.batch
        all_reviews = batch.reviews
        if all(r.status == 'completed' for r in all_reviews):
            batch.status = 'completed'
        elif batch.status == 'pending':
            batch.status = 'in_progress'

        db.session.commit()

        completed_count = sum(1 for r in all_reviews if r.status == 'completed')
        return jsonify({
            'success': True,
            'message': 'Feedback submitted',
            'completed_count': completed_count,
            'total': len(all_reviews),
            'batch_complete': batch.status == 'completed',
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.exception('submit_bulk_topic_feedback failed')
        return jsonify({'error': str(e)}), 500


@bulk_reviews_bp.route('/api/bulk-review/<token>/status', methods=['GET'])
def get_bulk_review_status(token):
    """Return lightweight per-topic completion status."""
    try:
        bt, err = _resolve_batch_token(token)
        if err:
            return err

        batch = bt.batch
        reviews = sorted(batch.reviews, key=lambda r: (r.batch_position or 0))

        return jsonify({
            'batch_id': batch.id,
            'status': batch.status,
            'total': len(reviews),
            'completed_count': sum(1 for r in reviews if r.status == 'completed'),
            'topics': [
                {
                    'review_id': r.id,
                    'position': r.batch_position,
                    'topic_title': r.topic.title if r.topic else None,
                    'completed': r.status == 'completed',
                }
                for r in reviews
            ],
        })

    except Exception as e:
        current_app.logger.exception('get_bulk_review_status failed')
        return jsonify({'error': str(e)}), 500
