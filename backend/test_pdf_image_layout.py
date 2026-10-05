import base64
import os
import sys
from types import SimpleNamespace

from flask import Flask
from PIL import Image as PILImage
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image, ImageAndFlowables, Paragraph, SimpleDocTemplate

import backend.services.pdf_generator as pdf_generator
from backend.services.pdf_generator import (
    _OverlayImageFlowable,
    _collect_overlay_paragraphs,
    _decode_pdf_layout_marker,
    convert_markdown_to_pdf_paragraphs,
)


def _image_path(tmp_path):
    path = tmp_path / 'layout-sample.png'
    PILImage.new('RGB', (120, 80), 'blue').save(path)
    return str(path)


def test_image_layout_markers_preserve_float_and_overlay_text(tmp_path):
    image_path = _image_path(tmp_path)
    cases = [
        (
            f'Before <img src="{image_path}" style="float: left" width="120" height="80"> after',
            'float',
            'left',
            'Before after',
            False,
        ),
        (
            f'<img src="{image_path}" style="position: absolute; z-index: 1" width="120" height="80"> overlay text',
            'overlay',
            'right',
            'overlay text',
            True,
        ),
        (
            f'<img src="{image_path}" style="position: absolute; z-index: -1" width="120" height="80"> overlay text',
            'overlay',
            'right',
            'overlay text',
            False,
        ),
    ]

    for content, mode, side, expected_text, image_on_top in cases:
        paragraphs = convert_markdown_to_pdf_paragraphs(content)
        marker = next(item for item in paragraphs if item.startswith('__PDF_LAYOUT_IMG__:'))
        payload = _decode_pdf_layout_marker(marker)

        assert payload['mode'] == mode
        assert payload['side'] == side
        assert payload['text'] == expected_text
        assert payload['image_on_top'] is image_on_top


def test_uppercase_single_quoted_image_attributes_are_parsed(tmp_path):
    image_path = _image_path(tmp_path)
    content = (
        f"<IMG SRC='{image_path}' STYLE='float: left' WIDTH='60' HEIGHT='40'> "
        'Text beside the image.'
    )

    paragraphs = convert_markdown_to_pdf_paragraphs(content)
    marker = next(item for item in paragraphs if item.startswith('__PDF_LAYOUT_IMG__:'))
    payload = _decode_pdf_layout_marker(marker)

    assert payload['src'] == image_path
    assert payload['mode'] == 'float'
    assert payload['side'] == 'left'
    assert payload['text'] == 'Text beside the image.'
    assert payload['width'] == 60
    assert payload['height'] == 40


def test_multiline_image_tag_is_parsed_as_one_image(tmp_path):
    image_path = _image_path(tmp_path)
    content = (
        f"<img\n src='{image_path}'\n style='float: left'\n"
        " width='60' height='40'> Text beside the image."
    )

    paragraphs = convert_markdown_to_pdf_paragraphs(content)
    marker = next(item for item in paragraphs if item.startswith('__PDF_LAYOUT_IMG__:'))
    payload = _decode_pdf_layout_marker(marker)

    assert payload['src'] == image_path
    assert payload['mode'] == 'float'
    assert payload['side'] == 'left'
    assert payload['text'] == 'Text beside the image.'
    assert payload['width'] == 60
    assert payload['height'] == 40


def test_pdf_image_flowable_prefers_css_width_over_legacy_dimensions(tmp_path):
    image_path = _image_path(tmp_path)

    for css_width, expected_width in [('25%', 100), ('50%', 200), ('75%', 300), ('180px', 135)]:
        paragraphs = convert_markdown_to_pdf_paragraphs(
            f'<img src="{image_path}" width="600" height="400" style="width:{css_width};height:auto">'
        )
        marker = next(item for item in paragraphs if item.startswith('__PDF_IMG__:'))
        _, _src, width, height = marker.split(':', 3)

        assert int(width) == expected_width
        assert int(height) == int(80 * expected_width / 120)


def test_absolute_app_image_url_resolves_from_local_storage(tmp_path, monkeypatch):
    image_path = tmp_path / 'inserted-image.png'
    PILImage.new('RGB', (120, 80), 'blue').save(image_path)
    monkeypatch.setenv('IMAGE_STORAGE_ROOT', str(tmp_path))
    monkeypatch.setattr(
        pdf_generator,
        '_download_image_for_pdf',
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError('should resolve locally')),
    )

    resolved = pdf_generator._resolve_pdf_image_source(
        'https://app.example.test/images/inserted-image.png?cache=1',
        str(tmp_path),
    )

    assert resolved == str(image_path)


def test_embedded_data_image_is_decoded_and_rendered_in_pdf(tmp_path):
    source_path = _image_path(tmp_path)
    with open(source_path, 'rb') as source_file:
        image_data = base64.b64encode(source_file.read()).decode('ascii')
    data_url = f'data:image/png;base64,{image_data}'
    paragraphs = convert_markdown_to_pdf_paragraphs(
        f'<img src="{data_url}" style="width:50%;height:auto">',
        temp_dir=str(tmp_path),
    )

    marker = next(item for item in paragraphs if item.startswith('__PDF_IMG__:'))
    _, image_path, width, height = marker.split(':', 3)
    assert int(width) == 200
    assert int(height) == 133

    output_path = tmp_path / 'embedded-image.pdf'
    SimpleDocTemplate(str(output_path), pagesize=letter).build([
        Image(image_path, width=int(width), height=int(height)),
    ])
    assert output_path.exists()
    assert os.path.getsize(output_path) > 0


