#!/usr/bin/env python3
"""
Test script for the new form_number field in Collections
"""

import sys
import os

# Add backend to path
backend_path = os.path.join(os.getcwd(), 'backend')
sys.path.insert(0, backend_path)

from app import create_app
from models import db, Collection

def test_form_number_field():
    """Test creating a collection with the new form_number field"""
    
    app = create_app()
    
    with app.app_context():
        print("🧪 Testing form_number field functionality")
        print("=" * 50)
        
        # Test 1: Create a collection with form_number
        try:
            test_collection = Collection(
                name="Test Collection with Form Number",
                form_number="TEST-001",
                position=1
            )
            
            db.session.add(test_collection)
            db.session.commit()
            
            print("✅ Test 1 PASSED: Successfully created collection with form_number")
            print(f"   Collection ID: {test_collection.id}")
            print(f"   Name: {test_collection.name}")
            print(f"   Form Number: {test_collection.form_number}")
            
        except Exception as e:
            print(f"❌ Test 1 FAILED: {e}")
            return False
        
        # Test 2: Verify the to_dict method includes form_number
        try:
            collection_dict = test_collection.to_dict()
            
            if 'form_number' in collection_dict and collection_dict['form_number'] == 'TEST-001':
                print("✅ Test 2 PASSED: to_dict() includes form_number")
                print(f"   Dict contents: {collection_dict}")
            else:
                print(f"❌ Test 2 FAILED: form_number not in dict or incorrect value")
                print(f"   Dict contents: {collection_dict}")
                return False
                
        except Exception as e:
            print(f"❌ Test 2 FAILED: {e}")
            return False
        
        # Test 3: Test uniqueness constraint
        try:
            duplicate_collection = Collection(
                name="Duplicate Form Number Test",
                form_number="TEST-001",  # Same form number
                position=2
            )
            
            db.session.add(duplicate_collection)
            db.session.commit()
            
            print("❌ Test 3 FAILED: Should have prevented duplicate form_number")
            return False
            
        except Exception as e:
            print("✅ Test 3 PASSED: Uniqueness constraint working")
            print(f"   Error (expected): {e}")
            db.session.rollback()
        
        # Test 4: Create another collection with different form_number
        try:
            second_collection = Collection(
                name="Second Test Collection",
                form_number="TEST-002",
                position=2
            )
            
            db.session.add(second_collection)
            db.session.commit()
            
            print("✅ Test 4 PASSED: Can create collection with different form_number")
            print(f"   Form Number: {second_collection.form_number}")
            
        except Exception as e:
            print(f"❌ Test 4 FAILED: {e}")
            return False
        
        # Test 5: Query collections and verify form_number is returned
        try:
            all_collections = Collection.query.all()
            test_collections = [c for c in all_collections if c.form_number and c.form_number.startswith('TEST-')]
            
            print(f"✅ Test 5 PASSED: Found {len(test_collections)} test collections")
            for c in test_collections:
                print(f"   - {c.name} (Form: {c.form_number})")
            
        except Exception as e:
            print(f"❌ Test 5 FAILED: {e}")
            return False
        
        print("\n🎉 All tests PASSED! The form_number field is working correctly.")
        
        # Clean up test data
        try:
            for c in test_collections:
                db.session.delete(c)
            db.session.commit()
            print("🧹 Test data cleaned up")
        except Exception as e:
            print(f"⚠️ Failed to clean up test data: {e}")
        
        return True

def main():
    print("🚀 Starting Collection form_number field tests")
    print()
    
    success = test_form_number_field()
    
    if success:
        print("\n✅ ALL TESTS PASSED!")
        print("The Collection form_number field is ready for use.")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()
