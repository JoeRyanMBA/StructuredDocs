#!/usr/bin/env python3

import sys
import os
sys.path.append('/workspaces/StructuredDocs/backend')

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

# Mock publication class
class MockPublication:
    def __init__(self):
        self.id = 1234
        self.form_number = "EC-1234"
        self.title = "Test Publication"
        self.subtitle = "Test Subtitle"

# Import our updated template classes
from routes.publications import BackgroundImageDocTemplate, HeaderDocTemplate

def test_background_template():
    """Test BackgroundImageDocTemplate"""
    print("Testing BackgroundImageDocTemplate...")
    
    # Create mock publication
    publication = MockPublication()
    
    # Create PDF with BackgroundImageDocTemplate
    doc = BackgroundImageDocTemplate(
        'test_background_layout.pdf',
        pagesize=letter,
        publication=publication
    )
    
    # Build content
    styles = getSampleStyleSheet()
    story = []
    
    # Add title page content
    story.append(Paragraph("Test Title Page", styles['Title']))
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("This is a test publication to verify the footer positioning.", styles['Normal']))
    
    # Add page break to trigger TOC page
    story.append(PageBreak())
    
    # Add TOC content
    story.append(Paragraph("Table of Contents", styles['Heading1']))
    story.append(Paragraph("Chapter 1 .................. 1", styles['Normal']))
    story.append(Paragraph("Chapter 2 .................. 5", styles['Normal']))
    story.append(Paragraph("Chapter 3 .................. 10", styles['Normal']))
    
    # Add page break to trigger content page
    story.append(PageBreak())
    
    # Add regular content
    story.append(Paragraph("Chapter 1: Introduction", styles['Heading1']))
    story.append(Paragraph("This is the content of the first chapter. " * 50, styles['Normal']))
    
    try:
        doc.build(story)
        print(f"✓ BackgroundImageDocTemplate test completed: test_background_layout.pdf")
        return True
    except Exception as e:
        print(f"✗ BackgroundImageDocTemplate test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_header_template():
    """Test HeaderDocTemplate"""
    print("Testing HeaderDocTemplate...")
    
    # Create mock publication
    publication = MockPublication()
    
    # Create PDF with HeaderDocTemplate
    doc = HeaderDocTemplate(
        'test_header_layout.pdf',
        pagesize=letter,
        publication=publication
    )
    
    # Build content
    styles = getSampleStyleSheet()
    story = []
    
    # Add title page content
    story.append(Paragraph("Test Title Page", styles['Title']))
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("This is a test publication to verify the header and footer positioning.", styles['Normal']))
    
    # Add page break to trigger TOC page
    story.append(PageBreak())
    
    # Add TOC content  
    story.append(Paragraph("Table of Contents", styles['Heading1']))
    story.append(Paragraph("Chapter 1 .................. 1", styles['Normal']))
    story.append(Paragraph("Chapter 2 .................. 5", styles['Normal']))
    story.append(Paragraph("Chapter 3 .................. 10", styles['Normal']))
    
    # Add page break to trigger content page
    story.append(PageBreak())
    
    # Add regular content
    story.append(Paragraph("Chapter 1: Introduction", styles['Heading1']))
    story.append(Paragraph("This is the content of the first chapter. " * 50, styles['Normal']))
    
    try:
        doc.build(story)
        print(f"✓ HeaderDocTemplate test completed: test_header_layout.pdf")
        return True
    except Exception as e:
        print(f"✗ HeaderDocTemplate test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing updated footer positioning...")
    print("=" * 50)
    
    success1 = test_background_template()
    print()
    success2 = test_header_template()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("✓ All layout tests passed!")
        print("\nGenerated files:")
        if os.path.exists('test_background_layout.pdf'):
            print(f"  - test_background_layout.pdf ({os.path.getsize('test_background_layout.pdf')} bytes)")
        if os.path.exists('test_header_layout.pdf'):
            print(f"  - test_header_layout.pdf ({os.path.getsize('test_header_layout.pdf')} bytes)")
    else:
        print("✗ Some tests failed!")
        sys.exit(1)
