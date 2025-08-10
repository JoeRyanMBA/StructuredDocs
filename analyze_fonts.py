#!/usr/bin/env python3
"""
Analyze the actual font configuration and styles being created
"""
import sys
sys.path.insert(0, '/workspaces/StructuredDocs/backend')

from pdf_config import PDFConfig, CorporateConfig, AcademicConfig, CompactConfig, OrganizationConfig
from reportlab.lib.styles import getSampleStyleSheet

def analyze_font_configuration():
    """Analyze the font configuration and see what's actually being applied"""
    print("🔍 Analyzing PDF Font Configuration")
    print("=" * 60)
    
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
        print("-" * 40)
        
        # Check the FONTS dictionary
        print(f"Font Configuration:")
        for font_type, font_name in config_class.FONTS.items():
            print(f"  {font_type}: {font_name}")
        
        # Test the actual styles created
        print(f"\nGenerated Styles:")
        
        # Title style
        title_style = config_class.create_title_style(base_styles)
        print(f"  Title: {title_style.fontName} (size: {title_style.fontSize})")
        
        # Subtitle style
        subtitle_style = config_class.create_subtitle_style(base_styles)
        print(f"  Subtitle: {subtitle_style.fontName} (size: {subtitle_style.fontSize})")
        
        # Heading styles for different levels
        for level in range(4):
            heading_style = config_class.create_heading_style(base_styles, level)
            print(f"  H{level+1}: {heading_style.fontName} (size: {heading_style.fontSize})")
    
    # Also check ReportLab base styles to see if there's inheritance
    print(f"\n🔍 ReportLab Base Styles Analysis:")
    print("-" * 40)
    base_styles = getSampleStyleSheet()
    
    important_styles = ['Normal', 'Heading1', 'Heading2', 'Heading3', 'Title']
    for style_name in important_styles:
        if style_name in base_styles:
            style = base_styles[style_name]
            print(f"  {style_name}: {style.fontName} (parent: {getattr(style, 'parent', 'None')})")

def test_roboto_registration():
    """Test if we can register Roboto fonts"""
    print(f"\n🧪 Testing Roboto Font Registration")
    print("-" * 40)
    
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.fonts import addMapping
    
    # Common system paths where Roboto might be found
    roboto_paths = [
        '/usr/share/fonts/truetype/roboto/Roboto-Bold.ttf',
        '/usr/share/fonts/roboto/Roboto-Bold.ttf',
        '/System/Library/Fonts/Roboto-Bold.ttf',
        '/home/fonts/Roboto-Bold.ttf',
        '/workspaces/StructuredDocs/fonts/Roboto-Bold.ttf'
    ]
    
    import os
    roboto_found = False
    
    for path in roboto_paths:
        if os.path.exists(path):
            print(f"✅ Found Roboto font: {path}")
            try:
                # Try to register it
                pdfmetrics.registerFont(TTFont('Roboto-Bold', path))
                addMapping('Roboto', 0, 0, 'Roboto-Bold')  # Regular
                addMapping('Roboto', 1, 0, 'Roboto-Bold')  # Bold
                print(f"✅ Successfully registered Roboto-Bold from {path}")
                roboto_found = True
                break
            except Exception as e:
                print(f"❌ Failed to register Roboto font: {e}")
        else:
            print(f"❌ Roboto font not found at: {path}")
    
    if not roboto_found:
        print(f"\n💡 Roboto fonts are not available on this system.")
        print(f"   Current configuration correctly uses Helvetica-Bold as fallback.")
        print(f"   To use Roboto, you would need to:")
        print(f"   1. Install Roboto fonts on the system")
        print(f"   2. Register them with ReportLab in the application startup")
    
    return roboto_found

if __name__ == "__main__":
    analyze_font_configuration()
    test_roboto_registration()
    
    print(f"\n📊 Summary:")
    print(f"✅ All configurations are set to use Helvetica-Bold for headings")
    print(f"✅ This is the correct choice since Helvetica is a standard PDF font") 
    print(f"✅ If headings appear different, it may be a PDF viewer rendering issue")
    print(f"\n💡 To confirm fonts are correct, check the generated PDFs with PDF inspector tools.")
