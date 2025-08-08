#!/usr/bin/env python3
"""
Test all PDF format configurations to see which ones have the italic issue
"""
import sys
sys.path.insert(0, '/workspaces/StructuredDocs/backend')

from pdf_config import PDFConfig, CorporateConfig, AcademicConfig, CompactConfig, OrganizationConfig
from reportlab.lib.styles import getSampleStyleSheet

def test_all_configs():
    """Test heading styles across all configuration classes"""
    print("🧪 Testing heading styles across all PDF configurations...")
    
    configs = {
        'default': PDFConfig,
        'corporate': CorporateConfig,
        'academic': AcademicConfig,
        'compact': CompactConfig,
        'organization': OrganizationConfig
    }
    
    base_styles = getSampleStyleSheet()
    
    for config_name, config_class in configs.items():
        print(f"\n📋 Testing {config_name.upper()} configuration:")
        
        # Test heading levels 0, 1, 2 (H1, H2, H3)
        for level in [0, 1, 2]:
            style = config_class.create_heading_style(base_styles, level)
            
            # Check if font is italic
            is_italic = 'Oblique' in style.fontName or 'Italic' in style.fontName
            
            print(f"   Level {level} (H{level+1}): {style.fontName}, {style.fontSize}pt", end="")
            
            if is_italic:
                print(f" ❌ ITALIC!")
            else:
                print(f" ✅")

if __name__ == "__main__":
    test_all_configs()
    print(f"\n🎉 Testing complete!")
