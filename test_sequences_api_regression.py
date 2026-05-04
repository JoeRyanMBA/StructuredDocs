from datetime import datetime, timedelta

import pytest

from flask_jwt_extended import create_access_token

from backend.app import create_app
from backend.models import Review, ReviewToken, Stakeholder, Topic, User, db
from backend.utils.email_service import email_service


@pytest.fixture()
def app(tmp_path, monkeypatch):
    monkeypatch.setenv('ENABLE_BLUEPRINTS', 'sequences,review_tokens')
    monkeypatch.delenv('SKIP_BLUEPRINTS', raising=False)
    monkeypatch.setenv('DATABASE_URL', f"sqlite:///{tmp_path / 'sequences_regression.db'}")

    flask_app = create_app()
    flask_app.config['TESTING'] = True

    with flask_app.app_context():
        db.create_all()

    yield flask_app

    with flask_app.app_context():
        db.session.remove()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def auth_header(app):
    with app.app_context():
        user = User(name='Sequence User', email='sequence-user@example.com', role='author')
        db.session.add(user)
        db.session.commit()
        token = create_access_token(identity=str(user.id))

    return {'Authorization': f'Bearer {token}'}


@pytest.fixture()
def seeded_data(app):
    with app.app_context():
        requester = Stakeholder(
            name='Sequence Author',
            email='sequence-author@example.com',
            role='author',
            can_review=False,
            active=True,
        )
        first_reviewer = Stakeholder(
            name='First Reviewer',
            email='first-reviewer@example.com',
            role='reviewer',
            can_review=True,
            active=True,
        )
        second_reviewer = Stakeholder(
            name='Second Reviewer',
            email='second-reviewer@example.com',
            role='reviewer',
            can_review=True,
            active=True,
        )
        topic = Topic(title='Sequential Topic', content='Draft content', status='draft')

        db.session.add_all([requester, first_reviewer, second_reviewer, topic])
        db.session.commit()

        return {
            'requester_id': requester.id,
            'first_reviewer_id': first_reviewer.id,
            'first_reviewer_email': first_reviewer.email,
            'second_reviewer_id': second_reviewer.id,
            'topic_id': topic.id,
        }


def test_create_sequence_uses_public_review_token_link(client, app, auth_header, seeded_data, monkeypatch):
    captured = {}

    def _fake_send_review_request(**kwargs):
        captured.update(kwargs)
        return True

    monkeypatch.setattr(email_service, 'send_review_request', _fake_send_review_request)

    response = client.post(
        '/api/sequences/',
        headers=auth_header,
        json={
            'topic_id': seeded_data['topic_id'],
            'created_by': seeded_data['requester_id'],
            'name': 'Sequential Review Flow',
            'description': 'Regression coverage for stakeholder links',
            'initial_message': 'Please review this topic.',
            'priority': 'medium',
            'days_per_review': 5,
            'auto_start': True,
            'reviewers': [
                {'reviewer_id': seeded_data['first_reviewer_id'], 'step_name': 'Expert Review'},
                {'reviewer_id': seeded_data['second_reviewer_id'], 'step_name': 'Clarity Review'},
            ],
        },
    )

    assert response.status_code == 201, response.data
    assert captured['review_url'].startswith('/review/')
    assert '/reviews' not in captured['review_url']

    with app.app_context():
        review = Review.query.one()
        token = ReviewToken.query.filter_by(review_id=review.id).one()

        assert token.reviewer_email == seeded_data['first_reviewer_email']
        assert captured['review_url'] == f'/review/{token.token}'


