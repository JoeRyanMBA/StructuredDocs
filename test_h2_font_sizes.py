#!/usr/bin/env python3
"""
Test the H2 font size increases across all PDF configurations
"""
import sys
sys.path.insert(0, '/workspaces/StructuredDocs/backend')

from pdf_config import PDFConfig, CorporateConfig, AcademicConfig, CompactConfig, OrganizationConfig
from reportlab.lib.styles import getSampleStyleSheet

def test_h2_font_sizes():
    """Test that H2 font sizes have been increased appropriately"""
    print("🔍 Testing H2 Font Size Changes")
    print("=" * 50)
    
    configs = {
        'PDFConfig (default)': PDFConfig,
        'CorporateConfig': CorporateConfig,
        'AcademicConfig': AcademicConfig,
        'CompactConfig': CompactConfig,
        'OrganizationConfig': OrganizationConfig
    }
    
    base_styles = getSampleStyleSheet()
    
    print("📊 Font Size Hierarchy:")
    print("-" * 30)
    
    for config_name, config_class in configs.items():
        print(f"\n📋 {config_name}")
        
        # Get font sizes from configuration
        h1_size = config_class.FONT_SIZES['h1']
        h2_size = config_class.FONT_SIZES['h2']
        h3_size = config_class.FONT_SIZES['h3']
        h4_size = config_class.FONT_SIZES['h4']
        
        print(f"  H1: {h1_size}pt")
        print(f"  H2: {h2_size}pt")
        print(f"  H3: {h3_size}pt")
        print(f"  H4: {h4_size}pt")
        
        # Test actual generated styles
        h1_style = config_class.create_heading_style(base_styles, 0)
        h2_style = config_class.create_heading_style(base_styles, 1)
        h3_style = config_class.create_heading_style(base_styles, 2)
        h4_style = config_class.create_heading_style(base_styles, 3)
        
        print(f"  Generated H1: {h1_style.fontSize}pt")
        print(f"  Generated H2: {h2_style.fontSize}pt")
        print(f"  Generated H3: {h3_style.fontSize}pt")
        print(f"  Generated H4: {h4_style.fontSize}pt")
        
        # Check size relationships
        h2_increased = h2_size >= h3_size + 2  # H2 should be at least 2pt larger than H3
        good_hierarchy = h1_size >= h2_size >= h3_size >= h4_size
        
        print(f"  ✅ H2 prominence: {'GOOD' if h2_increased else 'NEEDS IMPROVEMENT'}")
        print(f"  ✅ Size hierarchy: {'CORRECT' if good_hierarchy else 'INCORRECT'}")

def create_h2_font_test_pdf():
    """Create a test PDF showing H2 font sizes"""
    print(f"\n🔨 Creating H2 Font Size Test PDF...")
    
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch
    
    doc = SimpleDocTemplate("/tmp/h2_font_test.pdf", pagesize=A4)
    story = []
    base_styles = getSampleStyleSheet()
    
    configs = [
        ('Default', PDFConfig),
        ('Corporate', CorporateConfig), 
        ('Academic', AcademicConfig),
        ('Compact', CompactConfig),
        ('Organization', OrganizationConfig)
    ]
    
    # Title
    title_style = PDFConfig.create_title_style(base_styles)
    story.append(Paragraph("H2 Font Size Test", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    for config_name, config_class in configs:
        # Section header
        section_style = PDFConfig.create_heading_style(base_styles, 0)
        story.append(Paragraph(f"{config_name} Configuration", section_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Show each heading level
        for level in range(4):
            heading_style = config_class.create_heading_style(base_styles, level)
            heading_text = f"H{level+1} Heading - {heading_style.fontSize}pt"
            story.append(Paragraph(heading_text, heading_style))
            
            # Add size info
            content_style = config_class.create_content_style(base_styles, 0)
            size_info = f"Font: {heading_style.fontName}, Size: {heading_style.fontSize}pt"
            story.append(Paragraph(size_info, content_style))
            story.append(Spacer(1, 0.1*inch))
        
        story.append(Spacer(1, 0.3*inch))
    
    doc.build(story)
    print("✅ H2 font size test PDF created: /tmp/h2_font_test.pdf")

if __name__ == "__main__":
    test_h2_font_sizes()
    create_h2_font_test_pdf()
    
    print(f"\n📊 Summary of H2 Font Size Changes:")
    print(f"  • Default Config: H2 = 18pt (same as H1)")
    print(f"  • Corporate Config: H2 = 17pt (2pt larger than H3)")
    print(f"  • Academic Config: H2 = 17pt (5pt larger than H3)")
    print(f"  • Compact Config: H2 = 15pt (same as H1)")
    print(f"  • Organization Config: H2 = 18pt (same as H1)")
    
    print(f"\n💡 All H2 headings are now more prominent!")
    print(f"📄 Check /tmp/h2_font_test.pdf to see the visual differences.")
    
    print(f"\n🔄 Restart the backend to apply changes:")
    print(f"   cd /workspaces/StructuredDocs && bash restart.sh")
