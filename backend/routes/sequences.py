import secrets

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from datetime import datetime, timedelta
from ..models import db, ReviewSequence, ReviewSequenceStep, Topic, Stakeholder, Review, ReviewToken
from sqlalchemy import and_, or_
from sqlalchemy import inspect, text
from ..extensions import limiter
from ..services.review_sequences import create_review_token
from ..utils.email_service import email_service

sequences_bp = Blueprint('sequences', __name__, url_prefix='/api/sequences')


def _schema_drift_response(error):
    message = str(error)
    if 'review_sequences.created_by' in message and 'does not exist' in message:
        try:
            inspector = inspect(db.engine)
            columns = {column.get('name') for column in inspector.get_columns('review_sequences')}
            if 'created_by' not in columns:
                return jsonify({
                    'error': 'Database schema is out of date for sequential reviews. Run backend migrations (flask db upgrade) to add review_sequences.created_by.'
                }), 500
        except Exception:
            # If we cannot inspect the schema, preserve the original drift guidance.
            return jsonify({
                'error': 'Database schema is out of date for sequential reviews. Run backend migrations (flask db upgrade) to add review_sequences.created_by.'
            }), 500

        # Column exists; surface the real backend error instead of a stale drift message.
        return jsonify({'error': message}), 500
    return None


def _ensure_review_sequences_schema():
    """Runtime guard for older deployments missing sequential review columns."""
    try:
        inspector = inspect(db.engine)
        table_names = set(inspector.get_table_names())
        if 'review_sequences' not in table_names:
            return jsonify({'error': 'review_sequences table is missing. Run backend migrations.'}), 500
        if 'review_sequence_steps' not in table_names:
            return jsonify({'error': 'review_sequence_steps table is missing. Run backend migrations.'}), 500

        columns = {column.get('name') for column in inspector.get_columns('review_sequences')}
        statements = []

        # Add as nullable to stay compatible with existing rows on legacy databases.
        if 'created_by' not in columns:
            statements.append('ALTER TABLE review_sequences ADD COLUMN created_by INTEGER')

        # Keep defaults aligned with model behavior.
        if 'current_position' not in columns:
            statements.append('ALTER TABLE review_sequences ADD COLUMN current_position INTEGER NOT NULL DEFAULT 0')
        if 'auto_advance_on_approve' not in columns:
            statements.append('ALTER TABLE review_sequences ADD COLUMN auto_advance_on_approve BOOLEAN NOT NULL DEFAULT TRUE')
        if 'pause_on_changes' not in columns:
            statements.append('ALTER TABLE review_sequences ADD COLUMN pause_on_changes BOOLEAN NOT NULL DEFAULT TRUE')

        # Lifecycle timestamps for sequence flow.
        if 'started_at' not in columns:
            statements.append('ALTER TABLE review_sequences ADD COLUMN started_at TIMESTAMP')
        if 'completed_at' not in columns:
            statements.append('ALTER TABLE review_sequences ADD COLUMN completed_at TIMESTAMP')
        if 'paused_at' not in columns:
            statements.append('ALTER TABLE review_sequences ADD COLUMN paused_at TIMESTAMP')

        step_columns = {column.get('name') for column in inspector.get_columns('review_sequence_steps')}

        # Step ordering and metadata required by ReviewSequenceStep model.
        if 'step_order' not in step_columns:
            statements.append('ALTER TABLE review_sequence_steps ADD COLUMN step_order INTEGER NOT NULL DEFAULT 0')
        if 'reviewer_role' not in step_columns:
            statements.append('ALTER TABLE review_sequence_steps ADD COLUMN reviewer_role VARCHAR(100)')
        if 'step_name' not in step_columns:
            statements.append('ALTER TABLE review_sequence_steps ADD COLUMN step_name VARCHAR(200)')
        if 'instructions' not in step_columns:
            statements.append('ALTER TABLE review_sequence_steps ADD COLUMN instructions TEXT')
        if 'review_id' not in step_columns:
            statements.append('ALTER TABLE review_sequence_steps ADD COLUMN review_id INTEGER')
        if 'assigned_at' not in step_columns:
            statements.append('ALTER TABLE review_sequence_steps ADD COLUMN assigned_at TIMESTAMP')
        if 'completed_at' not in step_columns:
            statements.append('ALTER TABLE review_sequence_steps ADD COLUMN completed_at TIMESTAMP')

        # Status was introduced with step lifecycle tracking.
        if 'status' not in step_columns:
            statements.append("ALTER TABLE review_sequence_steps ADD COLUMN status VARCHAR(50) NOT NULL DEFAULT 'pending'")

        for statement in statements:
            db.session.execute(text(statement))

        normalized_legacy = False

        # Legacy compatibility: some databases still have a NOT NULL `position`
        # column on review_sequence_steps while newer code writes `step_order`.
        # Ensure inserts succeed by backfilling and setting a default.
        if 'position' in step_columns:
            db.session.execute(text('UPDATE review_sequence_steps SET position = COALESCE(position, step_order, 0) WHERE position IS NULL'))
            db.session.execute(text('ALTER TABLE review_sequence_steps ALTER COLUMN position SET DEFAULT 0'))
            normalized_legacy = True

        # Older schemas used `name` instead of `step_name` with NOT NULL.
        # Keep legacy column valid for inserts driven by the newer model.
        if 'name' in step_columns:
            db.session.execute(text("UPDATE review_sequence_steps SET name = COALESCE(name, step_name, 'Review Step') WHERE name IS NULL"))
            db.session.execute(text("ALTER TABLE review_sequence_steps ALTER COLUMN name SET DEFAULT 'Review Step'"))
            normalized_legacy = True

        if statements:
            db.session.commit()
            current_app.logger.warning('Auto-repaired review_sequences schema at runtime (added missing columns).')
        elif normalized_legacy:
            db.session.commit()
            current_app.logger.warning('Normalized legacy review_sequence_steps defaults at runtime.')

        return None
    except Exception as exc:
        db.session.rollback()
        current_app.logger.exception('Failed to auto-repair review_sequences schema')
        return jsonify({
            'error': f'Database schema is out of date for sequential reviews and auto-repair failed: {exc}'
        }), 500


