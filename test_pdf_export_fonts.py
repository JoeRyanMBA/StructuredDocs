#!/usr/bin/env python3
"""
Test the actual font rendering in a real PDF export to see if Helvetica is being used
"""
import sys
sys.path.insert(0, '/workspaces/StructuredDocs/backend')

import requests
import os

def test_pdf_export_fonts():
    """Test PDF export to see actual fonts used"""
    print("🔨 Testing PDF export fonts...")
    
    # Test if backend is running
    try:
        response = requests.get('http://localhost:5050/api/publications', timeout=5)
        if response.status_code != 200:
            print("❌ Backend not running. Starting it...")
            return False
    except requests.exceptions.RequestException:
        print("❌ Backend not running at localhost:5050")
        print("💡 Start the backend with: cd /workspaces/StructuredDocs && python3 backend/app.py")
        return False
    
    # Get list of publications
    try:
        pubs_response = requests.get('http://localhost:5050/api/publications')
        publications = pubs_response.json()
        
        if not publications:
            print("❌ No publications found in database")
            return False
            
        # Use the first publication
        pub_id = publications[0]['id']
        pub_title = publications[0]['title']
        
        print(f"📄 Testing PDF export for publication: {pub_title} (ID: {pub_id})")
        
        # Test different formats
        formats = ['default', 'corporate', 'academic', 'compact', 'organization']
        
        for format_name in formats:
            print(f"  📋 Testing {format_name} format...")
            
            pdf_url = f'http://localhost:5050/api/publications/{pub_id}/export/pdf?format={format_name}'
            pdf_response = requests.get(pdf_url)
            
            if pdf_response.status_code == 200:
                # Save PDF for inspection
                pdf_filename = f'/tmp/test_fonts_{format_name}.pdf'
                with open(pdf_filename, 'wb') as f:
                    f.write(pdf_response.content)
                print(f"    ✅ {format_name}: {len(pdf_response.content)} bytes -> {pdf_filename}")
            else:
                print(f"    ❌ {format_name}: Error {pdf_response.status_code}")
                if pdf_response.headers.get('content-type', '').startswith('text/html'):
                    print(f"       Error: {pdf_response.text[:200]}...")
        
        print(f"\n📋 Generated test PDFs in /tmp/")
        print(f"💡 Open these PDFs and inspect the font properties of headings to verify Helvetica usage.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    success = test_pdf_export_fonts()
    if success:
        print(f"\n🎉 PDF export test completed!")
        print(f"📋 Check the generated PDFs in /tmp/ to verify heading fonts.")
    else:
        print(f"\n❌ PDF export test failed. Make sure the backend is running.")
