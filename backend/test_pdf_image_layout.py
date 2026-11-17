import base64
import json
import os
import re
import sys
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from flask import Flask
from PIL import Image as PILImage
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Image, ImageAndFlowables, Paragraph, SimpleDocTemplate

import backend.services.pdf_generator as pdf_generator
from backend.services import export_branding
from backend.pdf_config import PDFConfig
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


@pytest.mark.parametrize(
    'link_markup',
    [
        '<a href="/topics/4/edit">Create a project</a>',
        '[Create a project](/topics/4/edit)',
    ],
)
def test_published_topic_links_in_numbered_lists_use_pdf_anchors(link_markup):
    tree = [
        {
            'id': 42,
            'topic_id': 4,
            'children': [{'id': 81, 'topic_id': 8, 'children': []}],
        },
    ]
    topic_anchors = pdf_generator._collect_topic_anchors(tree)

    paragraphs = convert_markdown_to_pdf_paragraphs(
        f'<ol><li>{link_markup}.</li></ol>',
        topic_anchors=topic_anchors,
    )

    assert paragraphs == [
        '__ORDERED__1__:<link href="#node_42">Create a project</link>.'
    ]


def test_default_pdf_palette_uses_neutral_heading_colors():
    heading_keys = ('h1_color', 'h2_color', 'h3_color', 'h4_color', 'h5_color')

    for key in heading_keys:
        heading_color = PDFConfig.COLORS[key]
        assert heading_color.red == heading_color.green == heading_color.blue


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


def test_image_inside_markdown_list_is_parsed(tmp_path):
    image_path = _image_path(tmp_path)
    content = f"- Text before <img src='{image_path}' style='float: left'> text after"

    paragraphs = convert_markdown_to_pdf_paragraphs(content)

    assert any(item.startswith('__PDF_LAYOUT_IMG__:') for item in paragraphs)


def test_layout_image_marker_survives_long_trailing_text(tmp_path):
    trailing_text = 'x' * 285
    for extra_path_length in range(3):
        image_path = tmp_path / (
            f'layout-{extra_path_length}' + ('x' * extra_path_length) + '.png'
        )
        PILImage.new('RGB', (120, 80), 'blue').save(image_path)
        content = (
            f'<img src="{image_path}" style="width:25%;height:auto;float:left">'
            f'{trailing_text}'
        )

        paragraphs = convert_markdown_to_pdf_paragraphs(content)
        marker = next(
            item for item in paragraphs if item.startswith('__PDF_LAYOUT_IMG__:')
        )
        payload = _decode_pdf_layout_marker(marker)

        assert payload['mode'] == 'float'
        assert payload['text'] == trailing_text


def test_watermark_text_is_top_aligned_over_image():
    image = Mock()
    paragraph = Mock()
    paragraph.wrap.return_value = (84, 30)
    flowable = _OverlayImageFlowable(image, paragraph, 100, 200, padding=8)
    flowable.wrap(100, 200)
    canvas = object()
    flowable.canv = canvas

    flowable.draw()

    paragraph.drawOn.assert_called_once_with(canvas, 8, 162)


def test_wrapped_editor_image_respects_saved_size_option(tmp_path):
    image_path = tmp_path / 'large-layout-image.png'
    PILImage.new('RGB', (1200, 800), 'blue').save(image_path)

    cases = [
        ('original', 180),
        ('25%', 100),
        ('50%', 200),
        ('75%', 300),
    ]
    for size, expected_width in cases:
        paragraphs = convert_markdown_to_pdf_paragraphs(
            f'<img src="{image_path}" data-sd-image-size="{size}" style="float:left">'
        )
        marker = next(item for item in paragraphs if item.startswith('__PDF_LAYOUT_IMG__:'))
        payload = _decode_pdf_layout_marker(marker)

        assert payload['width'] == expected_width
        assert payload['height'] == int(800 * expected_width / 1200)


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


def test_canonical_import_image_with_word_dimensions_is_embedded_in_pdf(tmp_path, monkeypatch):
    storage_root = tmp_path / 'images'
    image_path = storage_root / 'imports' / '12' / 'image1_7e7394d5.png'
    image_path.parent.mkdir(parents=True)
    PILImage.new('RGB', (512, 512), 'blue').save(image_path)
    monkeypatch.setenv('IMAGE_STORAGE_ROOT', str(storage_root))

    with Flask(__name__).app_context():
        paragraphs = convert_markdown_to_pdf_paragraphs(
            '<img src="/images/imports/12/image1_7e7394d5.png" '
            'style="width:2.08333in;height:2.08333in">',
            temp_dir=str(tmp_path),
        )

    marker = next(item for item in paragraphs if item.startswith('__PDF_IMG__:'))
    _, resolved_path, width, height = marker.split(':', 3)
    assert resolved_path == str(image_path)
    assert int(width) == 149
    assert int(height) == 149

    output_path = tmp_path / 'canonical-import-image.pdf'
    SimpleDocTemplate(str(output_path), pagesize=letter).build([
        Image(resolved_path, width=int(width), height=int(height)),
    ])

    assert b'/Subtype /Image' in output_path.read_bytes()


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


