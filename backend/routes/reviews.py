from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from datetime import datetime, timedelta
from ..models import db, Topic, Collection, ImportDocument, Review, Stakeholder, ProjectStakeholder, ReviewToken
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    # For type checking only to help Pylance understand names
    from ..models import ReviewSequence  # noqa: F401
from sqlalchemy import or_, and_
from ..services.review_sequences import apply_topic_status_for_review, advance_sequence_for_review
from ..utils.email_service import email_service
import secrets
import logging

# Set up logging
logger = logging.getLogger(__name__)

reviews_bp = Blueprint('reviews', __name__, url_prefix='/api/reviews')

# Base GET endpoint for /api/reviews
@reviews_bp.route('/', methods=['GET'])
@jwt_required()
def reviews_root():
    """Base endpoint for reviews API - returns all reviews"""
    try:
        reviews = Review.query.order_by(Review.requested_at.desc()).all()
        return jsonify([review.to_dict() for review in reviews])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reviews_bp.route('/<int:review_id>', methods=['GET'])
@jwt_required()
def get_review_details(review_id):
    """Get details for a specific review"""
    try:
        review = Review.query.get_or_404(review_id)
        data = review.to_dict()
        data['feedback_items'] = [item.to_dict() for item in review.feedback_items]
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reviews_bp.route('/reviewers', methods=['GET'])
@jwt_required()
def get_available_reviewers():
    """Get list of available reviewers from stakeholders"""
    try:
        # Include stakeholders with global review permissions OR project-level review permissions.
        reviewers = (
            db.session.query(Stakeholder)
            .outerjoin(ProjectStakeholder, ProjectStakeholder.stakeholder_id == Stakeholder.id)
            .filter(
                or_(
                    Stakeholder.can_review == True,
                    ProjectStakeholder.can_review == True
                )
            )
            .distinct()
            .all()
        )
        
        return jsonify([{
            'id': reviewer.id,
            'name': reviewer.name,
            'email': reviewer.email,
            'role': reviewer.role,
            'division': reviewer.division
        } for reviewer in reviewers])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reviews_bp.route('/request', methods=['POST'])
