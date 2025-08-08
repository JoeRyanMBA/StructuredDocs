#!/usr/bin/env python3
"""
Test script to verify PDF heading styles are correct (non-italic, proper font sizes)
"""
import sys
sys.path.insert(0, '/workspaces/StructuredDocs/backend')

try:
    import PyPDF2
    PDF_INSPECTION_AVAILABLE = True
    print("✅ PyPDF2 available for PDF inspection")
except ImportError:
    PDF_INSPECTION_AVAILABLE = False
    print("⚠️  PyPDF2 not available, trying alternative approach")

# Test by generating a simple PDF with the current config
from pdf_config import PDFConfig
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.pagesizes import A4
import io
import requests

def test_heading_styles():
    """Test that heading styles are configured correctly"""
    print("🧪 Testing PDF heading style configuration...")
    
    # Get base styles
    base_styles = getSampleStyleSheet()
    
    # Test heading styles for levels 1, 2, 3
    for level in [1, 2, 3]:
        style = PDFConfig.create_heading_style(base_styles, level)
        print(f"\n📝 Level {level} Heading Style:")
        print(f"   Font Name: {style.fontName}")
        print(f"   Font Size: {style.fontSize}")
        print(f"   Text Color: {style.textColor}")
        
        # Check if font is italic
        is_italic = 'Oblique' in style.fontName or 'Italic' in style.fontName
        if is_italic:
            print(f"   ❌ ISSUE: Font is italic! ({style.fontName})")
        else:
            print(f"   ✅ Font is NOT italic ({style.fontName})")
    
    # Test expected font sizes
    expected_sizes = {1: 16, 2: 16, 3: 13}  # Based on config
    print(f"\n📏 Font Size Verification:")
    for level in [1, 2, 3]:
        style = PDFConfig.create_heading_style(base_styles, level)
        expected = expected_sizes[level]
        actual = style.fontSize
        if actual == expected:
            print(f"   ✅ Level {level}: {actual}pt (correct)")
        else:
            print(f"   ❌ Level {level}: {actual}pt (expected {expected}pt)")

def create_test_pdf():
    """Create a test PDF with different heading levels"""
    print(f"\n🔨 Creating test PDF with heading samples...")
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    
    base_styles = getSampleStyleSheet()
    
    # Add heading samples
    for level in [1, 2, 3]:
        style = PDFConfig.create_heading_style(base_styles, level)
        heading_text = f"This is a Level {level} Heading"
        story.append(Paragraph(heading_text, style))
        
        # Add some content
        content_style = PDFConfig.create_content_style(base_styles, level)
        content_text = "This is some sample content to show the difference in formatting."
        story.append(Paragraph(content_text, content_style))
    
    doc.build(story)
    
    # Save the test PDF
    with open('/tmp/heading_test.pdf', 'wb') as f:
        f.write(buffer.getvalue())
    
    print(f"✅ Test PDF created: /tmp/heading_test.pdf")
    return buffer.getvalue()

def inspect_pdf_fonts(pdf_path):
    """Inspect the actual fonts used in a PDF file"""
    if not PDF_INSPECTION_AVAILABLE:
        print("⚠️  PDF inspection not available (PyPDF2 not installed)")
        return
    
    print(f"\n🔍 Inspecting fonts in PDF: {pdf_path}")
    
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            # Get fonts from first page
            if len(reader.pages) > 0:
                page = reader.pages[0]
                
                # Try to extract font information
                if '/Font' in page['/Resources']:
                    fonts = page['/Resources']['/Font']
                    print("📝 Fonts found in PDF:")
                    for font_name, font_obj in fonts.items():
                        if hasattr(font_obj, 'get_object'):
                            font_details = font_obj.get_object()
                            base_font = font_details.get('/BaseFont', 'Unknown')
                            print(f"   {font_name}: {base_font}")
                        else:
                            print(f"   {font_name}: {font_obj}")
                else:
                    print("⚠️  No font information found in PDF")
            else:
                print("⚠️  PDF has no pages")
                
    except Exception as e:
        print(f"❌ Error inspecting PDF: {e}")

def test_actual_pdf_export():
    """Test the actual PDF export from the API"""
    print(f"\n🌐 Testing actual PDF export from API...")
    
    import requests
    
    try:
        # Test default format
        response = requests.get("http://localhost:5050/api/publications/4/export/pdf?format=default", timeout=10)
        
        if response.status_code == 200:
            pdf_path = '/tmp/api_test.pdf'
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            print(f"✅ API PDF export successful: {pdf_path}")
            
            # Inspect the fonts in this PDF
            inspect_pdf_fonts(pdf_path)
        else:
            print(f"❌ API PDF export failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")

if __name__ == "__main__":
    test_heading_styles()
    create_test_pdf()
    
    # Inspect the test PDF we created
    inspect_pdf_fonts('/tmp/heading_test.pdf')
    
    # Test the actual API export
    test_actual_pdf_export()
    
    print(f"\n🎉 Testing complete!")
    print(f"\nTo view the test PDFs:")
    print(f"  - Generated export: /tmp/test_heading_styles.pdf")
    print(f"  - Heading test: /tmp/heading_test.pdf")
    print(f"  - API test: /tmp/api_test.pdf")
