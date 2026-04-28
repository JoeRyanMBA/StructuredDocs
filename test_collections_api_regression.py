import pytest

from flask_jwt_extended import create_access_token

from backend.app import create_app
from backend.models import Collection, Topic, User, collection_topic_tree, db


@pytest.fixture()
def app(tmp_path, monkeypatch):
    monkeypatch.setenv('ENABLE_BLUEPRINTS', 'collections')
    monkeypatch.delenv('SKIP_BLUEPRINTS', raising=False)
    monkeypatch.setenv('DATABASE_URL', f"sqlite:///{tmp_path / 'collections_regression.db'}")

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
        user = User(name='Collections User', email='collections@example.com', role='author')
        db.session.add(user)
        db.session.commit()
        token = create_access_token(identity=str(user.id))

    return {'Authorization': f'Bearer {token}'}


@pytest.fixture()
def seeded_collection(app):
    with app.app_context():
        collection = Collection(
            name='Collection Stats',
            form_number='COL-001',
            description='Regression fixture',
            position=0,
        )
        topic = Topic(
            title='Stats Topic',
            content='Fixture topic',
            status='draft',
        )

        db.session.add_all([collection, topic])
        db.session.commit()

        db.session.execute(
            collection_topic_tree.insert().values(
                collection_id=collection.id,
                topic_id=topic.id,
                position=0,
                parent_topic_id=None,
            )
        )
        db.session.commit()

        return collection.id


def test_collections_stats_endpoint_returns_json(client, auth_header, seeded_collection):
    response = client.get('/api/collections/stats', headers=auth_header)

    assert response.status_code == 200, response.data
    assert response.mimetype == 'application/json'

    payload = response.get_json()
    assert payload == {
        'total': 1,
        'active': 1,
        'totalTopics': 1,
        'newThisWeek': 1,
        'avgTopics': 1,
        'rootCollections': 1,
    }


def test_missing_api_route_returns_json_404(client):
    response = client.get('/api/collections/does-not-exist')

    assert response.status_code == 404
    assert response.mimetype == 'application/json'
    assert response.get_json() == {'error': 'API endpoint not found'}
