#!/usr/bin/env python3
"""
Test the API endpoints to create a collection with description and verify the response
"""
import requests
import json

def test_create_collection_with_description():
    """Test creating a new collection with a description"""
    url = "http://localhost:5000/api/collections"
    
    # Data for new collection with description
    collection_data = {
        "name": "Test Collection with Description",
        "form_number": "TEST-DESC-001",
        "description": "This is a test collection created to verify that the description field is working properly in the API.",
        "position": 999
    }
    
    try:
        response = requests.post(url, json=collection_data, timeout=5)
        
        if response.status_code == 201:
            data = response.json()
            print("✅ Collection created successfully!")
            print(f"   ID: {data.get('id')}")
            print(f"   Name: {data.get('name')}")
            print(f"   Form Number: {data.get('form_number')}")
            print(f"   Description: {data.get('description')}")
            
            if data.get('description') == collection_data['description']:
                print("✅ Description field saved and returned correctly!")
            else:
                print("❌ Description field not returned correctly!")
        else:
            print(f"❌ Failed to create collection: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    print("🧪 Testing Collection API with description...")
    test_create_collection_with_description()