def test_imported_image_resolves_through_configured_storage_backend(tmp_path, monkeypatch):
    image_bytes = base64.b64decode(
        'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+j'
        'mZkAAAAASUVORK5CYII='
    )
    image_record = SimpleNamespace(
        backend_path='images/imports/12/image1_7e7394d5.png',
        frontend_path='',
        public_url='/images/imports/12/image1_7e7394d5.png',
        filename='image1_7e7394d5.png',
        mime_type='image/png',
    )
    storage = SimpleNamespace(read_file=lambda path: image_bytes)
    monkeypatch.setattr(pdf_generator, '_resolve_local_image_path_for_pdf', lambda _src: '')
    monkeypatch.setattr(pdf_generator, '_get_import_image_for_pdf', lambda _src: image_record)
    monkeypatch.setattr('backend.utils.storage.get_storage_backend', lambda: storage)

    resolved = pdf_generator._resolve_pdf_image_source(
        image_record.public_url, str(tmp_path)
    )

    assert resolved.endswith('.png')
    with PILImage.open(resolved) as image:
        assert image.size == (1, 1)


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


@pytest.mark.parametrize('image_size', [(612, 792), (100, 100), (100, 200)])
def test_pdf_cover_image_fills_page_without_distortion(tmp_path, image_size):
    image_path = tmp_path / 'cover.png'
    PILImage.new('RGB', image_size, 'blue').save(image_path)
    output = BytesIO()
    doc = pdf_generator.BackgroundImageDocTemplate(
        output, background_image_path=str(image_path), pagesize=letter,
    )
    canvas = Canvas(output, pagesize=letter)

    doc.add_title_page_with_footer(canvas, doc)

    image_transform = re.search(r'^(.+) cm\n/FormXob\.\S+ Do$', canvas.getCurrentPageContent(), re.M)
    assert image_transform is not None
    width, _, _, height, x, y = map(float, image_transform[1].split())
    page_width, page_height = letter
    assert width >= page_width
    assert height >= page_height
    assert min(width / page_width, height / page_height) == pytest.approx(1)
    assert width / height == pytest.approx(image_size[0] / image_size[1])
    assert 2 * x + width == pytest.approx(page_width)
    assert 2 * y + height == pytest.approx(page_height)


@pytest.mark.parametrize('template_class, footer_y', [
    (pdf_generator.HeaderDocTemplate, 73.355932),
    (pdf_generator.BackgroundImageDocTemplate, 67.355932),
])
@pytest.mark.parametrize('placement, expected_x', [
    (None, 18),
    ('top-left', 18),
    ('top-center', 234),
    ('top-right', 450),
    ('bottom-center', 234),
    ('bottom-right', 450),
])
def test_pdf_cover_logo_placement(tmp_path, monkeypatch, template_class, footer_y, placement, expected_x):
    logo = tmp_path / 'cover-logo.png'
    PILImage.new('RGB', (177, 100), 'blue').save(logo)
    settings = {'export_pdf_title_logo': str(logo)}
    if placement is not None:
        settings['export_branding_templates'] = json.dumps([
            {'name': 'Cover', 'settings': {'export_pdf_cover_logo_placement': placement}},
        ])
    monkeypatch.setattr(export_branding, 'get_setting', lambda key, default: settings.get(key, default))
    branding = export_branding.get_export_branding_settings('Cover' if placement else '')
    output = BytesIO()
    doc = template_class(
        output, publication=SimpleNamespace(id=1, form_number='1'), branding=branding, pagesize=letter,
    )
    canvas = Canvas(output, pagesize=letter)
    doc.add_title_page_with_footer(canvas, doc)

    page = canvas.getCurrentPageContent()
    transform = re.search(r'^(.+) cm\n/FormXob\.\S+ Do$', page, re.M)
    assert transform is not None
    width, _, _, height, x, y = map(float, transform[1].split())
    assert width == pytest.approx(144)
    assert x == pytest.approx(expected_x)
    footer = re.search(r'([\d.]+) Tm \(Form: 1\)', page)
    assert footer is not None
    assert float(footer[1]) == pytest.approx(footer_y, abs=0.001)
    if placement and placement.startswith('top-'):
        assert y + height == pytest.approx(letter[1] - 18, abs=0.001)
    elif placement:
        assert y >= footer_y + 9
        assert y + height < letter[1] / 2
    else:
        assert y == pytest.approx(18)


