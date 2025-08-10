#!/usr/bin/env python3
"""
Test the actual upload endpoint to see if it works correctly
"""

import requests
import os

def test_upload_endpoint():
    """Test the actual /api/import/upload endpoint"""
    print("🧪 Testing the actual upload endpoint...")
    
    # Test with our markdown file
    test_file_path = '/workspaces/StructuredDocs/test_import_document.md'
    
    if not os.path.exists(test_file_path):
        print(f"❌ Test file not found: {test_file_path}")
        return
    
    # Upload to the actual endpoint
    url = 'http://localhost:5050/api/import/upload'
    
    try:
        with open(test_file_path, 'rb') as f:
            files = {'file': ('test_import_document.md', f, 'text/markdown')}
            data = {'source': 'markdown'}
            
            print(f"📤 Uploading to {url}...")
            response = requests.post(url, files=files, data=data)
            
        print(f"📊 Response status: {response.status_code}")
        print(f"📋 Response headers: {dict(response.headers)}")
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Upload successful!")
            print(f"📝 Import ID: {result.get('id')}")
            print(f"📝 Filename: {result.get('filename')}")
            print(f"📝 Status: {result.get('status')}")
            print(f"📝 Items count: {len(result.get('items', []))}")
            
            if result.get('items'):
                print("\n📋 Import items found:")
                for i, item in enumerate(result['items']):
                    print(f"  {i+1}. {item.get('title')} ({len(item.get('content', ''))} chars)")
            else:
                print("⚠️  No import items found!")
            
            return result.get('id')
        else:
            print(f"❌ Upload failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None

def test_word_upload():
    """Test uploading the Word document"""
    print("\n🧪 Testing Word document upload...")
    
    word_file_path = '/workspaces/StructuredDocs/backend/static/SC-50, Special Census Office Manual.docx'
    
    if not os.path.exists(word_file_path):
        print(f"❌ Word file not found: {word_file_path}")
        return
    
    url = 'http://localhost:5050/api/import/upload'
    
    try:
        with open(word_file_path, 'rb') as f:
            files = {'file': ('test_census_manual.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            data = {'source': 'word'}
            
            print(f"📤 Uploading Word document to {url}...")
            response = requests.post(url, files=files, data=data)
            
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Word upload successful!")
            print(f"📝 Import ID: {result.get('id')}")
            print(f"📝 Filename: {result.get('filename')}")
            print(f"📝 Status: {result.get('status')}")
            print(f"📝 Items count: {len(result.get('items', []))}")
            
            if result.get('items'):
                print(f"\n📋 Found {len(result['items'])} import items:")
                for i, item in enumerate(result['items'][:5]):  # Show first 5
                    print(f"  {i+1}. {item.get('title')} ({len(item.get('content', ''))} chars)")
                if len(result['items']) > 5:
                    print(f"  ... and {len(result['items']) - 5} more items")
            else:
                print("⚠️  No import items found!")
            
            return result.get('id')
        else:
            print(f"❌ Word upload failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Word request failed: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Testing Upload Endpoints")
    print("=" * 50)
    
    # Test markdown upload
    markdown_id = test_upload_endpoint()
    
    # Test Word upload
    word_id = test_word_upload()
    
    print("\n" + "=" * 50)
    print("📊 Upload Test Summary:")
    print(f"  Markdown Upload: {'✅ SUCCESS' if markdown_id else '❌ FAILED'} (ID: {markdown_id})")
    print(f"  Word Upload:     {'✅ SUCCESS' if word_id else '❌ FAILED'} (ID: {word_id})")
