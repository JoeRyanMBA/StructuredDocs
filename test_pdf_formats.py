#!/usr/bin/env python3
"""
PDF Format Testing Script
Test different PDF formatting configurations for your publications
"""

import requests
import sys
import os

# Configuration
BASE_URL = "http://localhost:5050"
FORMATS = ['default', 'corporate', 'academic', 'compact', 'organization']

def test_pdf_formats(publication_id):
    """Test all PDF format configurations for a publication"""
    
    print(f"🔍 Testing PDF formats for publication {publication_id}")
    print("=" * 50)
    
    for format_type in FORMATS:
        print(f"\n📄 Testing format: {format_type}")
        
        # Test URL
        url = f"{BASE_URL}/api/publications/{publication_id}/export/pdf?format={format_type}"
        
        try:
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                # Save PDF file
                filename = f"test_publication_{publication_id}_{format_type}.pdf"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                
                file_size = len(response.content)
                print(f"   ✅ Success: {filename} ({file_size:,} bytes)")
                
            else:
                print(f"   ❌ Error {response.status_code}: {response.text[:200]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Connection error: {e}")
    
    print(f"\n📁 PDF files saved in current directory")

def list_publications():
    """List available publications"""
    try:
        response = requests.get(f"{BASE_URL}/api/publications")
        if response.status_code == 200:
            publications = response.json()
            print("📚 Available Publications:")
            print("-" * 30)
            for pub in publications[:10]:  # Show first 10
                print(f"   ID: {pub['id']} - {pub['title']}")
            return publications
        else:
            print(f"❌ Error fetching publications: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return []

def main():
    """Main function"""
    print("📄 PDF Format Testing Tool")
    print("==========================")
    
    # Check if publication ID is provided
    if len(sys.argv) > 1:
        try:
            pub_id = int(sys.argv[1])
            test_pdf_formats(pub_id)
        except ValueError:
            print("❌ Invalid publication ID. Please provide a number.")
            sys.exit(1)
    else:
        # List available publications
        publications = list_publications()
        
        if publications:
            print(f"\n💡 Usage: python {sys.argv[0]} <publication_id>")
            print(f"   Example: python {sys.argv[0]} {publications[0]['id']}")
        else:
            print("❌ No publications found or server not running.")
            print("💡 Make sure your Flask server is running on http://localhost:5050")

if __name__ == "__main__":
    main()
