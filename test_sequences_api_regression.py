import pytest

from flask_jwt_extended import create_access_token

from backend.app import create_app
from backend.models import Review, ReviewToken, Stakeholder, Topic, User, db
from backend.utils.email_service import email_service


@pytest.fixture()
def app(tmp_path, monkeypatch):
    monkeypatch.setenv('ENABLE_BLUEPRINTS', 'sequences')
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