def test_token_approval_auto_advances_sequence_to_next_reviewer(client, app, seeded_data, monkeypatch):
    captured = {}

    def _fake_send_review_request(**kwargs):
        captured.update(kwargs)
        return True

    monkeypatch.setattr(email_service, 'send_review_request', _fake_send_review_request)

    with app.app_context():
        from backend.models import ReviewSequence, ReviewSequenceStep

        sequence = ReviewSequence(
            topic_id=seeded_data['topic_id'],
            created_by=seeded_data['requester_id'],
            name='Auto Advance Sequence',
            status='active',
            current_position=0,
            auto_advance_on_approve=True,
            pause_on_changes=True,
        )
        db.session.add(sequence)
        db.session.flush()

        first_step = ReviewSequenceStep(
            sequence_id=sequence.id,
            step_order=0,
            reviewer_id=seeded_data['first_reviewer_id'],
            reviewer_role='reviewer',
            step_name='SME Review',
            status='active',
        )
        second_step = ReviewSequenceStep(
            sequence_id=sequence.id,
            step_order=1,
            reviewer_id=seeded_data['second_reviewer_id'],
            reviewer_role='reviewer',
            step_name='Stakeholder Review',
            status='pending',
        )
        db.session.add_all([first_step, second_step])
        db.session.flush()

        review = Review(
            topic_id=seeded_data['topic_id'],
            requested_by=seeded_data['requester_id'],
            reviewer_id=seeded_data['first_reviewer_id'],
            sequence_id=sequence.id,
            sequence_position=0,
            status='pending',
        )
        db.session.add(review)
        db.session.flush()

        first_step.review_id = review.id

        token = ReviewToken(
            token='sequence-token',
            review_id=review.id,
            reviewer_email=seeded_data['first_reviewer_email'],
            expires_at=datetime.utcnow() + timedelta(days=7),
        )
        db.session.add(token)
        db.session.commit()

    response = client.post(
        '/api/review/sequence-token/feedback',
        json={
            'recommendation': 'approve',
            'feedback': 'Looks good to me.',
            'feedback_items': [],
        },
    )

    assert response.status_code == 201, response.data
    payload = response.get_json()
    assert payload['sequence_advanced'] is True

    with app.app_context():
        from backend.models import ReviewSequence, ReviewSequenceStep, Topic

        sequence = ReviewSequence.query.one()
        topic = Topic.query.get(seeded_data['topic_id'])
        reviews = Review.query.order_by(Review.id.asc()).all()
        next_review = reviews[-1]
        current_step = ReviewSequenceStep.query.filter_by(sequence_id=sequence.id, step_order=0).one()
        next_step = ReviewSequenceStep.query.filter_by(sequence_id=sequence.id, step_order=1).one()
        next_token = ReviewToken.query.filter_by(review_id=next_review.id).one()

        assert len(reviews) == 2
        assert reviews[0].status == 'completed'
        assert next_review.reviewer_id == seeded_data['second_reviewer_id']
        assert next_review.sequence_position == 1
        assert sequence.current_position == 1
        assert sequence.status == 'active'
        assert topic.status == 'pending_review'
        assert current_step.status == 'completed'
        assert next_step.status == 'active'
        assert next_step.review_id == next_review.id
        assert captured['review_url'] == f'/review/{next_token.token}'


def test_manual_advance_uses_next_available_step_when_order_has_gap(client, app, auth_header, seeded_data, monkeypatch):
    captured = {}

    def _fake_send_review_request(**kwargs):
        captured.update(kwargs)
        return True

    monkeypatch.setattr(email_service, 'send_review_request', _fake_send_review_request)

    with app.app_context():
        from backend.models import ReviewSequence, ReviewSequenceStep

        sequence = ReviewSequence(
            topic_id=seeded_data['topic_id'],
            created_by=seeded_data['requester_id'],
            name='Sparse Order Manual Advance',
            status='active',
            current_position=0,
            auto_advance_on_approve=True,
            pause_on_changes=True,
        )
        db.session.add(sequence)
        db.session.flush()

        first_step = ReviewSequenceStep(
            sequence_id=sequence.id,
            step_order=0,
            reviewer_id=seeded_data['first_reviewer_id'],
            reviewer_role='reviewer',
            step_name='Initial Review',
            status='active',
        )
        gap_step = ReviewSequenceStep(
            sequence_id=sequence.id,
            step_order=2,
            reviewer_id=seeded_data['second_reviewer_id'],
            reviewer_role='reviewer',
            step_name='Follow-up Review',
            status='pending',
        )
        db.session.add_all([first_step, gap_step])
        db.session.flush()

        review = Review(
            topic_id=seeded_data['topic_id'],
            requested_by=seeded_data['requester_id'],
            reviewer_id=seeded_data['first_reviewer_id'],
            sequence_id=sequence.id,
            sequence_position=0,
            status='completed',
            completed_at=datetime.utcnow(),
        )
        db.session.add(review)
        db.session.flush()

        first_step.review_id = review.id
        db.session.commit()

        sequence_id = sequence.id

    response = client.post(
        f'/api/sequences/{sequence_id}/advance',
        headers=auth_header,
        json={'message': 'Advance to next available reviewer.'},
    )

    assert response.status_code == 200, response.data

    with app.app_context():
        from backend.models import ReviewSequence, ReviewSequenceStep

        sequence = ReviewSequence.query.get(sequence_id)
        gap_step = ReviewSequenceStep.query.filter_by(sequence_id=sequence_id, step_order=2).one()
        reviews = Review.query.filter_by(sequence_id=sequence_id).order_by(Review.id.asc()).all()

        assert sequence.status == 'active'
        assert sequence.current_position == 2
        assert len(reviews) == 2
        assert reviews[-1].sequence_position == 2
        assert reviews[-1].reviewer_id == seeded_data['second_reviewer_id']
        assert gap_step.status == 'active'
        assert gap_step.review_id == reviews[-1].id
        assert captured['reviewer_email'] == 'second-reviewer@example.com'