@sequences_bp.route('/', methods=['POST'])
@jwt_required()
def create_review_sequence():
    """Create a new review sequence for a topic"""
    try:
        schema_fix = _ensure_review_sequences_schema()
        if schema_fix:
            return schema_fix

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
                            total_reviewers=len(data['reviewers']),
                            topic_id=topic.id
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
        schema_response = _schema_drift_response(e)
        if schema_response:
            return schema_response
        return jsonify({'error': str(e)}), 500

@sequences_bp.route('/<int:sequence_id>', methods=['GET'])
@jwt_required()
@limiter.exempt
def get_review_sequence(sequence_id):
    """Get details of a specific review sequence"""
    try:
        schema_fix = _ensure_review_sequences_schema()
        if schema_fix:
            return schema_fix

        sequence = ReviewSequence.query.get_or_404(sequence_id)
        return jsonify(sequence.to_dict(include_steps=True))
    except Exception as e:
        schema_response = _schema_drift_response(e)
        if schema_response:
            return schema_response
        return jsonify({'error': str(e)}), 500


@sequences_bp.route('/<int:sequence_id>/update', methods=['POST'])
@jwt_required()
def update_review_sequence(sequence_id):
    """Update sequence metadata and reviewer steps before reviews are assigned."""
    try:
        schema_fix = _ensure_review_sequences_schema()
        if schema_fix:
            return schema_fix

        sequence = ReviewSequence.query.get_or_404(sequence_id)
        data = request.get_json() or {}

        reviewers = data.get('reviewers')
        if not isinstance(reviewers, list) or len(reviewers) == 0:
            return jsonify({'error': 'At least one reviewer is required'}), 400

        # Do not allow step edits once any review has been assigned.
        existing_steps = ReviewSequenceStep.query.filter_by(sequence_id=sequence.id).all()
        if any(step.review_id for step in existing_steps):
            return jsonify({'error': 'Cannot edit reviewer steps after a sequence has started. Create a new sequence for additional reviewers.'}), 400

        sequence.name = (data.get('name') or '').strip() or sequence.name
        sequence.description = data.get('description')
        if 'auto_advance_on_approve' in data:
            sequence.auto_advance_on_approve = bool(data.get('auto_advance_on_approve'))
        if 'pause_on_changes' in data:
            sequence.pause_on_changes = bool(data.get('pause_on_changes'))

        # Replace existing unassigned steps with submitted order.
        for step in existing_steps:
            db.session.delete(step)
        db.session.flush()

        for i, reviewer_data in enumerate(reviewers):
            reviewer = Stakeholder.query.get(reviewer_data.get('reviewer_id'))
            if not reviewer:
                return jsonify({'error': f'Reviewer {reviewer_data.get("reviewer_id")} not found'}), 404

            step = ReviewSequenceStep(
                sequence_id=sequence.id,
                step_order=i,
                reviewer_id=reviewer.id,
                reviewer_role=reviewer.role,
                step_name=(reviewer_data.get('step_name') or '').strip() or f'Review Step {i + 1}',
                instructions=reviewer_data.get('instructions'),
                status='pending',
            )
            db.session.add(step)

        # Reset pointer to first step for edited unstarted sequence.
        sequence.current_position = 0
        db.session.commit()

        return jsonify({
            'message': 'Sequence updated successfully',
            'sequence': sequence.to_dict(include_steps=True)
        }), 200
    except Exception as e:
        db.session.rollback()
        schema_response = _schema_drift_response(e)
        if schema_response:
            return schema_response
        return jsonify({'error': str(e)}), 500

