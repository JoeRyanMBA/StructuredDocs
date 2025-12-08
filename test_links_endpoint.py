#!/usr/bin/env python3
"""Test script to verify imported links are accessible via API"""

import requests
import json

def test_links_endpoint():
    """Test the links endpoint to see all available links"""
    
    BASE_URL = "http://localhost:5000"
    
    print("🔗 Testing Links Endpoint")
    print("=" * 50)
    
    try:
        # Test 1: Get all links
        print("\n1. Fetching all links...")
        response = requests.get(f"{BASE_URL}/api/links?include_usage=true")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"   Total links: {data.get('total_count', 0)}")
            print(f"   Regular links: {data.get('regular_links_count', 0)}")
            print(f"   Imported links: {data.get('imported_links_count', 0)}")
            
            # Show first few imported links
            links = data.get('links', [])
            imported = [l for l in links if l.get('source') == 'import']
            
            if imported:
                print(f"\n📋 First {min(3, len(imported))} imported links:")
                for i, link in enumerate(imported[:3]):
                    print(f"   {i+1}. [{link.get('title')}]({link.get('url')})")
                    print(f"      Type: {link.get('link_type')}")
                    print(f"      Document ID: {link.get('document_id')}")
            else:
                print("\n⚠️  No imported links found")
        else:
            print(f"❌ Status: {response.status_code}")
            print(f"   Response: {response.text}")
        
        # Test 2: Get import history
        print("\n2. Fetching import history...")
        response = requests.get(f"{BASE_URL}/api/import/history")
        
        if response.status_code == 200:
            imports = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"   Total imports: {len(imports)}")
            
            for imp in imports[:3]:
                print(f"   - {imp['filename']} (ID: {imp['id']})")
                
                # Get links for this import
                links_response = requests.get(f"{BASE_URL}/api/import/staging/{imp['id']}/links")
                if links_response.status_code == 200:
                    links_data = links_response.json()
                    print(f"     Links extracted: {links_data.get('total_count', 0)}")
        else:
            print(f"❌ Status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_links_endpoint()
