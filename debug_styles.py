#!/usr/bin/env python3
"""
Create a debug PDF that shows exactly what styles are being applied to headings
"""
import sys
sys.path.insert(0, '/workspaces/StructuredDocs/backend')

from pdf_config import PDFConfig
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

def create_debug_pdf():
    """Create a PDF that shows the exact styles being applied"""
    print("🔍 Creating debug PDF to inspect actual styles...")
    
    doc = SimpleDocTemplate("/tmp/debug_styles.pdf", pagesize=A4)
    story = []
    base_styles = getSampleStyleSheet()
    
    # Show ReportLab's default styles for comparison
    story.append(Paragraph("ReportLab Default Styles (for comparison):", base_styles['Normal']))
    story.append(Paragraph("This is Heading1 style", base_styles['Heading1']))
    story.append(Paragraph("This is Heading2 style", base_styles['Heading2']))
    story.append(Paragraph("This is Heading3 style", base_styles['Heading3']))
    story.append(Spacer(1, 0.3*inch))
    
    # Show our custom styles
    story.append(Paragraph("Our Custom Heading Styles:", base_styles['Normal']))
    
    for level in range(3):
        custom_style = PDFConfig.create_heading_style(base_styles, level)
        heading_text = f"Level {level} Custom Heading (Font: {custom_style.fontName}, Size: {custom_style.fontSize}pt)"
        story.append(Paragraph(heading_text, custom_style))
        
        # Add style details as normal text
        details = f"  → Parent: {custom_style.parent.name if custom_style.parent else 'None'}, "
        details += f"FontName: {custom_style.fontName}, "
        details += f"FontSize: {custom_style.fontSize}pt"
        story.append(Paragraph(details, base_styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
    
    doc.build(story)
    print("✅ Debug PDF created: /tmp/debug_styles.pdf")
    
    # Also show the style details in console
    print("\n📋 Style Details:")
    for level in range(3):
        style = PDFConfig.create_heading_style(base_styles, level)
        print(f"  Level {level}: {style.fontName}, {style.fontSize}pt (parent: {style.parent.name if style.parent else 'None'})")

if __name__ == "__main__":
    create_debug_pdf()
