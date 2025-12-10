#!/usr/bin/env python3
"""
Fix missing images for import 64
Options:
1. Clean up database records for missing files
2. Re-extract images from source document (if available)
"""
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, '/root/StructuredDocs/backend')

from app import app, db
from models import ImportImage, ImportedDocument

def cleanup_missing_images(doc_id=64, dry_run=True):
    """Remove database records for images that don't exist on filesystem"""
    
    with app.app_context():
        db_images = ImportImage.query.filter_by(document_id=doc_id).all()
        
        backend_dir = Path(f'/root/StructuredDocs/backend/static/images/imports/{doc_id}')
        frontend_dir = Path(f'/root/StructuredDocs/frontend/public/images/imports/{doc_id}')
        
        to_delete = []
        
        for img in db_images:
            filename = img.filename
            backend_path = backend_dir / filename
            frontend_path = frontend_dir / filename
            
            # If file doesn't exist in either location, mark for deletion
            if not backend_path.exists() and not frontend_path.exists():
                to_delete.append(img)
        
        print(f"\n{'='*80}")
        print(f"CLEANUP ANALYSIS FOR IMPORT {doc_id}")
        print(f"{'='*80}\n")
        print(f"Total DB records: {len(db_images)}")
        print(f"Records to delete: {len(to_delete)}")
        
        if to_delete:
            print("\nImages to be deleted from database:")
            for img in to_delete:
                print(f"  - {img.filename} (id={img.id})")
        
        if dry_run:
            print("\n⚠️  DRY RUN - No changes made")
            print("Run with dry_run=False to actually delete records")
        else:
            print("\n🗑️  Deleting records...")
            for img in to_delete:
                db.session.delete(img)
            db.session.commit()
            print(f"✅ Deleted {len(to_delete)} records")

def check_source_document(doc_id=64):
    """Check if source document still exists for re-import"""
    
    with app.app_context():
        doc = ImportedDocument.query.get(doc_id)
        
        print(f"\n{'='*80}")
        print(f"SOURCE DOCUMENT CHECK FOR IMPORT {doc_id}")
        print(f"{'='*80}\n")
        
        if not doc:
            print(f"❌ Document {doc_id} not found in database")
            return False
        
        print(f"✅ Document found:")
        print(f"   ID: {doc.id}")
        print(f"   Title: {doc.title}")
        print(f"   Filename: {doc.original_filename}")
        print(f"   Created: {doc.created_at}")
        print(f"   Status: {doc.status}")
        
        # Check if original file exists
        if doc.file_path:
            file_path = Path(doc.file_path)
            if file_path.exists():
                size = file_path.stat().st_size
                print(f"\n✅ Source file exists: {file_path}")
                print(f"   Size: {size:,} bytes")
                print(f"\n💡 You can re-import this document to extract images again")
                return True
            else:
                print(f"\n❌ Source file missing: {file_path}")
                print(f"   Cannot re-import - file no longer exists")
                return False
        else:
            print(f"\n❌ No file path stored in database")
            return False

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix missing images for import')
    parser.add_argument('--doc-id', type=int, default=64, help='Document ID to fix')
    parser.add_argument('--cleanup', action='store_true', help='Clean up missing image records')
    parser.add_argument('--no-dry-run', action='store_true', help='Actually perform cleanup (not dry run)')
    parser.add_argument('--check-source', action='store_true', help='Check if source document exists')
    
    args = parser.parse_args()
    
    if args.check_source:
        check_source_document(args.doc_id)
    elif args.cleanup:
        cleanup_missing_images(args.doc_id, dry_run=not args.no_dry_run)
    else:
        print("Usage:")
        print("  Check source document:  python fix_import_64_images.py --check-source")
        print("  Cleanup (dry run):      python fix_import_64_images.py --cleanup")
        print("  Cleanup (for real):     python fix_import_64_images.py --cleanup --no-dry-run")
