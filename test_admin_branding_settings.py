import io
import json

from flask_jwt_extended import create_access_token

from backend.app import create_app
from backend.models import User, SystemSetting, db
from backend.utils.settings import _cache


def test_hidden_branding_assets_are_excluded_from_listing(monkeypatch, tmp_path):
    app = create_app()
    with app.app_context():
        admin = User.query.filter_by(email='admin@example.com').first()
        assert admin is not None
        token = create_access_token(identity=str(admin.id))

        assets_dir = tmp_path / 'backgrounds'
        assets_dir.mkdir()
        (assets_dir / 'selected_logo.png').write_bytes(b'selected')
        (assets_dir / 'old_logo.png').write_bytes(b'old')
        monkeypatch.setattr('backend.routes.admin._branding_backgrounds_dir', lambda: str(assets_dir))

        db.session.query(SystemSetting).filter(SystemSetting.key.in_([
            'export_pdf_footer_logo',
            'export_html_logo',
            'export_pdf_title_logo',
            'export_pdf_cover_background',
            'export_branding_hidden_assets',
        ])).delete(synchronize_session=False)
        db.session.add(SystemSetting(key='export_pdf_footer_logo', value='selected_logo.png'))
        db.session.add(SystemSetting(key='export_branding_hidden_assets', value=json.dumps(['selected_logo.png', 'old_logo.png'])))
        db.session.commit()
        _cache.clear()

        with app.test_client() as client:
            response = client.get(
                '/api/admin/export-branding/assets',
                headers={'Authorization': f'Bearer {token}'},
            )
            assert response.status_code == 200, response.get_data(as_text=True)
            asset_names = {row['name'] for row in response.get_json()}
            assert asset_names == set()


def test_hidden_branding_assets_ignore_stale_settings_cache(monkeypatch, tmp_path):
    app = create_app()
    with app.app_context():
        admin = User.query.filter_by(email='admin@example.com').first()
        assert admin is not None
        token = create_access_token(identity=str(admin.id))

        assets_dir = tmp_path / 'backgrounds'
        assets_dir.mkdir()
        (assets_dir / 'cached_logo.png').write_bytes(b'cached')
        monkeypatch.setattr('backend.routes.admin._branding_backgrounds_dir', lambda: str(assets_dir))

        db.session.query(SystemSetting).filter_by(key='export_branding_hidden_assets').delete()
        db.session.commit()
        _cache.clear()
        from backend.utils.settings import get_setting
        assert get_setting('export_branding_hidden_assets', '[]') == '[]'

        db.session.add(SystemSetting(key='export_branding_hidden_assets', value=json.dumps(['cached_logo.png'])))
        db.session.commit()

        with app.test_client() as client:
            response = client.get(
                '/api/admin/export-branding/assets',
                headers={'Authorization': f'Bearer {token}'},
            )
            assert response.status_code == 200, response.get_data(as_text=True)
            assert {row['name'] for row in response.get_json()} == set()


def test_uploaded_branding_assets_stay_visible_when_unused(monkeypatch, tmp_path):
    app = create_app()
    with app.app_context():
        admin = User.query.filter_by(email='admin@example.com').first()
        assert admin is not None
        token = create_access_token(identity=str(admin.id))

        assets_dir = tmp_path / 'backgrounds'
        assets_dir.mkdir()
        (assets_dir / 'active_logo.png').write_bytes(b'active')
        (assets_dir / 'old_logo.png').write_bytes(b'old')
        monkeypatch.setattr('backend.routes.admin._branding_backgrounds_dir', lambda: str(assets_dir))

        for key in [
            'export_pdf_footer_logo',
            'export_html_logo',
            'export_pdf_title_logo',
            'export_pdf_cover_background',
            'export_branding_hidden_assets',
        ]:
            SystemSetting.query.filter_by(key=key).delete()
        db.session.commit()

        SystemSetting.query.filter_by(key='export_pdf_footer_logo').delete()
        SystemSetting.query.filter_by(key='export_pdf_footer_logo').delete()
        db.session.commit()

        row = SystemSetting(key='export_pdf_footer_logo', value='active_logo.png')
        db.session.add(row)
        db.session.commit()
        _cache.clear()

        with app.test_client() as client:
            response = client.get(
                '/api/admin/export-branding/assets',
                headers={'Authorization': f'Bearer {token}'},
            )
            assert response.status_code == 200, response.get_data(as_text=True)
            asset_names = {row['name'] for row in response.get_json()}
            assert asset_names == {'active_logo.png', 'old_logo.png'}


