import io

from flask_jwt_extended import create_access_token

from backend.app import create_app
from backend.models import User, SystemSetting


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
