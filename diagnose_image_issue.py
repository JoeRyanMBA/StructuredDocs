#!/usr/bin/env python3
"""
Diagnose why images show as placeholders in Document Builder.
Check database records vs actual files on disk.
"""
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, '/workspaces/StructuredDocs')
sys.path.insert(0, '/workspaces/StructuredDocs/backend')

from backend import create_app
from backend.models import ImportImage, ImportDocument

# Create app context
app = create_app()

with app.app_context():
    from backend.extensions import db
    
    # Get all import images
    all_images = ImportImage.query.all()
    print(f"\n📊 Total ImportImage records in database: {len(all_images)}")
    
    # Group by document_id
    by_doc = {}
    for img in all_images:
        if img.document_id not in by_doc:
            by_doc[img.document_id] = []
        by_doc[img.document_id].append(img)
    
    print(f"\n📂 Images by document ID:")
    for doc_id in sorted(by_doc.keys()):
        print(f"\n  Doc {doc_id}: {len(by_doc[doc_id])} images")
        
        # Check if files exist
        backend_dir = Path(app.root_path) / 'static' / 'images' / 'imports' / str(doc_id)
        frontend_dir = Path(app.root_path).parent / 'frontend' / 'public' / 'images' / 'imports' / str(doc_id)
        
        existing_files_backend = []
        existing_files_frontend = []
        
        if backend_dir.exists():
            existing_files_backend = list(backend_dir.glob('*'))
        if frontend_dir.exists():
            existing_files_frontend = list(frontend_dir.glob('*'))
        
        print(f"    Backend dir: {backend_dir}")
        print(f"      Files on disk: {len(existing_files_backend)}")
        if existing_files_backend:
            for f in existing_files_backend[:3]:
                print(f"        - {f.name}")
        
        print(f"    Frontend dir: {frontend_dir}")
        print(f"      Files on disk: {len(existing_files_frontend)}")
        if existing_files_frontend:
            for f in existing_files_frontend[:3]:
                print(f"        - {f.name}")
        
        # Check for mismatches
        missing_count = 0
        for img in by_doc[doc_id][:5]:  # Check first 5
            backend_path = Path(img.backend_path)
            frontend_path = Path(img.frontend_path)
            
            backend_exists = backend_path.exists()
            frontend_exists = frontend_path.exists()
            
            if not backend_exists or not frontend_exists:
                missing_count += 1
                if missing_count <= 3:  # Show first 3 missing
                    print(f"\n    ❌ Missing files for: {img.filename}")
                    print(f"       DB record: public_url={img.public_url}")
                    print(f"       Backend path: {img.backend_path} ({'✓' if backend_exists else '✗'})")
                    print(f"       Frontend path: {img.frontend_path} ({'✓' if frontend_exists else '✗'})")
        
        if missing_count > 3:
            print(f"\n    ... and {missing_count - 3} more missing files")
        
        if missing_count == 0:
            print(f"    ✅ All files exist!")

    print("\n\n📋 Summary:")
    print(f"Total images in DB: {len(all_images)}")
    
    # Count missing
    missing = 0
    for img in all_images:
        if not Path(img.backend_path).exists() or not Path(img.frontend_path).exists():
            missing += 1
    
    print(f"Images with missing files: {missing}")
    print(f"Images with files present: {len(all_images) - missing}")
    
    if missing > 0:
        print(f"\n⚠️  {missing} database records point to non-existent files")
        print("This causes 404 errors when the frontend tries to display them as placeholders.")