@jwt_required()
def request_review():
    """Request a review for a topic"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['topic_id', 'reviewer_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if topic exists
        topic = Topic.query.get_or_404(data['topic_id'])
        
        # Check if reviewer exists and can review
        reviewer = Stakeholder.query.get_or_404(data['reviewer_id'])
        if not reviewer.can_review:
            return jsonify({'error': 'Selected stakeholder cannot perform reviews'}), 400
            
        # Resolve requester stakeholder (supports legacy requested_by and email/name fallbacks)
        requester = None
        requested_by = data.get('requested_by')
        if requested_by is not None:
            requester = Stakeholder.query.get(requested_by)

        if not requester:
            requester_email = (data.get('requester_email') or '').strip()
            if requester_email:
                requester = Stakeholder.query.filter(Stakeholder.email.ilike(requester_email)).first()

        if not requester:
            requester_name = (data.get('requester_name') or '').strip()
            if requester_name:
                requester = Stakeholder.query.filter(Stakeholder.name == requester_name).first()

        if not requester:
            requester = Stakeholder.query.filter(Stakeholder.active == True).order_by(Stakeholder.id.asc()).first()

        if not requester:
            return jsonify({'error': 'No valid requester stakeholder found. Please create an active stakeholder first.'}), 400
        
        # Calculate due date (default to 7 days from now if not specified)
        due_date = None
        if data.get('due_date'):
            due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
        else:
            due_date = datetime.utcnow() + timedelta(days=7)
        
        # Create review request
        review = Review(
            topic_id=data['topic_id'],
            requested_by=requester.id,
            reviewer_id=data['reviewer_id'],
            priority=data.get('priority', 'medium'),
            due_date=due_date,
            author_message=data.get('message', '')
        )
        
        # Update topic status to pending_review
        topic.status = 'pending_review'
        topic.updated_at = datetime.utcnow()
        
        db.session.add(review)
        db.session.commit()
        
        # Create secure token for external reviewer access
        token = ReviewToken(
            token=secrets.token_urlsafe(32),
            review_id=review.id,
            reviewer_email=reviewer.email,
            expires_at=due_date + timedelta(days=7)  # Token expires 7 days after due date
        )
        
        db.session.add(token)
        db.session.commit()
        
        # Send email notification to reviewer
        logger.info(f"Starting email notification process for review {review.id}")
        logger.info(f"Reviewer: {reviewer.name} ({reviewer.email})")
        logger.info(f"Topic: {topic.title}")
        logger.debug(f"Review token: {token.token}")
        
        try:
            logger.info(f"Attempting to send email to {reviewer.email} for topic '{topic.title}'")
            email_sent = email_service.send_review_notification(
                reviewer_email=reviewer.email,
                reviewer_name=reviewer.name,
                topic_title=topic.title,
                topic_id=topic.id,
                author_message=review.author_message,
                due_date=review.due_date,
                priority=review.priority,
                review_token=token.token
            )
            
            if email_sent:
                review.email_delivery_unavailable = False
                db.session.commit()
                current_app.logger.info(f" Email notification sent successfully to {reviewer.email}")
                current_app.logger.debug(f"📄 Review token: {token.token}")
                current_app.logger.debug(f"🔗 Review URL: http://localhost:5173/review/{token.token}")
            else:
                review.email_delivery_unavailable = True
                db.session.commit()
                current_app.logger.warning(f" Failed to send email notification to {reviewer.email}")
                
        except Exception as email_error:
            review.email_delivery_unavailable = True
            db.session.commit()
            current_app.logger.error(f" Email notification error: {str(email_error)}")
            import traceback
            current_app.logger.debug(f"🔍 Full traceback: {traceback.format_exc()}")
            # Don't fail the entire request if email fails
        
        return jsonify({
            'message': 'Review requested successfully',
            'review': review.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@reviews_bp.route('/<int:review_id>/start', methods=['POST'])
@jwt_required()
def start_review(review_id):
    """Mark a review as started"""
    try:
        review = Review.query.get_or_404(review_id)
        
        if review.status != 'pending':
            return jsonify({'error': 'Review is not in pending status'}), 400
            
        review.status = 'in_progress'
        review.started_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Review started',
            'review': review.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@reviews_bp.route('/<int:review_id>/submit', methods=['POST'])
@jwt_required()
def submit_review(review_id):
    """Submit completed review with feedback"""
    try:
        review = Review.query.get_or_404(review_id)
        data = request.get_json()
        
        if review.status not in ['pending', 'in_progress']:
            return jsonify({'error': 'Review cannot be modified in current status'}), 400
        
        # Validate required fields
        if 'recommendation' not in data:
            return jsonify({'error': 'Recommendation is required'}), 400
            
        if data['recommendation'] not in ['approve', 'approve_with_changes', 'reject', 'needs_more_info']:
            return jsonify({'error': 'Invalid recommendation'}), 400
        
        # Update review
        review.status = 'completed'
        review.completed_at = datetime.utcnow()
        review.feedback = data.get('feedback', '')
        review.recommendation = data['recommendation']
        review.review_notes = data.get('review_notes', '')
        
        # Handle sequence advancement if this is part of a sequence
        sequence_advanced = False
        sequence = review.sequence
        if review.sequence_id:
            sequence_advanced, sequence = advance_sequence_for_review(review, data['recommendation'])
        
        apply_topic_status_for_review(review, data['recommendation'], sequence)
        
        db.session.commit()
        
        response_data = {
            'message': 'Review submitted successfully',
            'review': review.to_dict()
        }
        
        if sequence_advanced:
            response_data['sequence_advanced'] = True
            response_data['message'] += ' and sequence advanced to next reviewer'
        
        return jsonify(response_data)
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@reviews_bp.route('/<int:review_id>/follow-up', methods=['POST'])
@jwt_required()
def follow_up_review(review_id):
    """Send a follow-up reminder for a pending review"""
    try:
        # Get the review
        review = Review.query.get_or_404(review_id)
        
        # Check if review is still pending
        if review.status != 'pending':
            return jsonify({'error': 'Can only send follow-ups for pending reviews'}), 400
        
        # Get reviewer, topic, and review token
        reviewer = review.reviewer
        topic = review.topic
        
        # Find the review token for this review, or create one if missing
        review_token = ReviewToken.query.filter_by(review_id=review.id).first()
        if not review_token:
            # Create a new token if one doesn't exist
            current_app.logger.warning(f" No token found for review {review_id}, creating new one")
            import secrets
            from datetime import timedelta
            
            review_token = ReviewToken(
                token=secrets.token_urlsafe(32),
                review_id=review.id,
                reviewer_email=reviewer.email,
                expires_at=review.due_date + timedelta(days=7) if review.due_date else datetime.utcnow() + timedelta(days=14)
            )
            db.session.add(review_token)
            db.session.commit()
            current_app.logger.info(f" Created new token for review {review_id}: {review_token.token[:10]}...")
        
        # Send follow-up reminder email
        current_app.logger.debug(f" Sending follow-up reminder for review {review_id}")
        current_app.logger.debug(f"📧 Reviewer: {reviewer.name} ({reviewer.email})")
        current_app.logger.debug(f"📝 Topic: {topic.title}")
        
        try:
            # Use existing reminder email service, but with "Second Request:" prefix
            email_sent = email_service.send_review_reminder(
                reviewer_email=reviewer.email,
                reviewer_name=reviewer.name,
                topic_title=topic.title,
                due_date=review.due_date,
                review_token=review_token.token,
                is_follow_up=True  # This will modify the subject line
            )
            
            # Always record follow-up attempt so UI reflects action.
            review.follow_up_sent_at = datetime.utcnow()
            review.email_delivery_unavailable = not email_sent
            db.session.commit()

            if email_sent:
                current_app.logger.info(f" Follow-up reminder sent successfully to {reviewer.email}")
                return jsonify({
                    'message': 'Follow-up reminder sent successfully',
                    'review': review.to_dict(),
                    'email_sent': True
                }), 200

            current_app.logger.warning(f" Follow-up recorded but email delivery failed for {reviewer.email}")
            return jsonify({
                'message': 'Follow-up recorded, but email delivery failed',
                'review': review.to_dict(),
                'email_sent': False,
                'warning': 'Email delivery is unavailable. Check email service configuration.'
            }), 200
                
        except Exception as email_error:
            current_app.logger.error(f" Follow-up email error: {str(email_error)}")
            # Preserve action result even if email transport fails.
            review.follow_up_sent_at = datetime.utcnow()
            review.email_delivery_unavailable = True
            db.session.commit()
            return jsonify({
                'message': 'Follow-up recorded, but email delivery failed',
                'review': review.to_dict(),
                'email_sent': False,
                'warning': str(email_error)
            }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reviews_bp.route('/pending', methods=['GET'])
@jwt_required()
def get_pending_reviews():
    """Get all pending reviews for the current user"""
    try:
        reviewer_id = request.args.get('reviewer_id', type=int)
        
        if reviewer_id:
            # Get reviews assigned to specific reviewer
            reviews = Review.query.filter(
                and_(
                    Review.reviewer_id == reviewer_id,
                    Review.status.in_(['pending', 'in_progress'])
                )
            ).order_by(Review.due_date.asc()).all()
        else:
            # Get all pending reviews
            reviews = Review.query.filter(
                Review.status.in_(['pending', 'in_progress'])
            ).order_by(Review.due_date.asc()).all()
        
        return jsonify([review.to_dict() for review in reviews])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reviews_bp.route('/my-reviews', methods=['GET'])
@jwt_required()
def get_my_reviews():
    """Get reviews requested by the current user"""
    try:
        requester_id = request.args.get('requester_id', type=int)
        
        if not requester_id:
            return jsonify({'error': 'requester_id is required'}), 400
            
        reviews = Review.query.filter(
            Review.requested_by == requester_id
        ).order_by(Review.requested_at.desc()).all()
        
        return jsonify([review.to_dict() for review in reviews])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reviews_bp.route('/topic/<int:topic_id>/reviews', methods=['GET'])
@jwt_required()
def get_topic_reviews(topic_id):
    """Get all reviews for a specific topic"""
    try:
        reviews = Review.query.filter(
            Review.topic_id == topic_id
        ).order_by(Review.requested_at.desc()).all()
        
        return jsonify([review.to_dict() for review in reviews])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reviews_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_review_stats():
    """Get review statistics"""
    try:
        # Get overall stats
        total_reviews = Review.query.count()
        pending_reviews = Review.query.filter(Review.status == 'pending').count()
        in_progress_reviews = Review.query.filter(Review.status == 'in_progress').count()
        completed_reviews = Review.query.filter(Review.status == 'completed').count()
        
        # Calculate average completion time for completed reviews
        completed_with_times = Review.query.filter(
            and_(
                Review.status == 'completed',
                Review.completed_at.isnot(None),
                Review.requested_at.isnot(None)
            )
        ).all()
        
        avg_completion_days = 0
        if completed_with_times:
            total_days = sum([
                (review.completed_at - review.requested_at).days 
                for review in completed_with_times
            ])
            avg_completion_days = round(total_days / len(completed_with_times), 1)
        
        # Get overdue reviews
        overdue_reviews = Review.query.filter(
            and_(
                Review.status.in_(['pending', 'in_progress']),
                Review.due_date < datetime.utcnow()
            )
        ).count()
        
        return jsonify({
            'total': total_reviews,
            'pending': pending_reviews,
            'in_progress': in_progress_reviews,
            'completed': completed_reviews,
            'overdue': overdue_reviews,
            'avg_completion_days': avg_completion_days,
            'topics': {
                'total': total_reviews,  # Using review count as proxy
                'pending_review': pending_reviews,
                'draft': 0,  # Placeholder
                'published': completed_reviews
            },
            'imports': {
                'total': 0,
                'pending': 0,
                'sme_approved': 0,
                'final_approved': 0
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Legacy endpoints for backward compatibility
@reviews_bp.route('/topics/pending', methods=['GET'])
@jwt_required()
def get_pending_topic_reviews():
    """Get topics that need review (legacy endpoint)"""
    try:
        # Get topics with pending reviews
        pending_reviews = Review.query.filter(
            Review.status.in_(['pending', 'in_progress'])
        ).all()
        
        result = []
        for review in pending_reviews:
            topic_dict = review.topic.to_dict()
            topic_dict['review_id'] = review.id
            topic_dict['reviewer_name'] = review.reviewer.name
            topic_dict['due_date'] = review.due_date.isoformat() if review.due_date else None
            topic_dict['priority'] = review.priority
            result.append(topic_dict)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reviews_bp.route('/collections/pending', methods=['GET'])
@jwt_required()
def get_pending_collection_reviews():
    """Get collections that need review"""
    try:
        # For now, return empty array - collections review system can be implemented later
        return jsonify([])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reviews_bp.route('/imports/pending', methods=['GET'])
@jwt_required()
def get_pending_import_reviews():
    """Get imports that need review"""
    try:
        # For now, return empty array - imports review system can be implemented later
        return jsonify([])
    except Exception as e:
        return jsonify({'error': str(e)}), 500
