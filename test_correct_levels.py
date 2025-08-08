#!/usr/bin/env python3
"""
Test script to verify PDF heading styles are correct - using correct level numbering
"""
import sys
sys.path.insert(0, '/workspaces/StructuredDocs/backend')

from pdf_config import PDFConfig
from reportlab.lib.styles import getSampleStyleSheet

def test_heading_styles():
    """Test that heading styles are configured correctly with proper levels"""
    print("🧪 Testing PDF heading style configuration (0-based levels)...")
    
    # Get base styles
    base_styles = getSampleStyleSheet()
    
    # Test heading styles for levels 0, 1, 2 (which map to H1, H2, H3)
    expected_sizes = {
        0: 18,  # H1
        1: 16,  # H2  
        2: 13   # H3
    }
    
    for level in [0, 1, 2]:
        style = PDFConfig.create_heading_style(base_styles, level)
        print(f"\n📝 Level {level} Heading Style (H{level+1}):")
        print(f"   Font Name: {style.fontName}")
        print(f"   Font Size: {style.fontSize}")
        print(f"   Text Color: {style.textColor}")
        
        # Check if font is italic
        is_italic = 'Oblique' in style.fontName or 'Italic' in style.fontName
        if is_italic:
            print(f"   ❌ ISSUE: Font is italic! ({style.fontName})")
        else:
            print(f"   ✅ Font is NOT italic ({style.fontName})")
        
        # Check font size
        expected = expected_sizes[level]
        actual = style.fontSize
        if actual == expected:
            print(f"   ✅ Font size: {actual}pt (correct)")
        else:
            print(f"   ❌ Font size: {actual}pt (expected {expected}pt)")

if __name__ == "__main__":
    test_heading_styles()
    print(f"\n🎉 Testing complete!")
