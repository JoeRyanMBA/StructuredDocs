#!/usr/bin/env python3

from app import app
from models import db, ImportDocument, ImportItem

print("Testing database setup...")

with app.app_context():
    # Try to create all tables
    try:
        db.create_all()
        print("✅ Database tables created/verified")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        exit(1)
    
    # Check what tables exist
    try:
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"📋 Available tables: {tables}")
        
        # Check specifically for import tables
        if 'import_documents' in tables:
            print("✅ import_documents table exists")
        else:
            print("❌ import_documents table missing")
            
        if 'import_items' in tables:
            print("✅ import_items table exists") 
        else:
            print("❌ import_items table missing")
            
    except Exception as e:
        print(f"❌ Error checking tables: {e}")
        
    # Try to create a test import document
    try:
        test_doc = ImportDocument(
            filename='test.md',
            source_type='markdown'
        )
        db.session.add(test_doc)
        db.session.commit()
        print(f"✅ Test ImportDocument created with ID: {test_doc.id}")
        
        # Clean up test data
        db.session.delete(test_doc)
        db.session.commit()
        print("✅ Test data cleaned up")
        
    except Exception as e:
        print(f"❌ Error creating test ImportDocument: {e}")
        db.session.rollback()

print("Database test completed!")import Flask, jsonify

app = Flask(__name__)

@app.route('/ping')
def ping():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    print("Starting Flask test server...")
    app.run(host='0.0.0.0', port=5000, debug=True)
