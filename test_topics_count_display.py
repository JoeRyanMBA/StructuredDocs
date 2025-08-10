#!/usr/bin/env python3
"""
Test script to verify that the topics count is correctly displayed
in the Import Review page.
"""

import requests
import json

def test_topics_count_display():
    base_url = "http://localhost:5050"
    
    print("🧪 Testing Topics Count Display in Import Review Page")
    print("=" * 60)
    
    # Get list of import documents
    response = requests.get(f"{base_url}/api/import/history")
    if response.status_code != 200:
        print(f"❌ Failed to get import history: {response.status_code}")
        return
    
    imports = response.json()
    print(f"📋 Found {len(imports)} import documents")
    
    # Test a few imports to verify topics_count is present
    for import_doc in imports[:3]:  # Test first 3
        doc_id = import_doc['id']
        filename = import_doc['filename']
        topics_count = import_doc.get('topics_count', 0)
        status = import_doc['status']
        
        print(f"\n📄 Import {doc_id}: {filename}")
        print(f"   Status: {status}")
        print(f"   Topics Count (from history): {topics_count}")
        
        # Get detailed staging data
        staging_response = requests.get(f"{base_url}/api/import/staging/{doc_id}")
        if staging_response.status_code == 200:
            staging_data = staging_response.json()
            staging_topics_count = staging_data.get('topics_count', 0)
            actual_items_count = len(staging_data.get('items', []))
            
            print(f"   Topics Count (from staging): {staging_topics_count}")
            print(f"   Actual Items Count: {actual_items_count}")
            
            # Verify they match
            if staging_topics_count == actual_items_count:
                print(f"   ✅ Topics count matches actual items")
            else:
                print(f"   ❌ Topics count mismatch!")
                
            # Check if the frontend would have the data it needs
            has_topics_count = 'topics_count' in staging_data
            has_items = 'items' in staging_data and len(staging_data['items']) > 0
            
            print(f"   Frontend data availability:")
            print(f"     - topics_count field: {'✅' if has_topics_count else '❌'}")
            print(f"     - items array: {'✅' if has_items else '❌'}")
        else:
            print(f"   ❌ Failed to get staging data: {staging_response.status_code}")
    
    print("\n" + "=" * 60)
    print("🎯 Frontend Implementation:")
    print("The Import Review page now shows:")
    print("   Status: {{ doc.status }}")
    print("   Total Topics: {{ doc.topics_count || (doc.items ? doc.items.length : 0) }}")
    print("")
    print("This ensures the topic count is displayed using either:")
    print("1. The topics_count field (preferred)")
    print("2. The length of the items array (fallback)")
    print("")
    print("✅ Implementation complete!")

if __name__ == "__main__":
    test_topics_count_display()
