#!/usr/bin/env python3
"""
Check image files for import 64 - compare database records vs actual files
"""
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, '/root/StructuredDocs/backend')

from app import app, db
from models import ImportImage

def check_import_images(doc_id=64):
    """Check which images exist in DB vs filesystem for a specific import"""
    
    with app.app_context():
        # Get all images from database for this import
        db_images = ImportImage.query.filter_by(document_id=doc_id).all()
        
        print(f"\n{'='*80}")
        print(f"IMAGE DIAGNOSIS FOR IMPORT {doc_id}")
        print(f"{'='*80}\n")
        
        print(f"📊 Database Records: {len(db_images)} images")
        
        # Check both storage locations
        backend_dir = Path(f'/root/StructuredDocs/backend/static/images/imports/{doc_id}')
        frontend_dir = Path(f'/root/StructuredDocs/frontend/public/images/imports/{doc_id}')
        
        backend_exists = backend_dir.exists()
        frontend_exists = frontend_dir.exists()
        
        print(f"📁 Backend directory exists: {backend_exists}")
        if backend_exists:
            backend_files = list(backend_dir.glob('*'))
            print(f"   Files in backend: {len(backend_files)}")
        else:
            backend_files = []
            
        print(f"📁 Frontend directory exists: {frontend_exists}")
        if frontend_exists:
            frontend_files = list(frontend_dir.glob('*'))
            print(f"   Files in frontend: {len(frontend_files)}")
        else:
            frontend_files = []
        
        # Analyze each database record
        print(f"\n{'='*80}")
        print("DETAILED ANALYSIS")
        print(f"{'='*80}\n")
        
        missing_backend = []
        missing_frontend = []
        found_both = []
        
        for img in db_images:
            filename = img.filename
            backend_path = backend_dir / filename if backend_exists else None
            frontend_path = frontend_dir / filename if frontend_exists else None
            
            backend_file_exists = backend_path.exists() if backend_path else False
            frontend_file_exists = frontend_path.exists() if frontend_path else False
            
            status = "✅" if (backend_file_exists and frontend_file_exists) else "❌"
            
            print(f"{status} {filename}")
            print(f"   DB: id={img.id}, size={img.file_size}")
            print(f"   Backend: {'EXISTS' if backend_file_exists else 'MISSING'}", end="")
            if backend_file_exists and backend_path:
                size = backend_path.stat().st_size
                print(f" ({size:,} bytes)")
            else:
                print()
                
            print(f"   Frontend: {'EXISTS' if frontend_file_exists else 'MISSING'}", end="")
            if frontend_file_exists and frontend_path:
                size = frontend_path.stat().st_size
                print(f" ({size:,} bytes)")
            else:
                print()
            print()
            
            if not backend_file_exists:
                missing_backend.append(filename)
            if not frontend_file_exists:
                missing_frontend.append(filename)
            if backend_file_exists and frontend_file_exists:
                found_both.append(filename)
        
        # Summary
        print(f"{'='*80}")
        print("SUMMARY")
        print(f"{'='*80}\n")
        print(f"✅ Files exist (both locations): {len(found_both)}")
        print(f"❌ Missing from backend: {len(missing_backend)}")
        print(f"❌ Missing from frontend: {len(missing_frontend)}")
        
        if missing_backend or missing_frontend:
            print(f"\n⚠️  ACTION REQUIRED:")
            print(f"   - Re-import document {doc_id} to extract missing images")
            print(f"   - OR clean up database records for missing files")
        else:
            print(f"\n✅ All database records have corresponding files!")

if __name__ == '__main__':
    check_import_images(64)
