from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from flask import Flask
from flask_jwt_extended import create_access_token

from backend.extensions import db, jwt
from backend.models import Review, ReviewSequence, Stakeholder, Topic, User
from backend.routes.bulk_reviews import bulk_reviews_bp
from backend.routes.reviews import reviews_bp
from backend.routes.sequences import sequences_bp
from backend.routes.topics import topics_bp


@pytest.fixture
def review_app(monkeypatch, tmp_path):
    app = Flask(__name__)
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI=f'sqlite:///{tmp_path / "reviews.sqlite"}',
        JWT_SECRET_KEY='review-task-testing-secret-key-at-least-32-bytes',
    )
    db.init_app(app)
    jwt.init_app(app)
    for blueprint in (reviews_bp, bulk_reviews_bp, sequences_bp, topics_bp):
        app.register_blueprint(blueprint)
    monkeypatch.setattr('backend.routes.reviews.email_service.send_review_notification', lambda **kwargs: True)
    monkeypatch.setattr('backend.routes.bulk_reviews.email_service.send_bulk_review_notification', lambda **kwargs: True)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


def auth(user_id):
    return {'Authorization': f'Bearer {create_access_token(identity=str(user_id))}'}


def test_tasks_use_stakeholder_email_and_separate_sent_received_and_completed(review_app):
    db.session.add_all([
        User(id=1, name='Current User', email='person@example.com'),
        Stakeholder(id=1, name='Unrelated', email='other@example.com'),
        Stakeholder(id=7, name='Current User', email='PERSON@example.com'),
        Stakeholder(id=8, name='Reviewer', email='reviewer@example.com'),
        Topic(id=1, title='Example'),
    ])
    db.session.flush()
    db.session.add_all([
        Review(id=1, topic_id=1, requested_by=8, reviewer_id=7, status='pending'),
        Review(id=2, topic_id=1, requested_by=7, reviewer_id=8, status='in_progress'),
        Review(id=3, topic_id=1, requested_by=7, reviewer_id=8, status='completed'),
        Review(id=4, topic_id=1, requested_by=8, reviewer_id=7, status='completed'),
        Review(id=5, topic_id=1, requested_by=1, reviewer_id=8, status='pending'),
        Review(id=6, topic_id=1, requested_by=7, reviewer_id=7, status='completed'),
        Review(id=7, topic_id=1, requested_by=7, reviewer_id=8, status='declined'),
        Review(id=8, topic_id=1, requested_by=7, reviewer_id=7, status='pending'),
    ])
    db.session.commit()

    response = review_app.test_client().get('/api/reviews/tasks', headers=auth(1))

    assert response.status_code == 200
    result = response.get_json()
    assert {r['id'] for r in result['assigned']} == {1, 8}
    assert {r['id'] for r in result['sent']} == {2, 7, 8}
    assert {r['id'] for r in result['completed']} == {3, 4, 6}


def test_tasks_without_matching_stakeholder_do_not_show_other_reviews(review_app):
    db.session.add_all([
        User(id=1, name='Current User', email='person@example.com'),
        Stakeholder(id=1, name='Unrelated', email='other@example.com'),
        Topic(id=1, title='Example'),
    ])
    db.session.flush()
    db.session.add(Review(topic_id=1, requested_by=1, reviewer_id=1, status='pending'))
    db.session.commit()

    response = review_app.test_client().get('/api/reviews/tasks', headers=auth(1))

    assert response.status_code == 200
    assert response.get_json() == {'assigned': [], 'sent': [], 'completed': [], 'stakeholder_linked': False}
    assert Stakeholder.query.count() == 1


def test_ambiguous_stakeholder_email_is_reported_instead_of_guessing(review_app):
    db.session.add_all([
        User(id=1, name='Current User', email='person@example.com'),
        Stakeholder(id=1, name='First', email='person@example.com'),
        Stakeholder(id=2, name='Second', email='PERSON@example.com'),
    ])
    db.session.commit()

    response = review_app.test_client().get('/api/reviews/tasks', headers=auth(1))

    assert response.status_code == 409
    assert 'Multiple stakeholders' in response.get_json()['error']


