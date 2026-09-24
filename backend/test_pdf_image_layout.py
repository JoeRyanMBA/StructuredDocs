import os

from PIL import Image as PILImage
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image, ImageAndFlowables, Paragraph, SimpleDocTemplate

from backend.services.pdf_generator import (
    _OverlayImageFlowable,
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


def test_image_layout_flowables_build_pdf(tmp_path):
    image_path = _image_path(tmp_path)
    output_path = tmp_path / 'layout.pdf'
    styles = getSampleStyleSheet()
    image = Image(image_path, width=120, height=80)

    story = [
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
