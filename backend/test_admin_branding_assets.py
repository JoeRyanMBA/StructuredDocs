import io

import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from PIL import Image

from backend.extensions import db, jwt
from backend.models import SystemSetting, User
from backend.routes.admin import admin_bp
from backend.utils import settings


@pytest.fixture
def branding_client(tmp_path, monkeypatch):
    monkeypatch.setenv('EXPORT_BRANDING_ASSETS_DIR', str(tmp_path))
    monkeypatch.setattr(settings, '_cache', {})
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
        admin = User(name='Admin', email='admin@example.com', role='admin', password_hash='test-hash')
        db.session.add(admin)
        db.session.commit()
        headers = {'Authorization': f'Bearer {create_access_token(identity=str(admin.id))}'}
        yield app.test_client(), headers, tmp_path
        db.session.remove()
        db.drop_all()


@pytest.mark.parametrize(('filename', 'content'), [
    ('logo.png', b'fakepngdata'),
    ('logo.svg', b'<not-svg/>'),
    ('logo.svg', b'<svg'),
])
def test_branding_upload_rejects_invalid_images(branding_client, filename, content):
    client, headers, assets_dir = branding_client
    response = client.post('/api/admin/export-branding/upload', headers=headers, data={
        'file': (io.BytesIO(content), filename),
        'target_key': 'export_html_logo',
    })

    assert response.status_code == 400
    assert 'valid image' in response.json['error']
    assert list(assets_dir.iterdir()) == []
    assert SystemSetting.query.filter_by(key='export_html_logo').first() is None


@pytest.mark.parametrize('format', ['PNG', 'JPEG', 'GIF', 'BMP', 'WEBP', 'SVG'])
def test_branding_upload_round_trips_valid_images(branding_client, format):
    client, headers, assets_dir = branding_client
    stream = io.BytesIO()
    if format == 'SVG':
        stream.write(b'<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1"/>')
    else:
        Image.new('RGB', (2, 2), 'red').save(stream, format=format)
    content = stream.getvalue()
    stream.seek(0)

    response = client.post('/api/admin/export-branding/upload', headers=headers, data={
        'file': (stream, f'logo.{format.lower()}'),
        'target_key': 'export_html_logo',
    })

    assert response.status_code == 200
    filename = response.json['filename']
    assert (assets_dir / filename).read_bytes() == content
    assert SystemSetting.query.filter_by(key='export_html_logo').one().value == filename
    preview = client.get(response.json['url'], headers=headers)
    assert preview.status_code == 200
    assert preview.data == content
