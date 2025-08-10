#!/usr/bin/env python3
"""
Test the heading font fix in PDF generation
"""
import sys
sys.path.insert(0, '/workspaces/StructuredDocs/backend')

from routes.publications import convert_markdown_to_pdf_paragraphs
from pdf_config import PDFConfig
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.pagesizes import A4

def test_heading_fonts_in_content():
    """Test that markdown headers within content use Helvetica font"""
    print("🧪 Testing Heading Fonts in Content")
    print("=" * 45)
    
    # Test markdown content with headers
    test_content = """This is regular paragraph content.

## This is a subheading in content

More content after the subheading.

### Another subheading

Final paragraph content."""

    print("Test content:")
    print(test_content)
    print("\nConverted paragraphs:")
    
    # Convert using the fixed function
    paragraphs = convert_markdown_to_pdf_paragraphs(test_content)
    
    for i, para in enumerate(paragraphs, 1):
        print(f"  {i}. {repr(para)}")
        
        # Check if headers use explicit Helvetica font
        if '<font face="Helvetica-Bold">' in para:
            print(f"     ✅ Uses explicit Helvetica-Bold font")
        elif '<b>' in para and '<font' not in para:
            print(f"     ❌ Uses generic <b> tag (will inherit Times font)")
    
    return paragraphs

def create_test_pdf():
    """Create a test PDF to verify the font fix"""
    print("\n🔨 Creating Test PDF")
    print("=" * 30)
    
    base_styles = getSampleStyleSheet()
    doc = SimpleDocTemplate("/tmp/heading_font_test.pdf", pagesize=A4)
    story = []
    
    # Add title
    title_style = PDFConfig.create_title_style(base_styles)
    story.append(Paragraph("Heading Font Test", title_style))
    
    # Add main heading (should be Helvetica-Bold)
    heading_style = PDFConfig.create_heading_style(base_styles, 0)
    story.append(Paragraph("Main Section Heading (H1)", heading_style))
    
    # Add content with embedded subheadings (should also be Helvetica-Bold)
    content_style = PDFConfig.create_content_style(base_styles, 0)
    
    test_content = """This paragraph contains embedded subheadings that should use Helvetica fonts.

## Embedded H2 Subheading

This text follows the H2 subheading.

### Embedded H3 Subheading  

This text follows the H3 subheading.

Regular paragraph text should use Times-Roman font, but the subheadings above should use Helvetica-Bold."""

    # Convert content and add each paragraph
    content_paragraphs = convert_markdown_to_pdf_paragraphs(test_content)
    for para_text in content_paragraphs:
        if para_text.strip():
            story.append(Paragraph(para_text, content_style))
    
    # Build PDF
    doc.build(story)
    print("✅ Test PDF created: /tmp/heading_font_test.pdf")
    
    return "/tmp/heading_font_test.pdf"

if __name__ == "__main__":
    # Test the conversion function
    paragraphs = test_heading_fonts_in_content()
    
    # Create test PDF
    pdf_path = create_test_pdf()
    
    print(f"\n📊 Summary:")
    print(f"  📄 Test PDF: {pdf_path}")
    print(f"  🔍 Check that embedded headings in content use Helvetica font")
    print(f"  💡 Compare with main section headings to verify consistency")
    
    # Check if the fix is properly applied
    has_explicit_font = any('<font face="Helvetica-Bold">' in p for p in paragraphs)
    has_generic_bold = any('<b>' in p and '<font' not in p for p in paragraphs if '<b>' in p)
    
    print(f"\n✅ Font Fix Status:")
    print(f"  - Uses explicit Helvetica font: {'YES' if has_explicit_font else 'NO'}")
    print(f"  - Has generic bold tags: {'YES (PROBLEM)' if has_generic_bold else 'NO (GOOD)'}")
    
    if has_explicit_font and not has_generic_bold:
        print(f"\n🎉 Font fix is working! All headings should now use Helvetica.")
    else:
        print(f"\n❌ Font fix needs more work.")
        
    print(f"\n🔄 Restart backend to apply changes: bash restart.sh")
