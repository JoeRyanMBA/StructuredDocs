#!/usr/bin/env python3
"""
Test heading colors with different levels
"""
import sys
sys.path.insert(0, '/workspaces/StructuredDocs/backend')

from pdf_config import PDFConfig, CorporateConfig, AcademicConfig, CompactConfig, OrganizationConfig
from reportlab.lib.styles import getSampleStyleSheet

def test_heading_colors():
    """Test that different heading levels have different colors"""
    print("🎨 Testing Heading Colors by Level")
    print("=" * 50)
    
    configs = {
        'PDFConfig (default)': PDFConfig,
        'CorporateConfig': CorporateConfig,
        'AcademicConfig': AcademicConfig,
        'CompactConfig': CompactConfig,
        'OrganizationConfig': OrganizationConfig
    }
    
    base_styles = getSampleStyleSheet()
    
    for config_name, config_class in configs.items():
        print(f"\n📋 {config_name}")
        print("-" * 30)
        
        # Show the color definitions if they exist
        colors = config_class.COLORS
        if 'h1_color' in colors:
            print(f"  Color Definitions:")
            for level in range(1, 6):
                color_key = f'h{level}_color'
                if color_key in colors:
                    color_obj = colors[color_key]
                    # Convert color back to approximate hex for display
                    r = int(color_obj.red * 255)
                    g = int(color_obj.green * 255) 
                    b = int(color_obj.blue * 255)
                    hex_color = f"#{r:02x}{g:02x}{b:02x}"
                    print(f"    H{level}: {hex_color}")
        
        # Test the actual styles created
        print(f"  Generated Heading Styles:")
        for level in range(4):
            heading_style = config_class.create_heading_style(base_styles, level)
            color_obj = heading_style.textColor
            
            # Convert color to hex for display
            r = int(color_obj.red * 255)
            g = int(color_obj.green * 255)
            b = int(color_obj.blue * 255)
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            
            print(f"    H{level+1}: {heading_style.fontSize}pt, Color: {hex_color}")

def create_heading_colors_test_pdf():
    """Create a test PDF showing different heading colors"""
    print(f"\n🔨 Creating Heading Colors Test PDF...")
    
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch
    
    doc = SimpleDocTemplate("/tmp/heading_colors_test.pdf", pagesize=A4)
    story = []
    base_styles = getSampleStyleSheet()
    
    # Title
    title_style = PDFConfig.create_title_style(base_styles)
    story.append(Paragraph("Heading Colors Test", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Show each heading level with its color
    for level in range(5):
        heading_style = PDFConfig.create_heading_style(base_styles, level)
        
        # Create heading text that shows the level and color
        color_obj = heading_style.textColor
        r = int(color_obj.red * 255)
        g = int(color_obj.green * 255)
        b = int(color_obj.blue * 255)
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        
        heading_text = f"Heading Level {level+1} - Color: {hex_color}"
        story.append(Paragraph(heading_text, heading_style))
        
        # Add some content to show context
        content_style = PDFConfig.create_content_style(base_styles, 0)
        content_text = f"This is content under H{level+1}. Font size: {heading_style.fontSize}pt. Each heading level has a distinct color for better visual hierarchy."
        story.append(Paragraph(content_text, content_style))
        story.append(Spacer(1, 0.2*inch))
    
    # Add color legend
    story.append(Spacer(1, 0.3*inch))
    legend_style = PDFConfig.create_heading_style(base_styles, 1)
    story.append(Paragraph("Color Usage Guide", legend_style))
    
    legend_content = [
        "• H1 (Dark Blue): Main sections and primary headings",
        "• H2 (Orange/Red): Major subsections",  
        "• H3 (Teal): Minor subsections",
        "• H4 (Dark Gray): Detail sections",
        "• H5+ (Medium Gray): Fine details and notes"
    ]
    
    for item in legend_content:
        story.append(Paragraph(item, content_style))
    
    doc.build(story)
    print("✅ Heading colors test PDF created: /tmp/heading_colors_test.pdf")

if __name__ == "__main__":
    test_heading_colors()
    create_heading_colors_test_pdf()
    
    print(f"\n📊 Current Heading Color Scheme:")
    print(f"  • H1: #112e51 (Dark Blue) - Primary importance")
    print(f"  • H2: #ff5622 (Orange/Red) - Secondary importance")
    print(f"  • H3: #008392 (Teal) - Tertiary importance")
    print(f"  • H4: #444444 (Dark Gray) - Detail level")
    print(f"  • H5+: #666666 (Medium Gray) - Fine details")
    
    print(f"\n🎨 How to Customize Heading Colors:")
    print(f"  1. Edit /workspaces/StructuredDocs/backend/pdf_config.py")
    print(f"  2. Modify the COLORS dictionary:")
    print(f"     'h1_color': hex_to_color('#your_color_here'),")
    print(f"     'h2_color': hex_to_color('#your_color_here'),")
    print(f"     etc.")
    print(f"  3. Restart the backend: bash restart.sh")
    
    print(f"\n🔄 Restart the backend to apply current color changes:")
    print(f"   cd /workspaces/StructuredDocs && bash restart.sh")
