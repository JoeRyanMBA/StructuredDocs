#!/usr/bin/env python3
"""
Hex Color Examples for PDF Configuration
Demonstrates how to use hex colors in your organization's PDF formatting
"""

from backend.pdf_config import hex_to_color, PDFConfig

# Example 1: Common Brand Color Palettes
class BrandExamples:
    """Examples of common brand color schemes"""
    
    # Tech Company (Blue-based)
    TECH_COLORS = {
        'primary': hex_to_color('#1DA1F2'),      # Twitter Blue
        'secondary': hex_to_color('#14171A'),    # Dark Gray
        'accent': hex_to_color('#1991DA'),       # Light Blue
        'success': hex_to_color('#17BF63'),      # Green
        'warning': hex_to_color('#FFAD1F'),      # Orange
        'text': hex_to_color('#14171A'),         # Dark Text
    }
    
    # Corporate (Navy/Gold)
    CORPORATE_COLORS = {
        'primary': hex_to_color('#003366'),      # Navy Blue
        'secondary': hex_to_color('#FFD700'),    # Gold
        'accent': hex_to_color('#CC9900'),       # Dark Gold
        'text': hex_to_color('#333333'),         # Dark Gray
        'light_bg': hex_to_color('#F8F9FA'),     # Light Background
    }
    
    # Healthcare (Green/Blue)
    HEALTHCARE_COLORS = {
        'primary': hex_to_color('#00A651'),      # Medical Green
        'secondary': hex_to_color('#0077BE'),    # Medical Blue
        'accent': hex_to_color('#8CC8FF'),       # Light Blue
        'text': hex_to_color('#2C3E50'),         # Professional Gray
        'highlight': hex_to_color('#E8F5E8'),    # Light Green Background
    }
    
    # Financial (Dark Blue/Gray)
    FINANCIAL_COLORS = {
        'primary': hex_to_color('#1E3A8A'),      # Professional Blue
        'secondary': hex_to_color('#64748B'),    # Slate Gray
        'accent': hex_to_color('#0EA5E9'),       # Sky Blue
        'success': hex_to_color('#059669'),      # Emerald
        'text': hex_to_color('#1F2937'),         # Nearly Black
    }


# Example 2: Creating a Custom Config with Your Brand Colors
class MyOrganizationConfig(PDFConfig):
    """Replace these with your actual organization's hex colors"""
    
    COLORS = {
        # Replace these hex values with your brand colors
        'primary': hex_to_color('#112e51'),      # e.g., '#1E3A8A'
        'secondary': hex_to_color('#FF5622'),  # e.g., '#059669'
        'accent': hex_to_color('#008392'),        # e.g., '#DC2626'
        
        # Functional colors
        'text': hex_to_color('#4B636E'),                     # Dark gray for readability
        'heading': hex_to_color('#333333'),                  # Nearly black for headings
        'subheading': hex_to_color('#78909C'),               # Medium gray

        # Background colors
        'light_bg': hex_to_color('#F9FAFB'),                 # Very light gray
        'highlight': hex_to_color('#FEF3C7'),                # Yellow highlight
        'border': hex_to_color('#D1D5DB'),                   # Border gray
    }


# Example 3: Color Usage in Styles
def create_branded_styles(color_palette):
    """Example of how to use hex colors in paragraph styles"""
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
    
    styles = getSampleStyleSheet()
    
    # Title with primary brand color
    title_style = ParagraphStyle(
        'BrandedTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=color_palette['primary'],  # Your brand color
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    # Heading with secondary color
    heading_style = ParagraphStyle(
        'BrandedHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=color_palette['secondary'],  # Your secondary color
        spaceBefore=20,
        spaceAfter=12
    )
    
    # Body text with readable dark color
    body_style = ParagraphStyle(
        'BrandedBody',
        parent=styles['Normal'],
        fontSize=11,
        textColor=color_palette['text'],
        alignment=TA_JUSTIFY,
        spaceAfter=12
    )
    
    return {
        'title': title_style,
        'heading': heading_style,
        'body': body_style
    }


# Example 4: How to test hex colors
def test_hex_colors():
    """Test that hex colors are working correctly"""
    
    # Test various hex formats
    test_colors = [
        '#FF5733',    # With hash
        'FF5733',     # Without hash
        '#ff5733',    # Lowercase
        '#F57C00',    # Mixed case
    ]
    
    print("🎨 Testing Hex Color Conversion")
    print("=" * 40)
    
    for hex_color in test_colors:
        color_obj = hex_to_color(hex_color)
        rgb_values = (color_obj.red, color_obj.green, color_obj.blue)
        print(f"Hex: {hex_color:>8} → RGB: {rgb_values}")
    
    print("\n✅ All hex colors converted successfully!")


# Example 5: Popular Color Palette Generators
def color_palette_resources():
    """Resources for finding good color palettes"""
    
    resources = {
        "Color Palette Generators": [
            "coolors.co - Generate color palettes",
            "paletton.com - Color scheme designer", 
            "colorhunt.co - Curated color palettes",
            "material.io/design/color - Material Design colors"
        ],
        
        "Brand Color Tools": [
            "brandcolors.net - Famous brand colors",
            "colourlovers.com - Community color palettes",
            "adobe.com/products/color.html - Adobe Color"
        ],
        
        "Accessibility Tools": [
            "webaim.org/resources/contrastchecker - Contrast checker",
            "colorbrewer2.org - Colorblind-safe palettes"
        ]
    }
    
    print("🎨 Color Palette Resources")
    print("=" * 40)
    
    for category, tools in resources.items():
        print(f"\n📁 {category}:")
        for tool in tools:
            print(f"   • {tool}")


if __name__ == "__main__":
    print("🎨 Hex Color Examples for PDF Configuration")
    print("=" * 50)
    
    # Test hex color conversion
    test_hex_colors()
    
    print("\n")
    
    # Show resources
    color_palette_resources()
    
    print("\n📝 Next Steps:")
    print("1. Choose your organization's hex colors")
    print("2. Update OrganizationConfig in pdf_config.py")
    print("3. Test with: python test_pdf_formats.py 3")
    print("4. Use format: /api/publications/3/export/pdf?format=organization")
