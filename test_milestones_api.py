import json
import os
from datetime import date

from backend.app import create_app
from backend.models import db


def _make_app(tmp_path):
    # Ensure only needed blueprints are loaded for speed
    os.environ.pop('SKIP_BLUEPRINTS', None)
    os.environ['ENABLE_BLUEPRINTS'] = 'projects,milestones'
    os.environ['DATABASE_URL'] = f"sqlite:///{tmp_path/'milestones.db'}"
    app = create_app()
    app.config['TESTING'] = True
    with app.app_context():
        db.create_all()
    return app


def test_milestones_crud_and_trailing_slash(tmp_path):
    app = _make_app(tmp_path)
    with app.app_context():
        client = app.test_client()

        # Create a project first
        proj_payload = {"name": "Milestone Test Project"}
        r = client.post('/api/projects/', data=json.dumps(proj_payload), content_type='application/json')
        assert r.status_code == 201, r.data
        project = r.get_json()
        project_id = project['id']

        # GET milestones with and without trailing slash
        r = client.get('/api/milestones')
        assert r.status_code == 200
        assert r.get_json() == []
        r = client.get('/api/milestones/')
        assert r.status_code == 200
        assert r.get_json() == []

        # POST without trailing slash
        m1 = {
            'project_id': project_id,
            'name': 'Kickoff',
            'date': '2025-10-01',
            'status': 'in-progress'
        }
        r = client.post('/api/milestones', data=json.dumps(m1), content_type='application/json')
        assert r.status_code == 201, r.data
        m1_resp = r.get_json()
        assert m1_resp['name'] == 'Kickoff'
        assert m1_resp['status'] == 'in-progress'
        assert m1_resp['date'] == '2025-10-01'

        # POST with trailing slash, rely on defaults (no date, no status)
        m2 = {
            'project_id': project_id,
            'name': 'Draft Complete'
        }
        r = client.post('/api/milestones/', data=json.dumps(m2), content_type='application/json')
        assert r.status_code == 201, r.data
        m2_resp = r.get_json()
        assert m2_resp['name'] == 'Draft Complete'
        assert m2_resp['status'] == 'planned'  # default
        assert m2_resp['date'] is None

        # Listing should include project_name field
        r = client.get('/api/milestones/')
        assert r.status_code == 200
        listing = r.get_json()
        assert len(listing) == 2
        for item in listing:
            assert item['project_name'] == 'Milestone Test Project'

        # Update: mark first milestone completed -> sets completion_date
        m1_id = m1_resp['id']
        r = client.put(
            f'/api/milestones/{m1_id}',
            data=json.dumps({'status': 'completed'}),
            content_type='application/json'
        )
        assert r.status_code == 200, r.data
        updated = r.get_json()
        assert updated['status'] == 'completed'
        assert updated['completion_date'] is not None