def test_ambiguous_account_email_is_reported_instead_of_sharing_tasks(review_app):
    db.session.add_all([
        User(id=1, name='First', email='person@example.com'),
        User(id=2, name='Second', email='PERSON@example.com'),
        Stakeholder(id=1, name='Reviewer', email='person@example.com'),
    ])
    db.session.commit()

    response = review_app.test_client().get('/api/reviews/tasks', headers=auth(1))

    assert response.status_code == 409
    assert 'Multiple accounts' in response.get_json()['error']


def test_review_creation_reuses_matching_stakeholder_without_changing_permissions(review_app):
    db.session.add_all([
        User(id=1, name='Sender', email='SENDER@example.com'),
        Stakeholder(id=1, name='Reviewer', email='reviewer@example.com', can_review=True),
        Stakeholder(id=9, name='Sender', email='sender@example.com', can_review=True),
        Topic(id=1, title='Example'),
    ])
    db.session.commit()

    response = review_app.test_client().post(
        '/api/reviews/request', json={'topic_id': 1, 'reviewer_id': 1, 'requested_by': 1}, headers=auth(1)
    )

    assert response.status_code == 201
    assert Review.query.one().requested_by == 9
    assert db.session.get(Stakeholder, 9).can_review is True
    assert Stakeholder.query.count() == 2


def test_failed_review_does_not_create_sender_stakeholder(review_app):
    db.session.add_all([
        User(id=1, name='Sender', email='sender@example.com'),
        Stakeholder(id=1, name='Reviewer', email='reviewer@example.com', can_review=True),
        Topic(id=1, title='Example'),
    ])
    db.session.commit()

    response = review_app.test_client().post(
        '/api/reviews/request',
        json={'topic_id': 1, 'reviewer_id': 1, 'due_date': 'invalid'},
        headers=auth(1),
    )

    assert response.status_code >= 400
    assert Stakeholder.query.filter_by(email='sender@example.com').first() is None


def test_parallel_requests_create_only_one_sender_stakeholder(review_app):
    db.session.add_all([
        User(id=1, name='Sender', email='sender@example.com'),
        Stakeholder(id=10, name='Reviewer', email='reviewer@example.com', can_review=True),
        Topic(id=1, title='First'),
        Topic(id=2, title='Second'),
    ])
    db.session.commit()
    headers = auth(1)
    barrier = Barrier(2)

    def send(topic_id):
        barrier.wait()
        return review_app.test_client().post(
            '/api/reviews/request',
            json={'topic_id': topic_id, 'reviewer_id': 10},
            headers=headers,
        ).status_code

    with ThreadPoolExecutor(max_workers=2) as executor:
        statuses = list(executor.map(send, [1, 2]))

    assert statuses == [201, 201]
    sender = Stakeholder.query.filter_by(email='sender@example.com').one()
    assert {review.requested_by for review in Review.query.all()} == {sender.id}


def test_review_moves_from_sent_and_assigned_to_both_completed_lists(review_app):
    db.session.add_all([
        User(id=1, name='Sender', email='sender@example.com'),
        User(id=2, name='Reviewer', email='reviewer@example.com'),
        Stakeholder(id=10, name='Reviewer', email='reviewer@example.com', can_review=True),
        Topic(id=1, title='Example'),
    ])
    db.session.commit()
    client = review_app.test_client()

    created = client.post(
        '/api/reviews/request', json={'topic_id': 1, 'reviewer_id': 10}, headers=auth(1)
    )
    assert created.status_code == 201
    review_id = created.get_json()['review']['id']
    assert created.get_json()['review']['requester_name'] == 'Sender'
    assert [r['id'] for r in client.get('/api/reviews/tasks', headers=auth(1)).get_json()['sent']] == [review_id]
    assert [r['id'] for r in client.get('/api/reviews/tasks', headers=auth(2)).get_json()['assigned']] == [review_id]

    assert client.post(f'/api/reviews/{review_id}/start', headers=auth(2)).status_code == 200
    response = client.post(
        f'/api/reviews/{review_id}/submit',
        json={'recommendation': 'approve', 'feedback': 'Looks good', 'review_notes': 'Private'},
        headers=auth(2),
    )
    assert response.status_code == 200
    sender_tasks = client.get('/api/reviews/tasks', headers=auth(1)).get_json()
    reviewer_tasks = client.get('/api/reviews/tasks', headers=auth(2)).get_json()
    assert sender_tasks['sent'] == []
    assert reviewer_tasks['assigned'] == []
    assert sender_tasks['completed'][0]['id'] == review_id
    assert 'review_notes' not in sender_tasks['completed'][0]
    assert reviewer_tasks['completed'][0]['review_notes'] == 'Private'


