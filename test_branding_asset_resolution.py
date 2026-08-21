from flask import Flask

from backend.services.pdf_generator import convert_image_to_base64


def test_convert_image_to_base64_resolves_uploaded_background_asset_by_filename(tmp_path, monkeypatch):
    backgrounds_dir = tmp_path / 'backgrounds'
    backgrounds_dir.mkdir()
    asset_path = backgrounds_dir / 'uploaded_logo.png'
    asset_path.write_bytes(b'fake-branding-bytes')

    monkeypatch.setenv('IMAGE_STORAGE_ROOT', str(tmp_path / 'custom-images'))
    app = Flask(__name__)
    with app.app_context():
        result = convert_image_to_base64('uploaded_logo.png')

    assert result.startswith('data:image/png;base64,')
