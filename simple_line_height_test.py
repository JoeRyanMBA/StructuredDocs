#!/usr/bin/env python3
"""
Simple test script to generate a PDF with long headings for line height testing
"""

import requests
import json

def test_line_height():
    """Test line height with a simple long heading"""
    
    data = {
        "title": "Testing Line Height for Wrapped Headings: A Very Long Title That Should Wrap to Multiple Lines",
        "subtitle": "This is a Long Subtitle That Should Also Wrap and Show Proper Line Height",
        "topics": [
            {
                "type": "topic",
                "data": {
                    "title": "Topic with Long Heading Test",
                    "content": "# This is a Very Long Heading 1 That Should Wrap to Multiple Lines and Show Good Line Height Spacing\n\nThis is some regular text content to compare spacing."
                }
            }
        ]
    }
    
    try:
        response = requests.post(
            "http://localhost:5050/api/publications/export-pdf?format=default",
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            with open('/tmp/line_height_test.pdf', 'wb') as f:
                f.write(response.content)
            print("✓ Generated /tmp/line_height_test.pdf")
            print("Check the PDF to verify long headings wrap with proper line spacing.")
        else:
            print(f"✗ Failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    test_line_height()
