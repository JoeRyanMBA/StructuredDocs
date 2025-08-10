#!/usr/bin/env python3
"""
Test the review endpoint to see what the frontend sees
"""

import requests

def test_review_endpoint(import_id):
    """Test the staging/{id} endpoint that the frontend uses"""
    print(f"🧪 Testing review endpoint for import ID {import_id}...")
    
    url = f'http://localhost:5050/api/import/staging/{import_id}'
    
    try:
        response = requests.get(url)
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Review endpoint successful!")
            print(f"📝 Import ID: {result.get('id')}")
            print(f"📝 Filename: {result.get('filename')}")
            print(f"📝 Status: {result.get('status')}")
            print(f"📝 Review Step: {result.get('review_step')}")
            print(f"📝 Items count: {len(result.get('items', []))}")
            
            if result.get('items'):
                print(f"\n📋 Found {len(result['items'])} import items:")
                for i, item in enumerate(result['items'][:5]):  # Show first 5
                    print(f"  {i+1}. {item.get('title')} ({len(item.get('content', ''))} chars)")
                if len(result['items']) > 5:
                    print(f"  ... and {len(result['items']) - 5} more items")
            else:
                print("⚠️  No import items found in review!")
                print("\nThis is the 'No content items found' issue!")
            
            return result
        else:
            print(f"❌ Review endpoint failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Testing Review Endpoints")
    print("=" * 50)
    
    # Test the markdown import we just created (ID 7)
    print("Testing Markdown Import (ID 7):")
    markdown_result = test_review_endpoint(7)
    
    print("\n" + "-" * 30)
    
    # Test the Word import we just created (ID 8)  
    print("Testing Word Import (ID 8):")
    word_result = test_review_endpoint(8)
    
    print("\n" + "=" * 50)
    print("📊 Review Test Summary:")
    print(f"  Markdown Review: {'✅ SUCCESS' if markdown_result else '❌ FAILED'}")
    print(f"  Word Review:     {'✅ SUCCESS' if word_result else '❌ FAILED'}")
    
    if markdown_result and len(markdown_result.get('items', [])) == 0:
        print("⚠️  Markdown shows no items in review - this is the bug!")
    if word_result and len(word_result.get('items', [])) == 0:
        print("⚠️  Word shows no items in review - this is the bug!")
