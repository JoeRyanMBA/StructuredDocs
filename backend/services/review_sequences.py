import secrets
from datetime import datetime, timedelta

from flask import current_app

from ..models import Review, ReviewSequenceStep, ReviewToken, db
from ..utils.email_service import email_service


def create_review_token(review, reviewer_email):
    token = ReviewToken(
        token=secrets.token_urlsafe(32),
        review_id=review.id,
        reviewer_email=reviewer_email,
        expires_at=(
            review.due_date + timedelta(days=7)
            if review.due_date
            else datetime.utcnow() + timedelta(days=14)
        ),
    )
    db.session.add(token)
    db.session.flush()
    return token


def advance_sequence_for_review(review, recommendation):
    sequence = review.sequence
    if not sequence or sequence.status != 'active':
        return False, sequence

    now = datetime.utcnow()
    current_position = review.sequence_position if review.sequence_position is not None else sequence.current_position
    current_step = ReviewSequenceStep.query.filter_by(
        sequence_id=sequence.id,
        step_order=current_position,
    ).first()

    if current_step:
        current_step.status = 'completed'
        current_step.completed_at = now
        current_step.review_id = current_step.review_id or review.id

    should_advance = False
    if recommendation == 'approve' and sequence.auto_advance_on_approve:
        should_advance = True
    elif recommendation in {'approve_with_changes', 'needs_more_info', 'reject'}:
        if sequence.pause_on_changes:
            sequence.status = 'paused'
            sequence.paused_at = now
        else:
            should_advance = True

    if not should_advance:
        return False, sequence

    next_position = current_position + 1
    next_step = ReviewSequenceStep.query.filter_by(
        sequence_id=sequence.id,
        step_order=next_position,
    ).first()

    if not next_step:
        sequence.status = 'completed'
        sequence.completed_at = now
        sequence.current_position = current_position
        return True, sequence

    total_reviewers = len(sequence.steps)
    next_review = Review(
        topic_id=sequence.topic_id,
        requested_by=sequence.created_by,
        reviewer_id=next_step.reviewer_id,
        sequence_id=sequence.id,
        sequence_position=next_position,
        author_message=(
            f'Sequential review (step {next_position + 1} of {total_reviewers}). '
            f'Previous reviewer: {recommendation}'
        ),
        priority=review.priority,
        due_date=datetime.utcnow() + timedelta(days=5),
    )
    db.session.add(next_review)
    db.session.flush()

    next_token = create_review_token(next_review, next_step.reviewer.email)

    sequence.current_position = next_position
    next_step.status = 'active'
    next_step.review_id = next_review.id
    next_step.assigned_at = now

    if email_service:
        try:
            email_service.send_review_request(
                reviewer_email=next_step.reviewer.email,
                reviewer_name=next_step.reviewer.name,
                topic_title=sequence.topic.title,
                author_name=sequence.creator.name if sequence.creator else 'Unknown',
                due_date=next_review.due_date,
                review_url=f"/review/{next_token.token}",
                author_message=next_review.author_message,
                is_sequential=True,
                sequence_position=next_position + 1,
                total_reviewers=total_reviewers,
            )
        except Exception as exc:
            current_app.logger.debug(f"Failed to send email notification: {exc}")

    return True, sequence


def apply_topic_status_for_review(review, recommendation, sequence):
    topic = review.topic

    if review.sequence_id and sequence:
        if sequence.status == 'completed':
            if recommendation == 'approve':
                topic.status = 'approved'
            elif recommendation == 'approve_with_changes':
                topic.status = 'revisions_requested'
            elif recommendation == 'needs_more_info':
                topic.status = 'draft'
            elif recommendation == 'reject':
                topic.status = 'rejected'
        elif sequence.status == 'paused':
            if recommendation == 'approve_with_changes':
                topic.status = 'revisions_requested'
            elif recommendation == 'needs_more_info':
                topic.status = 'draft'
            elif recommendation == 'reject':
                topic.status = 'rejected'
            else:
                topic.status = 'revisions_requested'
        else:
            topic.status = 'pending_review'
    else:
        if recommendation == 'approve':
            topic.status = 'approved'
        elif recommendation == 'approve_with_changes':
            topic.status = 'revisions_requested'
        elif recommendation == 'needs_more_info':
            topic.status = 'draft'
        elif recommendation == 'reject':
            topic.status = 'rejected'

    topic.updated_at = datetime.utcnow()
