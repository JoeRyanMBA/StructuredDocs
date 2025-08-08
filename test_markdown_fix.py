#!/usr/bin/env python3
"""
Test the Markdown heading conversion fix
"""
import sys
sys.path.insert(0, '/workspaces/StructuredDocs/backend')

from backend.routes.publications import convert_markdown_to_pdf_paragraphs
from pdf_config import PDFConfig
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

def test_markdown_conversion():
    """Test how Markdown headers are converted"""
    
    sample_markdown = """# Income Distribution Analysis
## Overview
Methods for analyzing income distribution patterns in survey data.
### Key Metrics
- Median household income
- Income percentiles
- Gini coefficient
- Income inequality measures

Some regular text with **bold** and *italic* formatting."""

    print("🧪 Testing Markdown to PDF conversion...")
    print("\n📝 Input Markdown:")
    print(sample_markdown)
    
    paragraphs = convert_markdown_to_pdf_paragraphs(sample_markdown)
    print(f"\n📄 Converted Paragraphs ({len(paragraphs)}):")
    for i, para in enumerate(paragraphs):
        print(f"  {i+1}: {para}")

def create_markdown_test_pdf():
    """Create a PDF showing the Markdown conversion results"""
    print(f"\n🔨 Creating Markdown test PDF...")
    
    sample_markdown = """# Income Distribution Analysis
## Overview  
Methods for analyzing income distribution patterns in survey data.
### Key Metrics
- Median household income
- Income percentiles
- Gini coefficient
- Income inequality measures

Some regular text with **bold** and *italic* formatting."""

    doc = SimpleDocTemplate("/tmp/markdown_test.pdf", pagesize=A4)
    story = []
    base_styles = getSampleStyleSheet()
    
    # Add title
    story.append(Paragraph("Markdown Conversion Test", base_styles['Title']))
    story.append(Spacer(1, 0.3*inch))
    
    # Show original markdown
    story.append(Paragraph("Original Markdown:", base_styles['Heading2']))
    for line in sample_markdown.split('\n'):
        if line.strip():
            story.append(Paragraph(line, base_styles['Code']))
    
    story.append(Spacer(1, 0.3*inch))
    
    # Show converted result
    story.append(Paragraph("Converted Result:", base_styles['Heading2']))
    paragraphs = convert_markdown_to_pdf_paragraphs(sample_markdown)
    
    content_style = PDFConfig.create_content_style(base_styles, 0)
    for para in paragraphs:
        if para.strip():
            story.append(Paragraph(para, content_style))
            story.append(Spacer(1, 0.1*inch))
    
    doc.build(story)
    print(f"✅ Markdown test PDF created: /tmp/markdown_test.pdf")

if __name__ == "__main__":
    test_markdown_conversion()
    create_markdown_test_pdf()
    
    print(f"\n🎉 Testing complete!")
    print(f"\n📋 Generated files:")
    print(f"  - /tmp/markdown_test.pdf (shows conversion results)")
    print(f"  - /tmp/fixed_markdown_headings.pdf (actual publication with fix)")
    print(f"\n💡 Markdown headers should now be bold (not italic) in the PDFs.")
