from backend.utils.image_registry import normalize_import_image_public_url


def test_normalize_import_image_public_url_keeps_canonical_relative_path():
    assert normalize_import_image_public_url('/imports/5/image.png', document_id=5, filename='image.png') == '/images/imports/5/image.png'
    assert normalize_import_image_public_url('images/imports/5/image.png', document_id=5, filename='image.png') == '/images/imports/5/image.png'
    assert normalize_import_image_public_url('/images/imports/5/image.png', document_id=5, filename='image.png') == '/images/imports/5/image.png'


def test_normalize_import_image_public_url_preserves_remote_urls():
    url = 'https://cdn.example.com/images/imports/5/image.png'
    assert normalize_import_image_public_url(url, document_id=5, filename='image.png') == url
