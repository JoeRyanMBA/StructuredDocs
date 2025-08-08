#!/usr/bin/env python3
"""
Test script to verify that our collection description and publication topics_count fixes work
"""
import sys
import os
sys.path.insert(0, '/workspaces/StructuredDocs/backend')

from models import db, Collection, Publication
from app import create_app

def test_collection_description():
    """Test that Collection model includes description field"""
    app = create_app()
    with app.app_context():
        # Test that a collection's to_dict includes description
        collections = Collection.query.limit(1).all()
        if collections:
            collection = collections[0]
            data = collection.to_dict()
            print("✅ Collection to_dict() includes:")
            for key in sorted(data.keys()):
                print(f"  - {key}: {data[key]}")
            
            if 'description' in data:
                print("✅ Collection description field is present!")
            else:
                print("❌ Collection description field is missing!")
        else:
            print("⚠️  No collections found in database")

def test_publication_topics_count():
    """Test that Publication model includes topics_count field"""
    app = create_app()
    with app.app_context():
        # Test that a publication's to_dict includes topics_count
        publications = Publication.query.limit(1).all()
        if publications:
            publication = publications[0]
            data = publication.to_dict()
            print("\n✅ Publication to_dict() includes:")
            for key in sorted(data.keys()):
                print(f"  - {key}: {data[key]}")
            
            if 'topics_count' in data:
                print("✅ Publication topics_count field is present!")
            else:
                print("❌ Publication topics_count field is missing!")
        else:
            print("⚠️  No publications found in database")

if __name__ == "__main__":
    print("🧪 Testing Collection and Publication model changes...")
    test_collection_description()
    test_publication_topics_count()
    print("\n🎉 Testing complete!")
