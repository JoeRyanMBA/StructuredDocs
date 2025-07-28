#!/usr/bin/env python3
print("Starting database test...")

try:
    import sys
    import os
    print("Imports successful")
    
    # Add backend to path
    backend_path = os.path.join(os.path.dirname(__file__), 'backend')
    sys.path.append(backend_path)
    print(f"Added {backend_path} to path")
    
    # Import Flask app and models
    from backend.app import app
    print("Imported app")
    
    from backend.models import db, ImportDocument
    print("Imported models")
    
    # Test with app context
    with app.app_context():
        print("Created app context")
        
        # Check database tables
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Available tables: {tables}")
        
        # Check if import_documents table exists
        if 'import_documents' in tables:
            print("import_documents table exists")
            
            # Try to query all import documents
            import_docs = ImportDocument.query.all()
            print(f"Found {len(import_docs)} import documents")
            
            for doc in import_docs:
                print(f"  - {doc.filename} (status: {doc.status})")
                
        else:
            print("import_documents table does NOT exist")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
