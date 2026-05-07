from io import BytesIO

from docx import Document

from backend.routes.import_handler import _convert_docx_to_markdown_fallback


def _build_docx_bytes():
    doc = Document()
    doc.add_heading('Main Topic', level=1)
    doc.add_paragraph('Intro paragraph')
    doc.add_paragraph('List bullet', style='List Bullet')
    doc.add_paragraph('Nested bullet', style='List Bullet 2')
    doc.add_paragraph('List bullet 2', style='List Bullet')
    doc.add_paragraph('List number', style='List Number')
    doc.add_paragraph('Nested number', style='List Number 2')
    doc.add_paragraph('List number 2', style='List Number')

    buffer = BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


def test_docx_fallback_preserves_word_list_markers():
    markdown = _convert_docx_to_markdown_fallback(_build_docx_bytes())

    assert '# Main Topic' in markdown
    assert 'Intro paragraph' in markdown
    assert '- List bullet' in markdown
    assert '    - Nested bullet' in markdown
    assert '- List bullet 2' in markdown
    assert '1. List number' in markdown
    assert '    1. Nested number' in markdown
    assert '2. List number 2' in markdown
