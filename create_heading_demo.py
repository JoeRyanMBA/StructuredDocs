#!/usr/bin/env python3
"""
Create a test PDF that clearly demonstrates the heading styles
"""
import sys
sys.path.insert(0, '/workspaces/StructuredDocs/backend')

from pdf_config import PDFConfig
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

def create_heading_demo_pdf():
    """Create a PDF that clearly shows all heading levels"""
    print("🔨 Creating heading demonstration PDF...")
    
    # Create PDF
    doc = SimpleDocTemplate("/tmp/heading_demo.pdf", pagesize=A4)
    story = []
    base_styles = getSampleStyleSheet()
    
    # Title
    title_style = PDFConfig.create_title_style(base_styles)
    story.append(Paragraph("Heading Style Demonstration", title_style))
    story.append(Spacer(1, 0.5*inch))
    
    # Demonstration of each heading level
    for level in range(4):  # Show levels 0-3
        heading_style = PDFConfig.create_heading_style(base_styles, level)
        content_style = PDFConfig.create_content_style(base_styles, level)
        
        # Add heading
        heading_text = f"Level {level} Heading (H{level+1}) - {heading_style.fontSize}pt {heading_style.fontName}"
        story.append(Paragraph(heading_text, heading_style))
        
        # Add description
        desc_text = f"This heading uses font: {heading_style.fontName}, size: {heading_style.fontSize}pt. "
        desc_text += "The font should be Helvetica-Bold (non-italic) with the size shown."
        story.append(Paragraph(desc_text, content_style))
        story.append(Spacer(1, 0.2*inch))
    
    # Build the PDF
    doc.build(story)
    print("✅ Heading demonstration PDF created: /tmp/heading_demo.pdf")

if __name__ == "__main__":
    create_heading_demo_pdf()
    print(f"\n📋 Generated test files:")
    print(f"   - /tmp/heading_demo.pdf (style demonstration)")
    print(f"   - /tmp/fresh_test.pdf (actual publication export)")
    print(f"\n💡 Compare these PDFs to verify heading styles are working correctly.")
