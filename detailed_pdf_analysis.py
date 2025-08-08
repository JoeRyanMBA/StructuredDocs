#!/usr/bin/env python3
"""
Detailed PDF font analysis to identify exactly which content is using italic fonts
"""
import sys
sys.path.insert(0, '/workspaces/StructuredDocs/backend')

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

def detailed_pdf_analysis(pdf_path):
    """Perform detailed analysis of PDF content and fonts"""
    if not PDF_AVAILABLE:
        print("PyPDF2 not available")
        return
    
    print(f"\n🔬 Detailed analysis of: {pdf_path}")
    
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            for page_num, page in enumerate(reader.pages):
                print(f"\n📄 Page {page_num + 1}:")
                
                # Extract text content
                try:
                    text = page.extract_text()
                    lines = text.split('\n')
                    print(f"   Text content ({len(lines)} lines):")
                    for i, line in enumerate(lines[:10]):  # Show first 10 lines
                        if line.strip():
                            print(f"     {i+1}: {line.strip()}")
                    if len(lines) > 10:
                        print(f"     ... ({len(lines)-10} more lines)")
                except:
                    print("   Could not extract text")
                
                # Check fonts on this page
                if hasattr(page, 'get') and '/Resources' in page:
                    resources = page['/Resources']
                    if '/Font' in resources:
                        fonts = resources['/Font']
                        print(f"   Fonts used on this page:")
                        for font_ref, font_obj in fonts.items():
                            try:
                                if hasattr(font_obj, 'get_object'):
                                    font_details = font_obj.get_object()
                                    base_font = font_details.get('/BaseFont', 'Unknown')
                                    font_type = font_details.get('/Subtype', 'Unknown')
                                    print(f"     {font_ref}: {base_font} ({font_type})")
                                    
                                    # Check if this is an italic/oblique font
                                    if 'Oblique' in str(base_font) or 'Italic' in str(base_font):
                                        print(f"       ⚠️  ITALIC FONT DETECTED: {base_font}")
                            except Exception as e:
                                print(f"     {font_ref}: Error reading font ({e})")
                
    except Exception as e:
        print(f"❌ Error analyzing PDF: {e}")

def create_heading_only_test():
    """Create a test PDF with ONLY headings to isolate the issue"""
    from pdf_config import PDFConfig
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch
    
    print(f"\n🧪 Creating heading-only test PDF...")
    
    doc = SimpleDocTemplate("/tmp/headings_only.pdf", pagesize=A4)
    story = []
    base_styles = getSampleStyleSheet()
    
    # Add title
    story.append(Paragraph("HEADING FONT TEST", base_styles['Title']))
    story.append(Spacer(1, 0.3*inch))
    
    # Add only headings (no content that might use italic)
    for level in [0, 1, 2]:
        style = PDFConfig.create_heading_style(base_styles, level)
        heading_text = f"Level {level} Heading - Font: {style.fontName} - Size: {style.fontSize}pt"
        story.append(Paragraph(heading_text, style))
        story.append(Spacer(1, 0.2*inch))
    
    doc.build(story)
    print(f"✅ Heading-only test PDF created: /tmp/headings_only.pdf")
    return "/tmp/headings_only.pdf"

if __name__ == "__main__":
    # Analyze the API export
    print("🔍 Analyzing API export PDF...")
    detailed_pdf_analysis("/tmp/api_test.pdf")
    
    # Create and analyze a heading-only test
    heading_only_path = create_heading_only_test()
    detailed_pdf_analysis(heading_only_path)
    
    print(f"\n📋 Summary:")
    print(f"   - API export: /tmp/api_test.pdf")
    print(f"   - Heading-only test: /tmp/headings_only.pdf")
    print(f"\n💡 Compare these files to see if headings specifically use italic fonts.")
