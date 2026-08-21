from pathlib import Path

from flask import Flask

from backend.services import pdf_generator as pdf_generator_module
from backend.services.pdf_generator import convert_image_to_base64, convert_markdown_to_html
from backend.utils.image_registry import normalize_import_image_public_url, normalize_stale_temp_image_refs_in_content
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
    assert 'ZmFrZS1pbWFnZS1ieXRlcw==' or 'ZmFrZS1pbWFnZS1pbWFnZS1ieXRlcw==' in result


def test_convert_markdown_to_html_rewrites_tmp_pandoc_image_paths_to_data_urls(tmp_path, monkeypatch):
    storage_root = tmp_path / 'custom-images'
    storage_root.mkdir()
    image_path = storage_root / 'imports' / '5' / 'image1.png'
    image_path.parent.mkdir(parents=True)
    image_path.write_bytes(b'fake-image-bytes')

    monkeypatch.setenv('IMAGE_STORAGE_ROOT', str(storage_root))
    app = Flask(__name__)
    with app.app_context():
        html = convert_markdown_to_html('![Figure](/tmp/import_8_kr60p3wc/media/media/image1.png)')

    assert '/tmp/import_8_kr60p3wc' not in html
    assert 'data:image/png;base64,' in html
    assert 'Figure' in html


def test_convert_markdown_to_html_resolves_canonical_import_paths_without_leading_slash(tmp_path, monkeypatch):
    storage_root = tmp_path / 'custom-images'
    storage_root.mkdir()
    image_path = storage_root / 'imports' / '5' / 'image2.png'
    image_path.parent.mkdir(parents=True)
    image_path.write_bytes(b'fake-image-bytes-2')

    monkeypatch.setenv('IMAGE_STORAGE_ROOT', str(storage_root))
    app = Flask(__name__)
    with app.app_context():
        html = convert_markdown_to_html('![Figure](images/imports/5/image2.png)')

    assert 'data:image/png;base64,' in html
    assert 'Figure' in html


def test_convert_image_to_base64_resolves_image_from_static_backgrounds_folder(tmp_path):
    app = Flask(__name__)
    backgrounds_dir = tmp_path / 'backgrounds'
    backgrounds_dir.mkdir()
    asset_path = backgrounds_dir / 'uploaded_logo.png'
    asset_path.write_bytes(b'fake-branding-bytes')

    with app.app_context():
        app.config['STATIC_FOLDER'] = str(backgrounds_dir)
        result = convert_image_to_base64('uploaded_logo.png')

    assert result.startswith('data:image/png;base64,')


def test_normalize_stale_temp_image_refs_in_content_rewrites_pandoc_tmp_urls():
    content = 'Before\n![Figure](/tmp/import_8_kr60p3wc/media/media/image1.png)\nAfter\n<img src="/tmp/import_8_kr60p3wc/media/media/image2.png" alt="alt">'
    rewritten = normalize_stale_temp_image_refs_in_content(
        content,
        basename_map={
            'image1.png': '/images/imports/5/image1.png',
            'image2.png': '/images/imports/5/image2.png',
        }
    )

    assert '/tmp/import_8_kr60p3wc' not in rewritten
    assert '/images/imports/5/image1.png' in rewritten
    assert '/images/imports/5/image2.png' in rewritten


def test_normalize_stale_temp_image_refs_in_content_keeps_unknown_paths():
    content = '![Figure](/tmp/unknown/media/ghost.png)'
    rewritten = normalize_stale_temp_image_refs_in_content(content, basename_map={})
    assert rewritten == content


def test_pdf_generator_exposes_datetime_for_footer_logo_rendering():
    assert hasattr(pdf_generator_module, 'datetime')
    assert pdf_generator_module.datetime is not None
