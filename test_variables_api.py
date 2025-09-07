import json
from backend.app import create_app
from backend.models import db


def test_variable_crud_basic(tmp_path):
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{tmp_path/'vars.db'}"
    with app.app_context():
        db.create_all()
        client = app.test_client()
        r = client.get('/api/variables')
        assert r.status_code == 200
        assert r.get_json() == []
        payload = { 'name':'Company', 'slug':'company', 'description':'Test', 'scope':'global' }
        r = client.post('/api/variables', data=json.dumps(payload), content_type='application/json')
        assert r.status_code == 201, r.data
        data = r.get_json()
        assert data['slug'] == 'company'
        var_id = data['id']
        r = client.post(f'/api/variables/{var_id}/values', data=json.dumps({'value':'ACME','is_default': True}), content_type='application/json')
        assert r.status_code == 201
        r = client.get('/api/variables?include_values=1')
        listing = r.get_json()
        assert len(listing) == 1
        assert listing[0]['values'][0]['value'] == 'ACME'