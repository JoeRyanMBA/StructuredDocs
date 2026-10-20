import pytest
from flask import Flask
from flask_jwt_extended import create_access_token

from backend.extensions import db, jwt
from backend.models import Collection, Project, Topic, User
from backend.routes.admin import admin_bp


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI='sqlite://',
        JWT_SECRET_KEY='test-secret-test-secret-test-secret',
    )
    db.init_app(app)
    jwt.init_app(app)
    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


def _create_user(email, role):
    user = User(name=email, email=email, role=role, password_hash='test-hash')
    db.session.add(user)
    db.session.flush()
    return user


def _auth_header(user_id):
    token = create_access_token(identity=str(user_id))
    return {'Authorization': f'Bearer {token}'}


def test_clear_database_preserves_configured_admin(app):
    with app.app_context():
        preserved_admin = _create_user('joe@joe-ryan.mba', 'admin')
        _create_user('admin@example.com', 'admin')
        _create_user('author@example.com', 'author')
        db.session.add_all([
            Project(id=23, name='Old project'),
            Collection(id=42, name='Old collection', form_number='OLD'),
            Topic(id=57, title='Old topic'),
        ])
        db.session.commit()
        headers = _auth_header(preserved_admin.id)

    response = app.test_client().post('/api/admin/clear-database', headers=headers)

    assert response.status_code == 200
    with app.app_context():
        users = User.query.all()
        assert [(user.email, user.role) for user in users] == [('joe@joe-ryan.mba', 'admin')]

        new_project = Project(name='New project')
        new_collection = Collection(name='New collection', form_number='NEW')
        new_topic = Topic(title='New topic')
        db.session.add_all([new_project, new_collection, new_topic])
        db.session.flush()
        assert (new_project.id, new_collection.id, new_topic.id) == (1, 1, 1)


def test_clear_database_rejects_non_admin_without_deleting_users(app):
    with app.app_context():
        _create_user('joe@joe-ryan.mba', 'admin')
        author = _create_user('author@example.com', 'author')
        db.session.commit()
        headers = _auth_header(author.id)

    response = app.test_client().post('/api/admin/clear-database', headers=headers)

    assert response.status_code == 403
    with app.app_context():
        assert User.query.count() == 2


def test_clear_database_requires_configured_admin_account(app):
    with app.app_context():
        another_admin = _create_user('another-admin@example.com', 'admin')
        _create_user('author@example.com', 'author')
        db.session.commit()
        headers = _auth_header(another_admin.id)

    response = app.test_client().post('/api/admin/clear-database', headers=headers)

    assert response.status_code == 409
    with app.app_context():
        assert User.query.count() == 2
