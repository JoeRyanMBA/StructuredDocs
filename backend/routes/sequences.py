import secrets

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from datetime import datetime, timedelta
from ..models import db, ReviewSequence, ReviewSequenceStep, Topic, Stakeholder, Review, ReviewToken
from sqlalchemy import and_, or_
from ..services.review_sequences import create_review_token
from ..utils.email_service import email_service

sequences_bp = Blueprint('sequences', __name__, url_prefix='/api/sequences')
@sequences_bp.route('/', methods=['POST'])
@jwt_required()
def create_review_sequence():
    """Create a new review sequence for a topic"""
    try:
        data = request.get_json() or {}
        
        # Validate required fields
        if not data.get('topic_id'):
            return jsonify({'error': 'topic_id is required'}), 400
        
        if not data.get('reviewers') or not isinstance(data['reviewers'], list):
            return jsonify({'error': 'reviewers list is required'}), 400
        
        if len(data['reviewers']) == 0:
            return jsonify({'error': 'At least one reviewer is required'}), 400
        
        # Validate topic exists
        topic = Topic.query.get(data['topic_id'])
        if not topic:
            return jsonify({'error': 'Topic not found'}), 404
        
        # Check if topic already has an active sequence
        existing_sequence = ReviewSequence.query.filter_by(
            topic_id=data['topic_id'],
            status='active'
        ).first()
        
        if existing_sequence:
            return jsonify({'error': 'Topic already has an active review sequence'}), 400
        
        # Determine requester stakeholder (author) for generated Review rows
        requester_id = data.get('created_by')
        requester = Stakeholder.query.get(requester_id) if requester_id else None

        # Fallback: use first reviewer as requester if provided requester is invalid/missing
        if not requester:
            first_reviewer_id = data['reviewers'][0].get('reviewer_id')
            requester = Stakeholder.query.get(first_reviewer_id) if first_reviewer_id else None

        if not requester:
            return jsonify({'error': 'Unable to resolve requester stakeholder for this sequence'}), 400

        sequence_name = (data.get('name') or '').strip() or f"Review Sequence for Topic {data['topic_id']}"

        # Create the sequence
        sequence = ReviewSequence(
            topic_id=data['topic_id'],
            created_by=requester.id,
            name=sequence_name,
            description=data.get('description'),
            current_position=0,
            auto_advance_on_approve=data.get('auto_advance_on_approve', True),
            pause_on_changes=data.get('pause_on_changes', True),
            started_at=datetime.utcnow() if data.get('auto_start', True) else None,
        )
        
        db.session.add(sequence)
        db.session.flush()  # Get the sequence ID
        
        # Create sequence steps for each reviewer
        for i, reviewer_data in enumerate(data['reviewers']):
            # Validate reviewer exists
            reviewer = Stakeholder.query.get(reviewer_data.get('reviewer_id'))
            if not reviewer:
                return jsonify({'error': f'Reviewer {reviewer_data.get("reviewer_id")} not found'}), 404
            
            step = ReviewSequenceStep(
                sequence_id=sequence.id,
                step_order=i,
                reviewer_id=reviewer_data['reviewer_id'],
                reviewer_role=reviewer.role,
                step_name=(reviewer_data.get('step_name') or '').strip() or f'Review Step {i + 1}',
                instructions=reviewer_data.get('instructions'),
                status='pending',
            )
            db.session.add(step)
        
        # Start the sequence by assigning the first reviewer
        if data.get('auto_start', True):
            first_step = ReviewSequenceStep.query.filter_by(
                sequence_id=sequence.id,
                step_order=0
            ).first()
            
            if first_step:
                # Create the first review
                review = Review(
                    topic_id=sequence.topic_id,
                    requested_by=requester.id,
                    reviewer_id=first_step.reviewer_id,
                    sequence_id=sequence.id,
                    sequence_position=0,
                    author_message=data.get('initial_message', ''),
                    priority=data.get('priority', 'medium'),
                    due_date=datetime.utcnow() + timedelta(days=data.get('days_per_review', 5))
                )
                db.session.add(review)
                db.session.flush()
                review_token = create_review_token(review, first_step.reviewer.email)
                first_step.status = 'active'
                first_step.review_id = review.id
                first_step.assigned_at = datetime.utcnow()
                topic.status = 'pending_review'
                topic.updated_at = datetime.utcnow()
                
                # Send notification email
                if email_service:
                    try:
                        email_service.send_review_request(
                            reviewer_email=first_step.reviewer.email,
                            reviewer_name=first_step.reviewer.name,
                            topic_title=topic.title,
                            author_name=requester.name,
                            due_date=review.due_date,
                            review_url=f"/review/{review_token.token}",
                            author_message=review.author_message,
                            is_sequential=True,
                            sequence_position=1,
                            total_reviewers=len(data['reviewers'])
                        )
                    except Exception as e:
                        # Don't fail the whole operation if email fails
                        current_app.logger.debug(f"Failed to send email notification: {e}")
        
        db.session.commit()
        
        return jsonify({
            'message': 'Review sequence created successfully',
            'sequence': sequence.to_dict(include_steps=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@sequences_bp.route('/<int:sequence_id>', methods=['GET'])
@jwt_required()
def get_review_sequence(sequence_id):
    """Get details of a specific review sequence"""
    try:
        sequence = ReviewSequence.query.get_or_404(sequence_id)
        return jsonify(sequence.to_dict(include_steps=True))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sequences_bp.route('/topic/<int:topic_id>', methods=['GET'])
@jwt_required()
def get_topic_sequences(topic_id):
    """Get all review sequences for a topic"""
    try:
        sequences = ReviewSequence.query.filter_by(topic_id=topic_id).order_by(ReviewSequence.created_at.desc()).all()
        return jsonify([seq.to_dict(include_steps=True) for seq in sequences])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sequences_bp.route('/<int:sequence_id>/advance', methods=['POST'])
@jwt_required()
def advance_sequence(sequence_id):
    """Manually advance a sequence to the next reviewer"""
    try:
        sequence = ReviewSequence.query.get_or_404(sequence_id)
        
        if sequence.status != 'active':
            return jsonify({'error': 'Sequence is not active'}), 400
        
        # Check if we can advance
        current_step = ReviewSequenceStep.query.filter_by(
            sequence_id=sequence.id,
            step_order=sequence.current_position
        ).first()
        
        if not current_step:
            return jsonify({'error': 'Current step not found'}), 404
        
        # Mark current step as completed if it has a review
        if current_step.review_id:
            current_review = Review.query.get(current_step.review_id)
            if current_review and current_review.status != 'completed':
                return jsonify({'error': 'Current review must be completed before advancing'}), 400
        
        # Move to next step
        next_position = sequence.current_position + 1
        next_step = ReviewSequenceStep.query.filter_by(
            sequence_id=sequence.id,
            step_order=next_position
        ).first()
        
        if not next_step:
            # Sequence is complete
            sequence.status = 'completed'
            sequence.completed_at = datetime.utcnow()
            db.session.commit()
            return jsonify({
                'message': 'Review sequence completed',
                'sequence': sequence.to_dict()
            })
        
        # Create review for next step
        data = request.get_json() or {}
        review = Review(
            topic_id=sequence.topic_id,
            requested_by=sequence.created_by,
            reviewer_id=next_step.reviewer_id,
            sequence_id=sequence.id,
            sequence_position=next_position,
            author_message=data.get('message', f'Sequential review (step {next_position + 1} of {len(sequence.steps)})'),
            priority=data.get('priority', 'medium'),
            due_date=datetime.utcnow() + timedelta(days=data.get('days_per_review', 5))
        )
        db.session.add(review)
        db.session.flush()
        review_token = create_review_token(review, next_step.reviewer.email)
        
        # Update sequence and step
        sequence.current_position = next_position
        next_step.status = 'active'
        next_step.review_id = review.id
        next_step.assigned_at = datetime.utcnow()
        
        # Send notification
        if email_service:
            try:
                email_service.send_review_request(
                    reviewer_email=next_step.reviewer.email,
                    reviewer_name=next_step.reviewer.name,
                    topic_title=sequence.topic.title,
                    author_name=sequence.creator.name if sequence.creator else 'Unknown',
                    due_date=review.due_date,
                    review_url=f"/review/{review_token.token}",
                    author_message=review.author_message,
                    is_sequential=True,
                    sequence_position=next_position + 1,
                    total_reviewers=len(sequence.steps)
                )
            except Exception as e:
                current_app.logger.debug(f"Failed to send email notification: {e}")
        
        db.session.commit()
        
        return jsonify({
            'message': f'Sequence advanced to reviewer {next_step.reviewer.name}',
            'sequence': sequence.to_dict(),
            'new_review': review.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@sequences_bp.route('/<int:sequence_id>/pause', methods=['POST'])
@jwt_required()
def pause_sequence(sequence_id):
    """Pause a review sequence"""
    try:
        sequence = ReviewSequence.query.get_or_404(sequence_id)
        
        if sequence.status != 'active':
            return jsonify({'error': 'Sequence is not active'}), 400
        
        sequence.status = 'paused'
        sequence.paused_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Review sequence paused',
            'sequence': sequence.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@sequences_bp.route('/<int:sequence_id>/resume', methods=['POST'])
@jwt_required()
def resume_sequence(sequence_id):
    """Resume a paused review sequence"""
    try:
        sequence = ReviewSequence.query.get_or_404(sequence_id)
        
        if sequence.status != 'paused':
            return jsonify({'error': 'Sequence is not paused'}), 400
        
        sequence.status = 'active'
        sequence.paused_at = None
        
        db.session.commit()
        
        return jsonify({
            'message': 'Review sequence resumed',
            'sequence': sequence.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
