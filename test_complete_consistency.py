#!/usr/bin/env python3
"""
Test that ALL heading-related styles use Helvetica consistently
"""
import sys
sys.path.insert(0, '/workspaces/StructuredDocs/backend')

from pdf_config import PDFConfig, CorporateConfig, AcademicConfig, CompactConfig, OrganizationConfig
from reportlab.lib.styles import getSampleStyleSheet

def test_complete_font_consistency():
    """Test that ALL heading-related styles use Helvetica"""
    print("🧪 Testing complete font consistency (title, subtitle, headings)...")
    
    configs = {
        'default': PDFConfig,
        'corporate': CorporateConfig,
        'academic': AcademicConfig,
        'compact': CompactConfig,
        'organization': OrganizationConfig
    }
    
    base_styles = getSampleStyleSheet()
    
    for config_name, config_class in configs.items():
        print(f"\n📋 {config_name.upper()} Configuration:")
        
        # Check title font
        title_style = config_class.create_title_style(base_styles)
        print(f"   Title: {title_style.fontName} ({title_style.fontSize}pt)")
        
        # Check subtitle font
        subtitle_style = config_class.create_subtitle_style(base_styles)
        print(f"   Subtitle: {subtitle_style.fontName} ({subtitle_style.fontSize}pt)")
        
        # Check heading fonts
        for level in [0, 1, 2]:
            heading_style = config_class.create_heading_style(base_styles, level)
            print(f"   H{level+1}: {heading_style.fontName} ({heading_style.fontSize}pt)")
        
        # Verify all use Helvetica
        all_fonts = [
            title_style.fontName,
            subtitle_style.fontName,
            config_class.create_heading_style(base_styles, 0).fontName,
            config_class.create_heading_style(base_styles, 1).fontName,
            config_class.create_heading_style(base_styles, 2).fontName
        ]
        
        helvetica_count = sum(1 for font in all_fonts if font.startswith('Helvetica'))
        if helvetica_count == len(all_fonts):
            print(f"   ✅ All {len(all_fonts)} heading styles use Helvetica")
        else:
            print(f"   ❌ Only {helvetica_count}/{len(all_fonts)} styles use Helvetica")

if __name__ == "__main__":
    test_complete_font_consistency()
    print(f"\n💡 All title, subtitle, and heading styles should now use Helvetica fonts.")
