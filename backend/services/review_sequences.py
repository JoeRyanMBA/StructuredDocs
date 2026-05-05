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


def _send_sequential_assignment_email(sequence, next_step, next_review, next_token, total_reviewers, next_position):
    """Send step-assignment email with a fallback template path when primary send fails."""
    if not email_service:
        return False

    reviewer = next_step.reviewer
    if not reviewer or not reviewer.email:
        current_app.logger.warning(
            "Cannot send sequential assignment email: missing reviewer/email for sequence_id=%s step=%s",
            sequence.id,
            next_position,
        )
        return False

    email_sent = False
    if not next_token:
        current_app.logger.warning(
            "Cannot send sequential assignment email: missing token for sequence_id=%s step=%s",
            sequence.id,
            next_position,
        )
        return False

    try:
        email_sent = bool(email_service.send_review_request(
            reviewer_email=reviewer.email,
            reviewer_name=reviewer.name,
            topic_title=sequence.topic.title,
            author_name=sequence.creator.name if sequence.creator else 'Unknown',
            due_date=next_review.due_date,
            review_url=f"/review/{next_token.token}",
            author_message=next_review.author_message,
            is_sequential=True,
            sequence_position=next_position + 1,
            total_reviewers=total_reviewers,
            topic_id=sequence.topic_id
        ))

        if email_sent:
            return True

        current_app.logger.warning(
            "Primary sequential review email send returned False for review_id=%s, reviewer_id=%s",
            next_review.id,
            next_step.reviewer_id,
        )
    except Exception:
        current_app.logger.exception(
            "Primary sequential review email send failed for review_id=%s, reviewer_id=%s",
            next_review.id,
            next_step.reviewer_id,
        )

    try:
        fallback_sent = bool(email_service.send_review_notification(
            reviewer_email=reviewer.email,
            reviewer_name=reviewer.name,
            topic_title=sequence.topic.title,
            topic_id=sequence.topic_id,
            author_message=next_review.author_message,
            due_date=next_review.due_date,
            priority=next_review.priority,
            review_token=next_token.token,
        ))
        if not fallback_sent:
            current_app.logger.warning(
                "Fallback sequential review email send returned False for review_id=%s, reviewer_id=%s",
                next_review.id,
                next_step.reviewer_id,
            )
        return fallback_sent
    except Exception:
        current_app.logger.exception(
            "Fallback sequential review email send failed for review_id=%s, reviewer_id=%s",
            next_review.id,
            next_step.reviewer_id,
        )
        return False


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

    next_step = ReviewSequenceStep.query.filter(
        ReviewSequenceStep.sequence_id == sequence.id,
        ReviewSequenceStep.step_order > current_position,
    ).order_by(ReviewSequenceStep.step_order.asc()).first()

    if not next_step:
        sequence.status = 'completed'
        sequence.completed_at = now
        sequence.current_position = current_position
        return True, sequence

    next_position = next_step.step_order

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

    reviewer = next_step.reviewer
    reviewer_email = (reviewer.email or '').strip() if reviewer else ''
    next_token = create_review_token(next_review, reviewer_email) if reviewer_email else None

    sequence.current_position = next_position
    next_step.status = 'active'
    next_step.review_id = next_review.id
    next_step.assigned_at = now

    email_sent = _send_sequential_assignment_email(
        sequence=sequence,
        next_step=next_step,
        next_review=next_review,
        next_token=next_token,
        total_reviewers=total_reviewers,
        next_position=next_position,
    )
    next_review.email_delivery_unavailable = not email_sent

    if not email_sent:
        current_app.logger.warning(
            "Sequential review advanced to step %s but email delivery failed for review_id=%s",
            next_position + 1,
            next_review.id,
        )

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
