import os
import sys
import types
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


def test_export_branding_falls_back_to_default_logos_when_settings_are_blank_or_invalid(monkeypatch):
    settings = {
        'export_brand_name': 'Acme Docs',
        'export_pdf_title_logo': '',
        'export_pdf_footer_logo': 'missing_footer_logo.png',
        'export_pdf_cover_background': 'missing_cover.png',
        'export_html_logo': '',
        'export_html_primary_color': '#005a9c',
        'export_html_accent_color': '#112E51',
    }

    monkeypatch.setattr('backend.services.export_branding.get_setting', lambda key, default=None: settings.get(key, default or ''))

    branding = pdf_generator_module.get_export_branding_settings()

    assert branding['brand_name'] == 'Acme Docs'
    assert branding['pdf_title_logo'] == 'Title_Page_Logo.png'
    assert branding['pdf_footer_logo'] == 'Footer_Logo.png'
    assert branding['pdf_cover_background'] == 'SC Cover Background.png'


def test_export_branding_preserves_no_cover_background_sentinel(monkeypatch):
    settings = {
        'export_brand_name': 'Acme Docs',
        'export_pdf_title_logo': 'Example_Logo.svg',
        'export_pdf_footer_logo': 'Footer_Logo.svg',
        'export_pdf_cover_background': '__none__',
        'export_html_logo': '',
        'export_html_primary_color': '#005a9c',
        'export_html_accent_color': '#112E51',
    }

    monkeypatch.setattr('backend.services.export_branding.get_setting', lambda key, default=None: settings.get(key, default or ''))

    branding = pdf_generator_module.get_export_branding_settings()

    assert branding['pdf_title_logo'] == 'Example_Logo.svg'
    assert branding['pdf_footer_logo'] == 'Footer_Logo.svg'
    assert branding['pdf_cover_background'] == '__none__'


def test_pdf_uses_png_when_svg_logo_is_uploaded(tmp_path, monkeypatch):
    svg_path = tmp_path / 'brand_logo.svg'
    svg_path.write_text('<svg xmlns="http://www.w3.org/2000/svg"></svg>')

    def fake_svg2png(url, write_to, **kwargs):
        with open(write_to, 'wb') as fh:
            fh.write(b'fake-png-bytes')

    monkeypatch.setitem(
        sys.modules,
        'cairosvg',
        types.SimpleNamespace(svg2png=fake_svg2png),
    )

    resolved = pdf_generator_module._resolve_pdf_renderable_image_path(str(svg_path))

    assert resolved.endswith('.png')
    assert os.path.exists(resolved)
    assert resolved != str(svg_path)


def test_pdf_uses_cli_svg_converter_when_cairosvg_is_missing(tmp_path, monkeypatch):
    svg_path = tmp_path / 'brand_logo.svg'
    svg_path.write_text('<svg xmlns="http://www.w3.org/2000/svg"></svg>')

    real_import = __import__

    def fake_import(name, *args, **kwargs):
        if name == 'cairosvg':
            raise ModuleNotFoundError('No module named cairosvg')
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr('builtins.__import__', fake_import)

    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        out_path = cmd[-1]
        if out_path.endswith('.png'):
            Path(out_path).write_bytes(b'cli-png-bytes')
        return types.SimpleNamespace(returncode=0, stdout='', stderr='')

    monkeypatch.setattr(pdf_generator_module.subprocess, 'run', fake_run)
    monkeypatch.setattr(pdf_generator_module.shutil, 'which', lambda executable: '/usr/bin/' + executable if executable in {'rsvg-convert', 'convert', 'magick'} else None)

    resolved = pdf_generator_module._resolve_pdf_renderable_image_path(str(svg_path))

    assert resolved.endswith('.png')
    assert os.path.exists(resolved)
    assert calls


def test_pdf_title_and_footer_templates_use_svg_rasterization(monkeypatch):
    calls = []

    def fake_rasterize(path):
        calls.append(path)
        return '/tmp/converted-brand-logo.png'

    def fake_resolve(value, fallback=''):
        return '/tmp/original-brand-logo.svg' if value else fallback

    monkeypatch.setattr(pdf_generator_module, '_resolve_pdf_renderable_image_path', fake_rasterize)
    monkeypatch.setattr(pdf_generator_module, 'resolve_brand_asset_path', fake_resolve)
    monkeypatch.setattr(pdf_generator_module.os.path, 'exists', lambda *_args, **_kwargs: True)

    class DummyCanvas:
        def saveState(self):
            pass

        def restoreState(self):
            pass

        def setFont(self, *args, **kwargs):
            pass

        def drawImage(self, path, *args, **kwargs):
            calls.append(path)

        def drawCentredString(self, *args, **kwargs):
            pass

        def drawString(self, *args, **kwargs):
            pass

        def stringWidth(self, *args, **kwargs):
            return 10

        def line(self, *args, **kwargs):
            pass

    template = pdf_generator_module.HeaderDocTemplate.__new__(pdf_generator_module.HeaderDocTemplate)
    template.branding = {'pdf_title_logo': 'brand.svg', 'pdf_footer_logo': 'brand.svg', 'brand_name': 'Acme'}
    template.publication = types.SimpleNamespace(form_number='FORM-1', id=1)
    template.pagesize = (612, 792)
    template.leftMargin = 36
    template.rightMargin = 36
    template.bottomMargin = 36
    template.width = 540
    template.height = 720

    template.add_title_footer(DummyCanvas(), object())
    template.add_content_footer(DummyCanvas(), types.SimpleNamespace(page=1))

    assert calls.count('/tmp/converted-brand-logo.png') >= 1
    assert any(path == '/tmp/converted-brand-logo.png' for path in calls)
