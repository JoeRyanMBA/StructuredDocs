import json
import os
import pytest
from backend.app import create_app
from backend.models import db, Project, User
from flask_jwt_extended import create_access_token

@pytest.fixture(scope='module')
def app():
    # Use an in-memory sqlite DB for speed
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    flask_app = create_app()
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with flask_app.app_context():
        db.create_all()
        # Create admin user
        admin = User(name='Admin', email='admin@example.com', role='admin')
        db.session.add(admin)
        db.session.commit()
        yield flask_app
        db.session.remove()

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def admin_token(app):
    with app.app_context():
        admin = User.query.filter_by(email='admin@example.com').first()
        return create_access_token(identity=str(admin.id))

@pytest.fixture()
def project(app):
    with app.app_context():
        p = Project(name='Test Project', description='Archive Flow')
        db.session.add(p)
        db.session.commit()
        return p

def test_archive_and_restore_project(client, admin_token, project, app):
    headers = {'Authorization': f'Bearer {admin_token}', 'Content-Type': 'application/json'}

    # Archive
    resp = client.post(f'/api/projects/{project.id}/archive', data=json.dumps({'archived': True}), headers=headers)
    assert resp.status_code == 200, resp.data
    data = resp.get_json()
    assert data['project']['archived'] is True

    # Restore
    resp2 = client.post(f'/api/projects/{project.id}/archive', data=json.dumps({'archived': False}), headers=headers)
    assert resp2.status_code == 200, resp2.data
    data2 = resp2.get_json()
    assert data2['project']['archived'] is False


def test_archive_requires_admin(client, project, app):
    # No token
    resp = client.post(f'/api/projects/{project.id}/archive', json={'archived': True})
    assert resp.status_code in (401, 422)