@sequences_bp.route('/topic/<int:topic_id>', methods=['GET'])
@jwt_required()
@limiter.exempt
def get_topic_sequences(topic_id):
    """Get all review sequences for a topic"""
    try:
        schema_fix = _ensure_review_sequences_schema()
        if schema_fix:
            return schema_fix

        sequences = ReviewSequence.query.filter_by(topic_id=topic_id).order_by(ReviewSequence.created_at.desc()).all()
        return jsonify([seq.to_dict(include_steps=True) for seq in sequences])
    except Exception as e:
        schema_response = _schema_drift_response(e)
        if schema_response:
            return schema_response
        return jsonify({'error': str(e)}), 500

@sequences_bp.route('/<int:sequence_id>/advance', methods=['POST'])
@jwt_required()
def advance_sequence(sequence_id):
    """Manually advance a sequence to the next reviewer"""
    try:
        schema_fix = _ensure_review_sequences_schema()
        if schema_fix:
            return schema_fix

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
        
        # Move to the next available step by order, even if legacy data has gaps.
        next_step = ReviewSequenceStep.query.filter(
            ReviewSequenceStep.sequence_id == sequence.id,
            ReviewSequenceStep.step_order > sequence.current_position,
        ).order_by(ReviewSequenceStep.step_order.asc()).first()
        
        if not next_step:
            # Sequence is complete
            sequence.status = 'completed'
            sequence.completed_at = datetime.utcnow()
            db.session.commit()
            return jsonify({
                'message': 'Review sequence completed',
                'sequence': sequence.to_dict()
            })

        next_position = next_step.step_order
        
        # Create review for next step
        data = request.get_json() or {}
        requester = Stakeholder.query.get(sequence.created_by) if sequence.created_by else None
        if not requester:
            requester = Stakeholder.query.filter(Stakeholder.can_review == True).order_by(Stakeholder.id.asc()).first()
        if not requester:
            return jsonify({'error': 'Unable to resolve requester stakeholder for this sequence'}), 400

        review = Review(
            topic_id=sequence.topic_id,
            requested_by=requester.id,
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
