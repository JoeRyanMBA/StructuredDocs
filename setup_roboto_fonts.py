#!/usr/bin/env python3
"""
Example script showing how to add Roboto font support to ReportLab
This is optional - your current Helvetica configuration is working correctly
"""

def setup_roboto_fonts():
    """Set up Roboto fonts for ReportLab if available"""
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.fonts import addMapping
    import os
    
    # Download and install Roboto fonts
    roboto_urls = {
        'Roboto-Regular.ttf': 'https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Regular.ttf',
        'Roboto-Bold.ttf': 'https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Bold.ttf',
        'Roboto-Italic.ttf': 'https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Italic.ttf',
        'Roboto-BoldItalic.ttf': 'https://github.com/google/fonts/raw/main/apache/roboto/Roboto-BoldItalic.ttf'
    }
    
    fonts_dir = '/workspaces/StructuredDocs/fonts'
    os.makedirs(fonts_dir, exist_ok=True)
    
    print("📥 Downloading Roboto fonts...")
    
    import urllib.request
    
    for filename, url in roboto_urls.items():
        font_path = os.path.join(fonts_dir, filename)
        if not os.path.exists(font_path):
            try:
                print(f"  Downloading {filename}...")
                urllib.request.urlretrieve(url, font_path)
                print(f"  ✅ {filename} downloaded")
            except Exception as e:
                print(f"  ❌ Failed to download {filename}: {e}")
                return False
        else:
            print(f"  ✅ {filename} already exists")
    
    # Register fonts with ReportLab
    print("\n🔧 Registering Roboto fonts with ReportLab...")
    
    try:
        # Register the font files
        pdfmetrics.registerFont(TTFont('Roboto-Regular', os.path.join(fonts_dir, 'Roboto-Regular.ttf')))
        pdfmetrics.registerFont(TTFont('Roboto-Bold', os.path.join(fonts_dir, 'Roboto-Bold.ttf')))
        pdfmetrics.registerFont(TTFont('Roboto-Italic', os.path.join(fonts_dir, 'Roboto-Italic.ttf')))
        pdfmetrics.registerFont(TTFont('Roboto-BoldItalic', os.path.join(fonts_dir, 'Roboto-BoldItalic.ttf')))
        
        # Add font family mappings
        addMapping('Roboto', 0, 0, 'Roboto-Regular')    # Normal
        addMapping('Roboto', 1, 0, 'Roboto-Bold')       # Bold
        addMapping('Roboto', 0, 1, 'Roboto-Italic')     # Italic
        addMapping('Roboto', 1, 1, 'Roboto-BoldItalic') # Bold + Italic
        
        print("✅ Roboto fonts registered successfully!")
        
        # Test the fonts
        from reportlab.platypus import SimpleDocTemplate, Paragraph
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.pagesizes import A4
        
        doc = SimpleDocTemplate("/tmp/roboto_test.pdf", pagesize=A4)
        story = []
        
        roboto_style = ParagraphStyle(
            'RobotoTest',
            fontName='Roboto-Bold',
            fontSize=18
        )
        
        story.append(Paragraph("This text uses Roboto-Bold font!", roboto_style))
        doc.build(story)
        
        print("✅ Roboto test PDF created: /tmp/roboto_test.pdf")
        return True
        
    except Exception as e:
        print(f"❌ Failed to register Roboto fonts: {e}")
        return False

def update_config_for_roboto():
    """Show how to update pdf_config.py to use Roboto fonts"""
    
    config_update = '''
# Updated FONTS configuration to use Roboto
FONTS = {
    'title': 'Roboto-Bold',
    'heading': 'Roboto-Bold', 
    'body': 'Roboto-Regular',  # or keep Times-Roman
    'caption': 'Roboto-Italic',
    'code': 'Courier'  # Keep monospace font for code
}
'''
    
    print("\n📝 To use Roboto in your PDFs, update pdf_config.py:")
    print(config_update)
    
    startup_code = '''
# Add this to your app.py startup code:
from setup_roboto_fonts import setup_roboto_fonts
setup_roboto_fonts()  # Register Roboto fonts when app starts
'''
    
    print("📝 And add this to your backend/app.py startup:")
    print(startup_code)

if __name__ == "__main__":
    print("🎨 Roboto Font Setup for ReportLab")
    print("=" * 50)
    print("⚠️  NOTE: Your current Helvetica configuration is working correctly!")
    print("   This script is only needed if you specifically want to use Roboto.")
    print()
    
    setup_success = setup_roboto_fonts()
    
    if setup_success:
        update_config_for_roboto()
        print("\n✅ Roboto fonts are now available for use in PDFs!")
    else:
        print("\n❌ Roboto font setup failed.")
        print("💡 Continue using Helvetica - it's a professional choice!")
