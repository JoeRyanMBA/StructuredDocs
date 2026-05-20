from backend.services.pdf_generator import (
    _format_inline_markdown_for_pdf,
    convert_markdown_to_html,
    convert_markdown_to_pdf_paragraphs,
)


def test_convert_markdown_to_html_renders_table_markup():
    markdown = """| Column A | Column B |
| --- | --- |
| 1 | 2 |
"""

    html = convert_markdown_to_html(markdown)

    assert '<table>' in html
    assert '<thead>' in html
    assert '<tbody>' in html
    assert '<th>Column A</th>' in html
    assert '<td>1</td>' in html


def test_convert_markdown_to_pdf_paragraphs_emits_table_sentinel():
    markdown = """| A | B |
| --- | --- |
| left | right |
"""

    paragraphs = convert_markdown_to_pdf_paragraphs(markdown)

    table_entries = [p for p in paragraphs if isinstance(p, str) and p.startswith('__TABLE__:')]
    assert len(table_entries) == 1
    assert '"A"' in table_entries[0]
    assert '"left"' in table_entries[0]


def test_pdf_inline_markdown_formatter_handles_bold_and_italic():
    formatted = _format_inline_markdown_for_pdf('**Leave Type** and *Code*')

    assert '<b>Leave Type</b>' in formatted
    assert '<i>Code</i>' in formatted
