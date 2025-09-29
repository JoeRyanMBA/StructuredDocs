#!/usr/bin/env python3
"""
Test the hierarchical import functionality with the backend
"""

import requests
import json
import io
import os

# Test the hierarchical import API endpoint
def test_hierarchical_import():
    # Read our test markdown document
    with open('/workspaces/StructuredDocs/test_employee_handbook.md', 'r') as f:
        content = f.read()
    
    print("=== Testing Hierarchical Import API ===")
    print(f"Document content length: {len(content)} characters")
    print(f"Document has {content.count('# ')} H1 headings")
    print(f"Document has {content.count('## ')} H2 headings") 
    print(f"Document has {content.count('### ')} H3 headings")
    print()
    
    # Create a file-like object for the test
    file_content = content.encode('utf-8')
    
    # Prepare the form data as if coming from the frontend
    files = {'file': ('test_employee_handbook.md', file_content, 'text/markdown')}
    data = {
        'source': 'markdown',
        'import_type': 'topics',
        'preserve_hierarchy': 'true'
    }
    
    print("Making request to backend...")
    print(f"Data: {data}")
    
    # Make the request to the backend
    try:
        response = requests.post('http://localhost:5000/api/import/upload', files=files, data=data)
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200 or response.status_code == 201:
            try:
                result = response.json()
                print("SUCCESS! Response:")
                print(json.dumps(result, indent=2))
                
                # Check if it created a collection
                if 'id' in result:
                    print(f"\n✅ Collection created with ID: {result['id']}")
                    if 'topics_count' in result:
                        print(f"✅ Created {result['topics_count']} topics")
                    if 'message' in result:
                        print(f"✅ Message: {result['message']}")
                else:
                    print("⚠️  No collection ID found in response")
                    
            except json.JSONDecodeError:
                print("Response is not JSON:")
                print(response.text)
        else:
            print(f"ERROR: {response.status_code}")
            print("Response text:")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend server at http://localhost:5000")
        print("Make sure the Flask backend is running with:")
        print("cd /workspaces/StructuredDocs && python backend/app.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_hierarchical_import()