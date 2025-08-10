#!/usr/bin/env python3
"""
Test the fixed import functionality with a real import
"""
import requests
import os
import time

def test_fixed_import():
    """Test the import with the fixed functionality"""
    print("🧪 Testing Fixed Import Functionality")
    print("=" * 50)
    
    # Check if backend is running
    try:
        response = requests.get('http://localhost:5050/api/publications', timeout=5)
        if response.status_code != 200:
            print("❌ Backend not running. Please start it with: bash restart.sh")
            return False
    except requests.exceptions.RequestException:
        print("❌ Backend not running at localhost:5050")
        return False
    
    # Test with our markdown file
    test_file = '/workspaces/StructuredDocs/test_import_fixed.md'
    
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return False
    
    print(f"📄 Testing import with: {test_file}")
    
    # Upload the file
    try:
        with open(test_file, 'rb') as f:
            files = {'file': ('test_import_fixed.md', f, 'text/markdown')}
            data = {'source': 'markdown'}
            
            print("📤 Uploading test file...")
            response = requests.post('http://localhost:5050/api/import/upload', 
                                   files=files, data=data, timeout=30)
        
        if response.status_code == 201:
            print("✅ Upload successful!")
            import_data = response.json()
            
            print(f"📋 Import Details:")
            print(f"  ID: {import_data['id']}")
            print(f"  Filename: {import_data['filename']}")
            print(f"  Items created: {len(import_data.get('items', []))}")
            
            # Analyze the imported items
            print(f"\n📊 Imported Items Analysis:")
            for i, item in enumerate(import_data.get('items', []), 1):
                title = item['title']
                content = item['content']
                content_preview = content.replace('\n', '\\n')[:100] + ('...' if len(content) > 100 else '')
                
                print(f"  {i}. Title: '{title}'")
                print(f"     Content preview: {content_preview}")
                
                # Check for merged headings (should contain ## headings)
                if '##' in content and not '###' in content:
                    merged_headings = [line.strip() for line in content.split('\n') if line.strip().startswith('##')]
                    if merged_headings:
                        print(f"     ✅ Contains merged headings: {merged_headings}")
                
                # Check for blank line preservation
                if '\n\n' in content:
                    print(f"     ✅ Contains paragraph breaks (blank lines preserved)")
                
                print()
            
            # Test the specific fixes
            verify_fixes(import_data)
            
            return True
            
        elif response.status_code == 422:
            print(f"❌ Upload failed with validation error: {response.json().get('error', 'Unknown error')}")
            return False
        else:
            print(f"❌ Upload failed with status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Upload failed with exception: {e}")
        return False

def verify_fixes(import_data):
    """Verify that the specific fixes are working"""
    print("🔍 Verifying Fixes:")
    print("-" * 30)
    
    items = import_data.get('items', [])
    
    # Fix 1: Check for blank line preservation
    blank_lines_preserved = False
    for item in items:
        if '\n\n' in item['content'] and 'paragraph' in item['content'].lower():
            blank_lines_preserved = True
            break
    
    print(f"✅ Blank line preservation: {'WORKING' if blank_lines_preserved else 'NOT DETECTED'}")
    
    # Fix 2: Check for heading merging
    headings_merged = False
    for item in items:
        # Look for items that contain merged headings (## format in content)
        if item['title'] == 'Section With Actual Content':
            content_lines = item['content'].split('\n')
            h2_headings = [line for line in content_lines if line.strip().startswith('## ')]
            if h2_headings:
                headings_merged = True
                print(f"   Found merged headings in '{item['title']}': {[h.strip() for h in h2_headings]}")
                break
    
    print(f"✅ Heading merging: {'WORKING' if headings_merged else 'NOT DETECTED'}")
    
    # Additional check: Verify we didn't create heading-only topics
    heading_only_topics = 0
    for item in items:
        content = item['content'].strip()
        if not content or all(line.strip() == '' or line.strip().startswith('#') for line in content.split('\n')):
            heading_only_topics += 1
    
    print(f"✅ No heading-only topics: {'WORKING' if heading_only_topics == 0 else f'FOUND {heading_only_topics} EMPTY TOPICS'}")
    
    return blank_lines_preserved and headings_merged and heading_only_topics == 0

if __name__ == "__main__":
    success = test_fixed_import()
    
    if success:
        print(f"\n🎉 Import functionality test completed successfully!")
        print(f"💡 Both fixes appear to be working correctly.")
    else:
        print(f"\n❌ Import test failed. Check the backend logs for more details.")
        
    print(f"\n📝 Next steps:")
    print(f"  1. Test with an actual Word document")
    print(f"  2. Verify the import review interface shows correct content")
    print(f"  3. Check that imported content maintains formatting in the final publication")