@pytest.mark.parametrize(
    'default_alignment, default_color, template, with_background, centered, expected_colors',
    [
        (None, None, None, False, False, ('#222222', '#4a4a4a')),
        ('center', '005a9c', None, False, True, ('#005a9c', '#005a9c')),
        ('right', '#ffffff', {
            'export_pdf_cover_text_alignment': 'center',
            'export_pdf_cover_text_color': '#112e51',
        }, True, True, ('#112e51', '#112e51')),
        ('center', '#005a9c', {}, True, False, ('#ffffff', '#ffffff')),
    ],
)
def test_pdf_cover_text_style(
    tmp_path, monkeypatch, default_alignment, default_color, template, with_background, centered, expected_colors,
):
    settings = {'export_pdf_cover_background': '__none__'}
    if with_background:
        settings['export_pdf_cover_background'] = _image_path(tmp_path)
    if default_alignment:
        settings['export_pdf_cover_text_alignment'] = default_alignment
    if default_color is not None:
        settings['export_pdf_cover_text_color'] = default_color
    if template is not None:
        settings['export_branding_templates'] = json.dumps([{'name': 'Test', 'settings': template}])
    monkeypatch.setattr(export_branding, 'get_setting', lambda key, default: settings.get(key, default))
    title, subtitle = 'Cover test title', 'Cover test subtitle'
    publication = SimpleNamespace(
        id=1, title=title, description=subtitle, form_number='1',
        branding_template_name='Test' if template is not None else '',
    )
    tree = [{'id': 1, 'title': 'Topic', 'content': 'Body text', 'children': []}]
    text_edges = {}
    text_colors = {}
    draw_on = Paragraph.drawOn

    def record_cover_text(paragraph, canvas, x, y, _sW=0):
        before = len(canvas.getCurrentPageContent())
        draw_on(paragraph, canvas, x, y, _sW)
        if canvas.getPageNumber() == 1 and paragraph.text in (title, subtitle):
            emitted = canvas.getCurrentPageContent()[before:]
            offset = re.search(r'([\d.]+) 0 Td \(', emitted)
            assert offset is not None
            left = x + float(offset[1])
            style = paragraph.style
            width = canvas.stringWidth(paragraph.text, style.fontName, style.fontSize)
            text_edges[paragraph.text] = (left, left + width)
            fill = re.search(r'^([\d.]+ [\d.]+ [\d.]+) rg$', emitted, re.M)
            assert fill is not None
            text_colors[paragraph.text] = tuple(map(float, fill[1].split()))

    monkeypatch.setattr(Paragraph, 'drawOn', record_cover_text)
    with Flask(__name__).app_context():
        pdf = pdf_generator.generate_pdf(publication, tree)

    assert pdf.getvalue().startswith(b'%PDF')
    assert set(text_edges) == {title, subtitle}
    for text, expected_color in zip((title, subtitle), expected_colors):
        rgb = tuple(int(expected_color[i:i + 2], 16) / 255 for i in (1, 3, 5))
        assert text_colors[text] == pytest.approx(rgb, abs=1e-6)
    for left, right in text_edges.values():
        if centered:
            assert (left + right) / 2 == pytest.approx(letter[0] / 2, abs=0.01)
        else:
            assert right == pytest.approx(570, abs=0.01)


@pytest.mark.parametrize('style', ['', 'float: left', 'position: absolute'])
@pytest.mark.parametrize('config_type', ['default', 'corporate', 'academic', 'compact', 'organization'])
def test_pdf_export_fits_tall_images_on_a_page(tmp_path, monkeypatch, style, config_type):
    image_path = tmp_path / 'tall.png'
    PILImage.new('RGB', (254, 4312), 'blue').save(image_path)
    small_image_path = _image_path(tmp_path)
    images = []

    def record_image(*args, **kwargs):
        image = Image(*args, **kwargs)
        images.append(image)
        return image

    monkeypatch.setattr(pdf_generator, 'Image', record_image)
    monkeypatch.setattr(
        pdf_generator,
        'get_export_branding_settings',
        lambda: {'pdf_cover_background': '__none__'},
    )
    publication = SimpleNamespace(id=1, title='Guide', description='', form_number='1')
    tree = [{
        'id': 1,
        'title': 'Topic',
        'content': (
            f'<img src="{image_path}" style="{style}"> Image text\n\n'
            f'<img src="{small_image_path}">'
        ),
        'children': [],
    }]

    with Flask(__name__).app_context():
        pdf = pdf_generator.generate_pdf(publication, tree, config_type)

    assert pdf.getvalue().startswith(b'%PDF')
    assert b'/Subtype /Image' in pdf.getvalue()
    tall_images = [image for image in images if image.filename == str(image_path)]
    small_images = [image for image in images if image.filename == small_image_path]
    assert tall_images and small_images
    for image in tall_images:
        assert 0 < image.drawHeight < 4312
        assert image.drawWidth / image.drawHeight == pytest.approx(254 / 4312)
    assert all((image.drawWidth, image.drawHeight) == (120, 80) for image in small_images)


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
