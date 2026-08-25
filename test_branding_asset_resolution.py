from flask import Flask

from backend.services.pdf_generator import convert_image_to_base64
from backend.services.export_branding import resolve_brand_asset_path


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


def test_export_branding_resolves_runtime_asset_directory(tmp_path, monkeypatch):
    branding_dir = tmp_path / 'branding'
    branding_dir.mkdir()
    asset_path = branding_dir / 'runtime_logo.png'
    asset_path.write_bytes(b'runtime-branding-bytes')
    monkeypatch.setenv('EXPORT_BRANDING_ASSETS_DIR', str(branding_dir))

    assert resolve_brand_asset_path('runtime_logo.png') == str(asset_path)
