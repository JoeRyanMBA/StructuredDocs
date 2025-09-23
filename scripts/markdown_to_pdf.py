#!/usr/bin/env python3
"""
Minimal Markdown→PDF converter for headings, paragraphs, lists, and horizontal rules.
Uses ReportLab (already in requirements.txt) to render simple structured docs.

Limitations:
- This is intentionally lightweight; it supports a useful subset of Markdown:
  - #, ##, ### headings
  - paragraphs
  - unordered lists (-, *) and ordered lists (1.)
  - --- as horizontal rule
  - bold/italic are not fully parsed; raw asterisks will render as-is

Usage:
  python scripts/markdown_to_pdf.py INPUT.md OUTPUT.pdf
"""
import sys
from pathlib import Path
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem, HRFlowable
from reportlab.lib.units import inch


def parse_markdown_lines(lines):
    blocks = []  # each block is {type: 'heading'|'para'|'ul'|'ol'|'hr', ...}
    current_list = None  # {'type': 'ul'|'ol', 'items': []}

    def flush_list():
        nonlocal current_list
        if current_list and current_list['items']:
            blocks.append(current_list)
        current_list = None

    for raw in lines:
        line = raw.rstrip('\n')
        stripped = line.strip()
        if not stripped:
            flush_list()
            continue

        # Horizontal rule
        if stripped == '---':
            flush_list()
            blocks.append({'type': 'hr'})
            continue

        # Headings (#, ##, ###)
        if stripped.startswith('#'):
            flush_list()
            hashes = len(stripped) - len(stripped.lstrip('#'))
            text = stripped.lstrip('#').strip()
            level = min(hashes, 3)
            blocks.append({'type': 'heading', 'level': level, 'text': text})
            continue

        # Ordered list item: e.g., "1. item" (simple detection)
        if any(stripped.startswith(f"{n}. ") for n in range(1, 10)):
            if not current_list or current_list['type'] != 'ol':
                flush_list()
                current_list = {'type': 'ol', 'items': []}
            # remove leading digits and dot
            text = stripped.split('. ', 1)[1]
            current_list['items'].append(text)
            continue

        # Unordered list item: -, *
        if stripped.startswith('- ') or stripped.startswith('* '):
            if not current_list or current_list['type'] != 'ul':
                flush_list()
                current_list = {'type': 'ul', 'items': []}
            text = stripped[2:]
            current_list['items'].append(text)
            continue

        # Paragraph
        flush_list()
        blocks.append({'type': 'para', 'text': stripped})

    flush_list()
    return blocks


def build_pdf(input_md: Path, output_pdf: Path):
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle('H1', parent=styles['Heading1'], spaceAfter=8)
    h2 = ParagraphStyle('H2', parent=styles['Heading2'], spaceAfter=6)
    h3 = ParagraphStyle('H3', parent=styles['Heading3'], spaceAfter=4)
    body = ParagraphStyle('Body', parent=styles['BodyText'], leading=14, spaceAfter=6, alignment=TA_LEFT)

    doc = SimpleDocTemplate(str(output_pdf), pagesize=LETTER, leftMargin=0.85*inch, rightMargin=0.85*inch, topMargin=0.9*inch, bottomMargin=0.9*inch)

    story = []

    blocks = parse_markdown_lines(input_md.read_text(encoding='utf-8').splitlines())
    for b in blocks:
        if b['type'] == 'heading':
            style = h1 if b['level'] == 1 else h2 if b['level'] == 2 else h3
            story.append(Paragraph(b['text'], style))
        elif b['type'] == 'para':
            story.append(Paragraph(b['text'], body))
        elif b['type'] in ('ul', 'ol'):
            items = [ListItem(Paragraph(item, body), leftIndent=12) for item in b['items']]
            story.append(ListFlowable(items, bulletType='1' if b['type'] == 'ol' else 'bullet', start='1'))
        elif b['type'] == 'hr':
            story.append(Spacer(1, 6))
            story.append(HRFlowable(width='100%', thickness=1, color='#999999'))
            story.append(Spacer(1, 6))
        story.append(Spacer(1, 2))

    doc.build(story)


def main():
    if len(sys.argv) != 3:
        print("Usage: python scripts/markdown_to_pdf.py INPUT.md OUTPUT.pdf")
        sys.exit(1)
    input_md = Path(sys.argv[1])
    output_pdf = Path(sys.argv[2])
    if not input_md.exists():
        print(f"Input not found: {input_md}")
        sys.exit(2)
    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    build_pdf(input_md, output_pdf)
    print(f"✅ Wrote {output_pdf}")


if __name__ == '__main__':
    main()
