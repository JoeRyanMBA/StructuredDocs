# backend/routes/review_tokens.py

import secrets
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, render_template_string
from ..models import db, ReviewToken, Review, ReviewFeedback, Topic
from sqlalchemy.exc import IntegrityError

review_tokens_bp = Blueprint('review_tokens_api', __name__)


@review_tokens_bp.route('/api/reviews/<int:review_id>/generate-token', methods=['POST'])
def generate_review_token(review_id):
    """Generate a secure token for external reviewer access"""
    try:
        # Get the review
        review = Review.query.get_or_404(review_id)
        
        data = request.get_json() or {}
        
        # Generate secure token
        token = secrets.token_urlsafe(32)
        
        # Set expiration (default 30 days)
        expires_in_days = data.get('expires_in_days', 30)
        expires_at = datetime.now() + timedelta(days=expires_in_days)
        
        # Create token record
        review_token = ReviewToken(
            token=token,
            review_id=review_id,
            reviewer_email=review.reviewer.email if review.reviewer else data.get('reviewer_email'),
            expires_at=expires_at,
            max_access_count=data.get('max_access_count', 10)
        )
        
        db.session.add(review_token)
        db.session.commit()
        
        # Generate email template
        email_template = generate_email_template(review, review_token)
        
        return jsonify({
            'success': True,
            'token': token,
            'review_url': f'/review/{token}',
            'expires_at': expires_at.isoformat(),
            'email_template': email_template
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@review_tokens_bp.route('/api/review/<token>', methods=['GET'])
def get_review_by_token(token):
    """Get review content using secure token (for external reviewers)"""
    try:
        # Find and validate token
        review_token = ReviewToken.query.filter_by(token=token).first()
        if not review_token:
            return jsonify({'error': 'Invalid review token'}), 404
            
        is_valid, message = review_token.is_valid()
        if not is_valid:
            return jsonify({'error': message}), 403
            
        # Update access tracking
        review_token.access_count += 1
        if not review_token.accessed_at:
            review_token.accessed_at = datetime.now()
        db.session.commit()
        
        # Get review and topic data
        review = review_token.review
        topic = review.topic
        
        # Get existing feedback for this review
        feedback_items = ReviewFeedback.query.filter_by(review_id=review.id).all()
        
        return jsonify({
            'success': True,
            'review': {
                'id': review.id,
                'topic_id': topic.id,
                'topic_title': topic.title,
                'topic_content': topic.content,
                'author_message': review.author_message,
                'due_date': review.due_date.isoformat() if review.due_date else None,
                'priority': review.priority,
                'status': review.status
            },
            'feedback_items': [item.to_dict() for item in feedback_items],
            'token_info': {
                'access_count': review_token.access_count,
                'max_access_count': review_token.max_access_count,
                'expires_at': review_token.expires_at.isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@review_tokens_bp.route('/api/review/<token>/feedback', methods=['POST'])
def submit_review_feedback(token):
    """Submit structured feedback using token authentication"""
    try:
        # Validate token
        review_token = ReviewToken.query.filter_by(token=token).first()
        if not review_token:
            return jsonify({'error': 'Invalid review token'}), 404
            
        is_valid, message = review_token.is_valid()
        if not is_valid:
            return jsonify({'error': message}), 403
            
        data = request.get_json()
        feedback_items = data.get('feedback_items', [])
        overall_recommendation = data.get('recommendation')
        overall_feedback = data.get('feedback')
        edited_content = data.get('edited_content')  # NEW: Get edited content
        
        # Create feedback items
        created_items = []
        for item in feedback_items:
            feedback = ReviewFeedback(
                review_id=review_token.review_id,
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
                impact=item.get('impact', 'moderate')
            )
            db.session.add(feedback)
            created_items.append(feedback)
        
        # Update review with overall feedback
        review = review_token.review
        if overall_recommendation:
            review.recommendation = overall_recommendation
        if overall_feedback:
            review.feedback = overall_feedback
            
        # NEW: Handle edited content based on recommendation
        if edited_content and overall_recommendation == 'approve_with_changes':
            # Apply the edits directly to the topic
            topic = review.topic
            topic.content = edited_content
            topic.updated_at = datetime.now()
            print(f"✅ Applied reviewer edits to Topic {topic.id}")
        elif edited_content:
            # Store edited content for author review (future enhancement)
            review.edited_content = edited_content
            print(f"📝 Stored edited content for author review of Topic {review.topic.id}")
        
        review.status = 'completed'
        review.completed_at = datetime.now()
        
        # Mark token as used
        review_token.used_at = datetime.now()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Feedback submitted successfully',
            'feedback_items_count': len(created_items),
            'content_updated': edited_content is not None and overall_recommendation == 'approve_with_changes'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@review_tokens_bp.route('/api/reviews/<int:review_id>/feedback', methods=['GET'])
def get_review_feedback(review_id):
    """Get structured feedback for a review (for authors)"""
    try:
        review = Review.query.get_or_404(review_id)
        feedback_items = ReviewFeedback.query.filter_by(review_id=review_id).order_by(ReviewFeedback.created_at).all()
        
        return jsonify({
            'success': True,
            'review_id': review_id,
            'feedback_items': [item.to_dict() for item in feedback_items],
            'summary': {
                'total_items': len(feedback_items),
                'pending': len([f for f in feedback_items if f.status == 'pending']),
                'accepted': len([f for f in feedback_items if f.status == 'accepted']),
                'rejected': len([f for f in feedback_items if f.status == 'rejected'])
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@review_tokens_bp.route('/api/feedback/<int:feedback_id>/respond', methods=['PUT'])
def respond_to_feedback(feedback_id):
    """Author responds to specific feedback item"""
    try:
        feedback = ReviewFeedback.query.get_or_404(feedback_id)
        data = request.get_json()
        
        feedback.author_response = data.get('author_response')
        feedback.status = data.get('status')  # 'accepted', 'rejected', 'modified'
        feedback.responded_at = datetime.now()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'feedback': feedback.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


def generate_email_template(review, review_token):
    """Generate email template for review request"""
    
    template = """
Subject: Review Request: {{topic_title}} (Topic #{{topic_id}})

Dear {{reviewer_name}},

You have been asked to review the following content:

Topic #{{topic_id}}: {{topic_title}}
Due Date: {{due_date}}
Priority: {{priority}}

{{author_message}}

To access the review material and submit your feedback, please click the link below:
{{review_url}}

This secure link will expire on {{expires_at}} and can be accessed up to {{max_access}} times.

Instructions for Review:
1. Click the link above to access the content
2. Read through the material carefully
3. Use the feedback form to submit your comments
4. You can provide general feedback or specific suggestions for text changes
5. Please complete your review by the due date

If you have any questions or issues accessing the review, please contact the author directly.

Thank you for your time and expertise!

Best regards,
{{author_name}}
"""
    
    # Format the template
    topic = review.topic
    reviewer = review.reviewer
    author = review.requester
    
    formatted_template = template.replace('{{topic_title}}', topic.title or 'Untitled')
    formatted_template = formatted_template.replace('{{topic_id}}', str(topic.id))
    formatted_template = formatted_template.replace('{{reviewer_name}}', reviewer.name if reviewer else 'Reviewer')
    formatted_template = formatted_template.replace('{{due_date}}', review.due_date.strftime('%B %d, %Y') if review.due_date else 'No specific deadline')
    formatted_template = formatted_template.replace('{{priority}}', review.priority.title())
    formatted_template = formatted_template.replace('{{author_message}}', review.author_message or 'Please review this content and provide your feedback.')
    formatted_template = formatted_template.replace('{{review_url}}', f'http://localhost:5173/review/{review_token.token}')
    formatted_template = formatted_template.replace('{{expires_at}}', review_token.expires_at.strftime('%B %d, %Y'))
    formatted_template = formatted_template.replace('{{max_access}}', str(review_token.max_access_count))
    formatted_template = formatted_template.replace('{{author_name}}', author.name if author else 'Content Author')
    
    return formatted_template