def test_sequential_review_keeps_requester_when_advancing(review_app):
    db.session.add_all([
        User(id=1, name='Sender', email='sender@example.com'),
        User(id=2, name='First Reviewer', email='first@example.com'),
        Stakeholder(id=10, name='First Reviewer', email='first@example.com', can_review=True),
        Stakeholder(id=11, name='Second Reviewer', email='second@example.com', can_review=True),
        Topic(id=1, title='Example'),
    ])
    db.session.commit()
    client = review_app.test_client()
    created = client.post(
        '/api/sequences/',
        json={'topic_id': 1, 'reviewers': [{'reviewer_id': 10}, {'reviewer_id': 11}]},
        headers=auth(1),
    )
    assert created.status_code == 201
    first = Review.query.one()

    response = client.post(
        f'/api/reviews/{first.id}/submit', json={'recommendation': 'approve'}, headers=auth(2)
    )

    assert response.status_code == 200
    tasks = client.get('/api/reviews/tasks', headers=auth(1)).get_json()
    assert [r['reviewer_id'] for r in tasks['completed']] == [10]
    assert [r['reviewer_id'] for r in tasks['sent']] == [11]
    assert tasks['sent'][0]['requester_name'] == 'Sender'


def test_legacy_sequence_recovers_requester_from_its_existing_review(review_app):
    db.session.add_all([
        User(id=1, name='Sender', email='sender@example.com'),
        Stakeholder(id=10, name='First Reviewer', email='first@example.com', can_review=True),
        Stakeholder(id=11, name='Second Reviewer', email='second@example.com', can_review=True),
        Topic(id=1, title='Example'),
    ])
    db.session.commit()
    client = review_app.test_client()
    response = client.post(
        '/api/sequences/',
        json={'topic_id': 1, 'reviewers': [{'reviewer_id': 10}, {'reviewer_id': 11}]},
        headers=auth(1),
    )
    assert response.status_code == 201
    sequence = ReviewSequence.query.one()
    first = Review.query.one()
    sender_id = first.requested_by
    first.status = 'completed'
    sequence.created_by = 999
    db.session.commit()

    response = client.post(f'/api/sequences/{sequence.id}/advance', json={}, headers=auth(1))

    assert response.status_code == 200
    assert sequence.created_by == sender_id
    assert Review.query.filter_by(reviewer_id=11).one().requested_by == sender_id


@pytest.mark.parametrize('path,payload', [
    ('/api/reviews/request', {'topic_id': 1, 'reviewer_id': 1, 'requested_by': 1}),
    ('/api/reviews/bulk-request', {'topic_ids': [1, 2], 'reviewer_id': 1, 'requested_by': 1}),
    ('/api/sequences/', {'topic_id': 1, 'created_by': 1, 'reviewers': [{'reviewer_id': 1}]}),
    ('/api/topics/1/review', {'reviewer_id': 1, 'requested_by': 1}),
])
def test_review_creation_attributes_authenticated_user_and_creates_stakeholder(review_app, path, payload):
    db.session.add_all([
        User(id=1, name='Actual Sender', email='sender@example.com'),
        Stakeholder(id=1, name='Unrelated Reviewer', email='reviewer@example.com', can_review=True),
        Topic(id=1, title='First'),
        Topic(id=2, title='Second'),
    ])
    db.session.commit()

    response = review_app.test_client().post(path, json=payload, headers=auth(1))

    assert response.status_code == 201, response.get_json()
    sender = Stakeholder.query.filter_by(email='sender@example.com').one()
    assert sender.name == 'Actual Sender'
    assert sender.can_review is False
    assert all(review.requested_by == sender.id for review in Review.query.all())
    if path == '/api/sequences/':
        assert ReviewSequence.query.one().created_by == sender.id
