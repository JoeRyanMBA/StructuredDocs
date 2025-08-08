#!/usr/bin/env python3
"""
Test that all PDF configurations use Helvetica for headings
"""
import sys
sys.path.insert(0, '/workspaces/StructuredDocs/backend')

from pdf_config import PDFConfig, CorporateConfig, AcademicConfig, CompactConfig, OrganizationConfig
from reportlab.lib.styles import getSampleStyleSheet

def test_all_fonts():
    """Test that all configurations use Helvetica fonts for headings"""
    print("🧪 Testing font consistency across all PDF configurations...")
    
    configs = {
        'default': PDFConfig,
        'corporate': CorporateConfig,
        'academic': AcademicConfig,
        'compact': CompactConfig,
        'organization': OrganizationConfig
    }
    
    base_styles = getSampleStyleSheet()
    
    all_consistent = True
    
    for config_name, config_class in configs.items():
        print(f"\n📋 {config_name.upper()} Configuration:")
        
        # Check title font
        title_style = config_class.create_title_style(base_styles)
        print(f"   Title font: {title_style.fontName}")
        
        # Check heading fonts for levels 0, 1, 2
        for level in [0, 1, 2]:
            heading_style = config_class.create_heading_style(base_styles, level)
            print(f"   H{level+1} font: {heading_style.fontName} ({heading_style.fontSize}pt)")
            
            # Check if it's Helvetica-based
            if not heading_style.fontName.startswith('Helvetica'):
                print(f"   ❌ NOT HELVETICA: {heading_style.fontName}")
                all_consistent = False
            else:
                print(f"   ✅ Helvetica family")
        
        # Check FONTS dictionary
        fonts = config_class.FONTS
        print(f"   Font settings: title='{fonts['title']}', heading='{fonts['heading']}'")
    
    print(f"\n🎯 Summary:")
    if all_consistent:
        print("✅ All configurations use Helvetica fonts for headings!")
    else:
        print("❌ Some configurations use non-Helvetica fonts")
    
    return all_consistent

if __name__ == "__main__":
    test_all_fonts()
    print(f"\n💡 All headings across all PDF formats should be using Helvetica fonts.")
