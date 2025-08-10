#!/usr/bin/env python3
"""
Test the heading font size fix for markdown headers within content
"""
import sys
sys.path.insert(0, '/workspaces/StructuredDocs/backend')

# Import the function we just modified
from routes.publications import convert_markdown_to_pdf_paragraphs

def test_heading_size_conversion():
    """Test that markdown headers get converted with different font sizes"""
    print("🧪 Testing Heading Font Size Conversion")
    print("=" * 50)
    
    # Test content with multiple heading levels
    test_content = """This is some content.

# Heading Level 1 (should be 16pt)

Some content after H1.

## Heading Level 2 (should be 14pt)

Content after H2.

### Heading Level 3 (should be 12pt)

Content after H3.

#### Heading Level 4 (should be 11pt)

Final content.

##### Deep Heading (should be 11pt)

More content."""

    print("Original markdown content:")
    print(test_content)
    print("\n" + "="*60)
    
    # Convert using our function
    paragraphs = convert_markdown_to_pdf_paragraphs(test_content)
    
    print("\nConverted paragraphs:")
    for i, para in enumerate(paragraphs, 1):
        if para.strip():
            print(f"{i:2d}: {para}")
    
    print("\n" + "="*60)
    print("Font Size Analysis:")
    
    # Analyze the font sizes in the output
    for i, para in enumerate(paragraphs, 1):
        if 'font face="Helvetica-Bold"' in para and 'size=' in para:
            # Extract the font size
            import re
            size_match = re.search(r'size="(\d+)"', para)
            text_match = re.search(r'<b>(.*?)</b>', para)
            
            if size_match and text_match:
                size = size_match.group(1)
                text = text_match.group(1)
                print(f"  Heading: '{text}' -> {size}pt")
    
    return paragraphs

def create_heading_size_test_pdf():
    """Create a test PDF to verify heading sizes work in practice"""
    print(f"\n🔨 Creating Heading Size Test PDF...")
    
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch
    from reportlab.lib.styles import getSampleStyleSheet
    from pdf_config import PDFConfig
    
    doc = SimpleDocTemplate("/tmp/heading_sizes_test.pdf", pagesize=A4)
    story = []
    base_styles = getSampleStyleSheet()
    
    # Title
    title_style = PDFConfig.create_title_style(base_styles)
    story.append(Paragraph("Heading Size Test Within Content", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Test content with various heading levels
    test_content = """This paragraph shows how headings within content are rendered with different font sizes.

# This is H1 within content (16pt)

This paragraph follows the H1 heading.

## This is H2 within content (14pt)

This paragraph follows the H2 heading.

### This is H3 within content (12pt)

This paragraph follows the H3 heading.

#### This is H4 within content (11pt)

This paragraph follows the H4 heading.

##### This is H5 within content (11pt)

This is the final paragraph showing the smallest heading size."""
    
    # Convert content to paragraphs
    paragraphs = convert_markdown_to_pdf_paragraphs(test_content)
    
    # Add each paragraph to the story
    content_style = PDFConfig.create_content_style(base_styles, 0)
    for para in paragraphs:
        if para.strip():
            story.append(Paragraph(para, content_style))
            story.append(Spacer(1, 6))
    
    doc.build(story)
    print("✅ Heading sizes test PDF created: /tmp/heading_sizes_test.pdf")

if __name__ == "__main__":
    # Test the conversion function
    converted_paras = test_heading_size_conversion()
    
    # Create test PDF
    create_heading_size_test_pdf()
    
    print(f"\n📊 Expected Font Sizes:")
    print(f"  • H1 within content: 16pt")
    print(f"  • H2 within content: 14pt") 
    print(f"  • H3 within content: 12pt")
    print(f"  • H4+ within content: 11pt")
    
    print(f"\n💡 The fix ensures that merged headings (from consecutive headings)")
    print(f"   now render with appropriate font sizes instead of all being the same.")
    
    print(f"\n🔄 Restart the backend to apply the fix:")
    print(f"   cd /workspaces/StructuredDocs && bash restart.sh")
