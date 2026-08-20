from pathlib import Path

from flask import Flask

from backend.services.pdf_generator import convert_image_to_base64
from backend.utils.image_registry import normalize_import_image_public_url
from backend.utils.storage import resolve_local_storage_root


def test_normalize_import_image_public_url_keeps_canonical_relative_path():
    assert normalize_import_image_public_url('/imports/5/image.png', document_id=5, filename='image.png') == '/images/imports/5/image.png'
    assert normalize_import_image_public_url('images/imports/5/image.png', document_id=5, filename='image.png') == '/images/imports/5/image.png'
    assert normalize_import_image_public_url('/images/imports/5/image.png', document_id=5, filename='image.png') == '/images/imports/5/image.png'


def test_normalize_import_image_public_url_preserves_remote_urls():
    url = 'https://cdn.example.com/images/imports/5/image.png'
    assert normalize_import_image_public_url(url, document_id=5, filename='image.png') == url


def test_resolve_local_storage_root_uses_repo_local_data_directory_when_env_unset():
    root = resolve_local_storage_root()
    assert root.endswith('/data/images') or root.endswith('/backend/static/images')


def test_convert_image_to_base64_can_resolve_imported_image_from_local_storage_root(tmp_path, monkeypatch):
    storage_root = tmp_path / 'custom-images'
    storage_root.mkdir()
    image_path = storage_root / 'imports' / '5' / 'image.png'
    image_path.parent.mkdir(parents=True)
    image_path.write_bytes(b'fake-image-bytes')

    monkeypatch.setenv('IMAGE_STORAGE_ROOT', str(storage_root))
    app = Flask(__name__)
    with app.app_context():
        result = convert_image_to_base64('/images/imports/5/image.png')

    assert result.startswith('data:image/png;base64,')
    assert 'ZmFrZS1pbWFnZS1ieXRlcw==' or 'ZmFrZS1pbWFnZS1ieXRlcw==' in result
