#!/usr/bin/env python3

import sys
import os
import base64
import mimetypes

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Now we can import from the backend
from routes.publications import convert_image_to_base64, convert_markdown_to_html

# Mock the Flask app context since we're testing outside Flask
class MockApp:
    def __init__(self):
        self.config = {
            'STATIC_FOLDER': os.path.join(os.path.dirname(__file__), 'backend', 'static')
        }

class MockContext:
    def __enter__(self):
        import routes.publications
        routes.publications.current_app = MockApp()
        return self
    
    def __exit__(self, *args):
        pass

def test_image_conversion():
    with MockContext():
        print("Testing image base64 conversion...")
        
        # Test markdown with image
        test_markdown = """
# Test Document

This is a test with an image:

![Test Image](/images/20221123_103925_e835d817.jpg)

Some more content after the image.
"""
        
        print("Original markdown:")
        print(test_markdown)
        print("\n" + "="*50 + "\n")
        
        # Convert to HTML
        html_result = convert_markdown_to_html(test_markdown)
        
        print("Converted HTML:")
        print(html_result)
        
        # Check if base64 data is included
        if "data:image" in html_result:
            print("\n✅ SUCCESS: Image converted to base64!")
        else:
            print("\n❌ FAILED: No base64 image data found")
            
        # Test direct image path conversion
        print("\n" + "="*50 + "\n")
        print("Testing direct image path conversion...")
        
        test_path = "/images/20221123_103925_e835d817.jpg"
        base64_result = convert_image_to_base64(test_path)
        
        if base64_result.startswith("data:image"):
            print(f"✅ SUCCESS: Direct conversion worked")
            print(f"Result length: {len(base64_result)} characters")
        else:
            print(f"❌ FAILED: {base64_result}")

if __name__ == "__main__":
    test_image_conversion()
