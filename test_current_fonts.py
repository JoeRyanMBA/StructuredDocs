#!/usr/bin/env python3
"""
Test the current PDF fonts to see what's actually being used in headings
"""
import sys
sys.path.insert(0, '/workspaces/StructuredDocs/backend')

from pdf_config import PDFConfig
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

def test_current_pdf_fonts():
    """Create a test PDF showing actual fonts used"""
    print("🔨 Testing current PDF fonts...")
    
    doc = SimpleDocTemplate("/tmp/current_fonts_test.pdf", pagesize=A4)
    story = []
    base_styles = getSampleStyleSheet()
    
    # Test title style
    title_style = PDFConfig.create_title_style(base_styles)
    story.append(Paragraph("Title Style Font Test", title_style))
    story.append(Paragraph(f"Font: {title_style.fontName}, Size: {title_style.fontSize}pt", base_styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Test subtitle style
    subtitle_style = PDFConfig.create_subtitle_style(base_styles)
    story.append(Paragraph("Subtitle Style Font Test", subtitle_style))
    story.append(Paragraph(f"Font: {subtitle_style.fontName}, Size: {subtitle_style.fontSize}pt", base_styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Test heading styles
    for level in range(4):
        heading_style = PDFConfig.create_heading_style(base_styles, level)
        
        # Main heading
        heading_text = f"Level {level} Heading (H{level+1})"
        story.append(Paragraph(heading_text, heading_style))
        
        # Details about the style
        details = f"Font: {heading_style.fontName}, Size: {heading_style.fontSize}pt"
        story.append(Paragraph(details, base_styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
    
    # Show what's configured in PDFConfig
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("PDFConfig Font Settings:", base_styles['Heading2']))
    
    font_info = [
        f"Title font: {PDFConfig.FONTS['title']}",
        f"Heading font: {PDFConfig.FONTS['heading']}",
        f"Body font: {PDFConfig.FONTS['body']}",
        f"Caption font: {PDFConfig.FONTS['caption']}",
        f"Code font: {PDFConfig.FONTS['code']}"
    ]
    
    for info in font_info:
        story.append(Paragraph(info, base_styles['Normal']))
    
    doc.build(story)
    print("✅ Current fonts test PDF created: /tmp/current_fonts_test.pdf")

if __name__ == "__main__":
    test_current_pdf_fonts()
    print("\n📋 Generated test file:")
    print("  - /tmp/current_fonts_test.pdf")
    print("\n💡 This shows what fonts are actually being used in your PDFs.")
