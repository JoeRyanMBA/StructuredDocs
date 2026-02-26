import os
from datetime import datetime, timedelta

import pytest

from backend.app import create_app
from backend.models import db, Review, Stakeholder, Topic
from backend.utils.email_service import email_service


@pytest.fixture()
def app(tmp_path, monkeypatch):
    monkeypatch.setenv('ENABLE_BLUEPRINTS', 'reviews')
    monkeypatch.delenv('SKIP_BLUEPRINTS', raising=False)
    monkeypatch.setenv('DATABASE_URL', f"sqlite:///{tmp_path / 'reviews_regression.db'}")

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
def seeded_data(app):
    with app.app_context():
        requester = Stakeholder()
        requester.name = 'Author User'
        requester.email = 'author@example.com'
        requester.role = 'author'
        requester.can_review = False
        requester.active = True

        reviewer = Stakeholder()
        reviewer.name = 'Reviewer User'
        reviewer.email = 'reviewer@example.com'
        reviewer.role = 'reviewer'
        reviewer.can_review = True
        reviewer.active = True
        topic = Topic(
            title='Regression Test Topic',
            content='Sample content',
            status='draft'
        )

        db.session.add_all([requester, reviewer, topic])
        db.session.commit()

        return {
            'requester_id': requester.id,
            'requester_email': requester.email,
            'requester_name': requester.name,
            'reviewer_id': reviewer.id,
            'topic_id': topic.id,
        }


def test_request_review_resolves_requester_and_sets_email_unavailable_flag(client, app, seeded_data, monkeypatch):
    monkeypatch.setattr(email_service, 'send_review_notification', lambda **_: False)

    response = client.post(
        '/api/reviews/request',
        json={
            'topic_id': seeded_data['topic_id'],
            'reviewer_id': seeded_data['reviewer_id'],
            'requester_email': seeded_data['requester_email'],
            'requester_name': seeded_data['requester_name'],
            'message': 'Please review this topic.'
        }
    )

    assert response.status_code == 201, response.data
    payload = response.get_json()
    review_payload = payload['review']

    assert review_payload['requested_by'] == seeded_data['requester_id']
    assert review_payload['email_delivery_unavailable'] is True

    with app.app_context():
        review = Review.query.get(review_payload['id'])
        assert review is not None
        assert review.email_delivery_unavailable is True


def test_follow_up_failure_records_attempt_and_persists_unavailable_flag(client, app, seeded_data, monkeypatch):
    with app.app_context():
        review = Review(
            topic_id=seeded_data['topic_id'],
            requested_by=seeded_data['requester_id'],
            reviewer_id=seeded_data['reviewer_id'],
            status='pending',
            due_date=datetime.utcnow() + timedelta(days=5),
            email_delivery_unavailable=False
        )
        db.session.add(review)
        db.session.commit()
        review_id = review.id

    def _raise_email_error(**_):
        raise RuntimeError('SMTP unavailable')

    monkeypatch.setattr(email_service, 'send_review_reminder', _raise_email_error)

    response = client.post(f'/api/reviews/{review_id}/follow-up')
    assert response.status_code == 200, response.data

    payload = response.get_json()
    assert payload['email_sent'] is False
    assert 'SMTP unavailable' in payload.get('warning', '')
    assert payload['review']['email_delivery_unavailable'] is True

    with app.app_context():
        review = Review.query.get(review_id)
        assert review is not None
        assert review.follow_up_sent_at is not None
        assert review.email_delivery_unavailable is True


def test_follow_up_success_clears_unavailable_flag(client, app, seeded_data, monkeypatch):
    with app.app_context():
        review = Review(
            topic_id=seeded_data['topic_id'],
            requested_by=seeded_data['requester_id'],
            reviewer_id=seeded_data['reviewer_id'],
            status='pending',
            due_date=datetime.utcnow() + timedelta(days=5),
            email_delivery_unavailable=True
        )
        db.session.add(review)
        db.session.commit()
        review_id = review.id

    monkeypatch.setattr(email_service, 'send_review_reminder', lambda **_: True)

    response = client.post(f'/api/reviews/{review_id}/follow-up')
    assert response.status_code == 200, response.data

    payload = response.get_json()
    assert payload['email_sent'] is True
    assert payload['review']['email_delivery_unavailable'] is False

    with app.app_context():
        review = Review.query.get(review_id)
        assert review is not None
        assert review.follow_up_sent_at is not None
        assert review.email_delivery_unavailable is False