def test_hidden_branding_metadata_blocks_preview_of_existing_file(monkeypatch, tmp_path):
    app = create_app()
    with app.app_context():
        admin = User.query.filter_by(email='admin@example.com').first()
        assert admin is not None
        token = create_access_token(identity=str(admin.id))

        assets_dir = tmp_path / 'backgrounds'
        assets_dir.mkdir()
        (assets_dir / 'existing_logo.png').write_bytes(b'png-data')
        monkeypatch.setattr('backend.routes.admin._branding_backgrounds_dir', lambda: str(assets_dir))

        db.session.query(SystemSetting).filter(SystemSetting.key.in_([
            'export_pdf_footer_logo',
            'export_html_logo',
            'export_pdf_title_logo',
            'export_pdf_cover_background',
            'export_branding_hidden_assets',
        ])).delete(synchronize_session=False)
        db.session.add(SystemSetting(key='export_branding_hidden_assets', value=json.dumps(['existing_logo.png'])))
        db.session.commit()
        _cache.clear()

        with app.test_client() as client:
            response = client.get(
                '/api/admin/export-branding/assets/existing_logo.png/preview',
                headers={'Authorization': f'Bearer {token}'},
            )
            assert response.status_code == 404, response.get_data(as_text=True)


def test_delete_removes_legacy_hidden_file(monkeypatch, tmp_path):
    app = create_app()
    with app.app_context():
        admin = User.query.filter_by(email='admin@example.com').first()
        assert admin is not None
        token = create_access_token(identity=str(admin.id))

        assets_dir = tmp_path / 'backgrounds'
        assets_dir.mkdir()
        asset_path = assets_dir / 'legacy_logo.png'
        asset_path.write_bytes(b'legacy-data')
        monkeypatch.setattr('backend.routes.admin._branding_backgrounds_dir', lambda: str(assets_dir))

        db.session.query(SystemSetting).filter_by(key='export_branding_hidden_assets').delete()
        db.session.add(SystemSetting(key='export_branding_hidden_assets', value=json.dumps(['legacy_logo.png'])))
        db.session.commit()
        _cache.clear()

        with app.test_client() as client:
            response = client.delete(
                '/api/admin/export-branding/assets/legacy_logo.png',
                headers={'Authorization': f'Bearer {token}'},
            )
            assert response.status_code == 200, response.get_data(as_text=True)
            assert not asset_path.exists()


def test_upload_branding_asset_persists_selected_setting():
    app = create_app()
    with app.app_context():
        admin = User.query.filter_by(email='admin@example.com').first()
        assert admin is not None
        token = create_access_token(identity=str(admin.id))

        with app.test_client() as client:
            response = client.post(
                '/api/admin/export-branding/upload',
                data={
                    'file': (io.BytesIO(b'fakepngdata'), 'logo.png'),
                    'target_key': 'export_html_logo',
                },
                content_type='multipart/form-data',
                headers={'Authorization': f'Bearer {token}'},
            )

            assert response.status_code == 200, response.get_data(as_text=True)
            payload = response.get_json()
            filename = payload['filename']
            assert filename.endswith('.png')
            assert SystemSetting.query.filter_by(key='export_html_logo').first().value == filename

            settings_response = client.get(
                '/api/admin/settings',
                headers={'Authorization': f'Bearer {token}'},
            )
            assert settings_response.status_code == 200
            values = {item['key']: item['value'] for item in settings_response.get_json()}
            assert values['export_html_logo'] == filename
