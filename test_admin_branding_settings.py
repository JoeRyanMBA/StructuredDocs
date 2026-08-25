import io
import json

from flask_jwt_extended import create_access_token

from backend.app import create_app
from backend.models import User, SystemSetting, db
from backend.utils.settings import _cache


def test_branding_assets_use_configured_runtime_directory(monkeypatch, tmp_path):
    runtime_dir = tmp_path / 'branding'
    runtime_dir.mkdir()
    monkeypatch.setenv('EXPORT_BRANDING_ASSETS_DIR', str(runtime_dir))

    from backend.routes.admin import _branding_backgrounds_dir

    assert _branding_backgrounds_dir() == str(runtime_dir)


def test_existing_branding_assets_are_listed_regardless_of_legacy_metadata(monkeypatch, tmp_path):
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
            assert asset_names == {'selected_logo.png', 'old_logo.png'}


def test_legacy_hidden_metadata_does_not_hide_existing_asset(monkeypatch, tmp_path):
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
            assert {row['name'] for row in response.get_json()} == {'cached_logo.png'}


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


def test_hidden_branding_metadata_does_not_block_preview_of_existing_file(monkeypatch, tmp_path):
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
            assert response.status_code == 200, response.get_data(as_text=True)
            assert response.data == b'png-data'


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


def test_delete_does_not_persist_oversized_hidden_asset_list(monkeypatch, tmp_path):
    app = create_app()
    with app.app_context():
        admin = User.query.filter_by(email='admin@example.com').first()
        assert admin is not None
        token = create_access_token(identity=str(admin.id))

        assets_dir = tmp_path / 'backgrounds'
        assets_dir.mkdir()
        asset_path = assets_dir / 'delete_me.png'
        asset_path.write_bytes(b'delete-me')
        monkeypatch.setattr('backend.routes.admin._branding_backgrounds_dir', lambda: str(assets_dir))

        hidden_names = [f'branding_{index:04d}_logo.png' for index in range(100)]
        SystemSetting.query.filter_by(key='export_branding_hidden_assets').delete()
        db.session.add(SystemSetting(key='export_branding_hidden_assets', value=json.dumps(hidden_names)))
        db.session.commit()
        _cache.clear()

        with app.test_client() as client:
            response = client.delete(
                '/api/admin/export-branding/assets/delete_me.png',
                headers={'Authorization': f'Bearer {token}'},
            )
            assert response.status_code == 200, response.get_data(as_text=True)
            assert not asset_path.exists()


def test_branding_preview_is_exempt_from_global_rate_limit(monkeypatch, tmp_path):
    app = create_app()
    with app.app_context():
        admin = User.query.filter_by(email='admin@example.com').first()
        assert admin is not None
        token = create_access_token(identity=str(admin.id))

        assets_dir = tmp_path / 'backgrounds'
        assets_dir.mkdir()
        (assets_dir / 'preview_logo.png').write_bytes(b'preview-data')
        monkeypatch.setattr('backend.routes.admin._branding_backgrounds_dir', lambda: str(assets_dir))

        with app.test_client() as client:
            for _ in range(55):
                response = client.get(
                    '/api/admin/export-branding/assets/preview_logo.png/preview',
                    headers={'Authorization': f'Bearer {token}'},
                )
                assert response.status_code == 200, response.get_data(as_text=True)


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
