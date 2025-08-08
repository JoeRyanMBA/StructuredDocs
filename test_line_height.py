#!/usr/bin/env python3
"""
Test script to generate a PDF with long headings to verify line height fixes
"""

import requests
import json
import time

def test_line_height_fix():
    """Test that long headings wrap properly with good line spacing"""
    
    # Create test data with very long headings
    test_data = {
        "title": "Testing Line Height in PDF Generation: A Very Long Title That Should Wrap to Multiple Lines and Show Proper Spacing",
        "subtitle": "This is Also a Very Long Subtitle That Should Demonstrate Proper Line Height When It Wraps to Multiple Lines in the PDF Document",
        "topics": [
            {
                "type": "topic",
                "data": {
                    "title": "This is an Extremely Long Topic Title That Should Wrap to Multiple Lines and Test the Line Height Feature",
                    "content": "# This is a Very Long Heading 1 That Should Wrap to Multiple Lines and Show Good Line Height Spacing Between the Lines\n\n## This is Another Very Long Heading 2 That Should Also Wrap to Multiple Lines and Demonstrate Proper Line Height\n\n### And This is a Very Long Heading 3 That Will Test the Line Height Feature When Text Wraps to Multiple Lines\n\nThis is regular paragraph text to show the difference between heading line height and paragraph line height."
                }
            },
            {
                "type": "topic", 
                "data": {
                    "title": "Second Topic with Regular Title",
                    "content": "#### This is a Very Long Heading 4 That Should Wrap Properly with Good Line Height Spacing Between the Lines of Text\n\n##### This is a Very Long Heading 5 That Should Also Show Proper Line Height When It Wraps to Multiple Lines\n\n###### And This is a Very Long Heading 6 That Will Test the Line Height Feature When Text Wraps to Multiple Lines in the PDF\n\nMore regular paragraph text to fill out the document and show the difference in spacing."
                }
            }
        ]
    }
    
    print("Testing line height fixes for wrapped headings...")
    
    # Test each PDF format
    formats = ['default', 'corporate', 'academic', 'compact', 'organization']
    
    for pdf_format in formats:
        print(f"\nTesting {pdf_format} format...")
        
        try:
            # Add timestamp to avoid caching
            url = f"http://localhost:5050/api/publications/export-pdf?format={pdf_format}&t={int(time.time())}"
            
            response = requests.post(
                url,
                json=test_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                filename = f"/tmp/test_line_height_{pdf_format}.pdf"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"✓ Generated {filename}")
            else:
                print(f"✗ Failed to generate {pdf_format} PDF: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"✗ Error testing {pdf_format} format: {e}")
    
    print("\nLine height test complete!")
    print("Check the generated PDFs to verify that long headings wrap with proper spacing.")

if __name__ == "__main__":
    test_line_height_fix()