def test_imported_remote_image_url_resolves_to_downloaded_file(tmp_path, monkeypatch):
    image_path = _image_path(tmp_path)
    public_url = '/images/imports/9/image3_511f306e.png'
    image_record = SimpleNamespace(
        backend_path='',
        frontend_path='https://cdn.example.com/images/imports/9/image3_511f306e.png',
        public_url=public_url,
    )
    monkeypatch.setattr(pdf_generator, '_resolve_local_image_path_for_pdf', lambda _src: '')
    monkeypatch.setattr(pdf_generator, '_get_import_image_for_pdf', lambda _src: image_record)
    monkeypatch.setattr(pdf_generator, '_download_image_for_pdf', lambda _url, _temp_dir: image_path)

    assert pdf_generator._resolve_pdf_image_source(public_url, str(tmp_path)) == image_path


def test_legacy_pandoc_image_path_resolves_by_basename(tmp_path):
    image_path = tmp_path / 'imports' / '42' / 'pdf_legacy_basename_image.png'
    image_path.parent.mkdir(parents=True)
    PILImage.new('RGB', (120, 80), 'blue').save(image_path)

    with Flask(__name__).app_context():
        resolved = pdf_generator._resolve_pdf_image_source(
            'media/pdf_legacy_basename_image.png',
            str(tmp_path),
        )

    assert resolved
    with PILImage.open(resolved) as resolved_image:
        assert resolved_image.size == (120, 80)


def test_svg_content_image_is_rasterized_for_pdf(tmp_path, monkeypatch):
    svg_path = tmp_path / 'topic-image.svg'
    svg_path.write_text('<svg xmlns="http://www.w3.org/2000/svg"></svg>')

    def fake_svg2png(url, write_to, **kwargs):
        PILImage.new('RGB', (120, 80), 'blue').save(write_to, format='PNG')

    monkeypatch.setitem(
        sys.modules,
        'cairosvg',
        SimpleNamespace(svg2png=fake_svg2png),
    )

    paragraphs = convert_markdown_to_pdf_paragraphs(
        f'<img src="{svg_path}" width="120" height="80">',
        temp_dir=str(tmp_path),
    )

    image_marker = next(item for item in paragraphs if item.startswith('__PDF_IMG__:'))
    image_path = image_marker.split(':', 3)[1]
    assert image_path.endswith('.png')
    assert os.path.exists(image_path)

    output_path = tmp_path / 'svg-content.pdf'
    SimpleDocTemplate(str(output_path), pagesize=letter).build([
        Image(image_path, width=120, height=80),
    ])
    assert output_path.exists()
    assert os.path.getsize(output_path) > 0


def test_downloaded_svg_keeps_its_format_for_pdf_rasterization(tmp_path, monkeypatch):
    response = SimpleNamespace(
        status_code=200,
        headers={'content-type': 'image/svg+xml'},
        iter_content=lambda _chunk_size: [b'<svg></svg>'],
    )
    monkeypatch.setattr(pdf_generator._http, 'get', lambda *_args, **_kwargs: response)

    downloaded_path = pdf_generator._download_image_for_pdf(
        'https://cdn.example.com/topic-image.svg', str(tmp_path)
    )

    assert downloaded_path.endswith('.svg')
    assert open(downloaded_path, 'rb').read() == b'<svg></svg>'


def test_image_layout_flowables_build_pdf(tmp_path):
    image_path = _image_path(tmp_path)
    output_path = tmp_path / 'layout.pdf'
    styles = getSampleStyleSheet()
    image = Image(image_path, width=120, height=80)

    story = [
        ImageAndFlowables(
            image,
            [Paragraph('Text on the right.', styles['BodyText'])],
            imageSide='left',
        ),
        ImageAndFlowables(
            image,
            [Paragraph('Text wraps around the image.', styles['BodyText'])],
            imageSide='right',
        ),
        _OverlayImageFlowable(
            image,
            Paragraph('Text overlays the image.', styles['BodyText']),
            120,
            80,
        ),
    ]
    SimpleDocTemplate(str(output_path), pagesize=letter).build(story)

    assert output_path.exists()
    assert os.path.getsize(output_path) > 0


def test_overlay_paragraphs_collect_until_structural_content(tmp_path):
    image_path = _image_path(tmp_path)
    content = (
        f'<img src="{image_path}" style="position: absolute; z-index: -1" width="120" height="80">'
        '\n\nFirst paragraph with **inline formatting**.\n\n'
        'Second paragraph.\n\n## Next heading\n\n- list content'
    )
    paragraphs = convert_markdown_to_pdf_paragraphs(content)
    marker_index = next(
        index for index, item in enumerate(paragraphs)
        if item.startswith('__PDF_LAYOUT_IMG__:')
    )
    payload = _decode_pdf_layout_marker(paragraphs[marker_index])

    text, next_index = _collect_overlay_paragraphs(paragraphs, marker_index + 1)

    assert payload['mode'] == 'overlay'
    assert text == 'First paragraph with <b>inline formatting</b>.<br/><br/>Second paragraph.'
    assert paragraphs[next_index].startswith('<font face="Helvetica-Bold"')
