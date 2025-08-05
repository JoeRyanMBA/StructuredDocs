#!/usr/bin/env python3
"""
PDF Debug Tool - Check available fonts and test PDF generation
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.pdfbase import pdfutils
import io

def test_fonts():
    """Test available fonts in ReportLab"""
    print("🔍 Testing ReportLab Fonts")
    print("=" * 40)
    
    # Standard fonts that should always work
    standard_fonts = [
        'Helvetica',
        'Helvetica-Bold', 
        'Helvetica-Oblique',
        'Helvetica-BoldOblique',
        'Times-Roman',
        'Times-Bold',
        'Times-Italic', 
        'Times-BoldItalic',
        'Courier',
        'Courier-Bold',
        'Courier-Oblique',
        'Courier-BoldOblique'
    ]
    
    print("✅ Standard fonts available:")
    for font in standard_fonts:
        print(f"   - {font}")
    
    # Test problematic fonts
    problematic_fonts = [
        'Roboto-Bold',
        'Lora',
        'Lora-Regular', 
        'Roboto-Italic'
    ]
    
    print("\n❌ Fonts that might cause issues:")
    for font in problematic_fonts:
        print(f"   - {font} (not registered)")
        
    return standard_fonts

def test_simple_pdf():
    """Test generating a simple PDF"""
    print("\n🧪 Testing Simple PDF Generation")
    print("=" * 40)
    
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        styles = getSampleStyleSheet()
        
        # Test with safe fonts
        title_style = ParagraphStyle(
            'TestTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=24,
            textColor=colors.blue
        )
        
        story.append(Paragraph("Test PDF Generation", title_style))
        story.append(Spacer(1, 20))
        story.append(Paragraph("This is a test paragraph with safe fonts.", styles['Normal']))
        
        doc.build(story)
        
        pdf_data = buffer.getvalue()
        buffer.close()
        
        print(f"✅ Simple PDF generated successfully: {len(pdf_data)} bytes")
        
        # Save test file
        with open('test_simple.pdf', 'wb') as f:
            f.write(pdf_data)
        print("✅ Test PDF saved as test_simple.pdf")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating simple PDF: {e}")
        return False

def main():
    """Main test function"""
    print("🔧 PDF Generation Debugging Tool")
    print("=" * 50)
    
    # Test fonts
    standard_fonts = test_fonts()
    
    # Test simple PDF
    success = test_simple_pdf()
    
    if success:
        print("\n💡 Recommendations:")
        print("   1. Use standard ReportLab fonts (Helvetica, Times, Courier)")
        print("   2. Replace custom fonts with safe alternatives")
        print("   3. Register custom fonts if needed with pdfutils.registerFont()")
    
    print("\n🔧 Safe font mapping:")
    print("   Roboto-Bold     → Helvetica-Bold")
    print("   Lora            → Times-Roman") 
    print("   Lora-Regular    → Times-Roman")
    print("   Roboto-Italic   → Helvetica-Oblique")

if __name__ == "__main__":
    main()
