#!/usr/bin/env python3
"""
Recovery tool for missing imported images.
This script helps diagnose and potentially recover images that were imported
but whose files are no longer on disk while database records still exist.
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

def check_import_status():
    """Check status of all imports and their images"""
    with app.app_context():
        from backend.extensions import db
        
        print("\n" + "="*70)
        print("📋 IMPORT IMAGE RECOVERY DIAGNOSTIC")
        print("="*70)
        
        # Get all import documents
        all_docs = ImportDocument.query.all()
        print(f"\n📚 Total import documents: {len(all_docs)}")
        
        problematic_docs = []
        
        for doc in all_docs:
            db_images = ImportImage.query.filter_by(document_id=doc.id).all()
            
            if db_images:
                # Check which images have missing files
                missing_count = 0
                existing_count = 0
                
                for img in db_images:
                    backend_path = Path(img.backend_path)
                    frontend_path = Path(img.frontend_path)
                    
                    if backend_path.exists() or frontend_path.exists():
                        existing_count += 1
                    else:
                        missing_count += 1
                
                if missing_count > 0:
                    problematic_docs.append({
                        'id': doc.id,
                        'filename': doc.filename,
                        'total_images': len(db_images),
                        'existing': existing_count,
                        'missing': missing_count
                    })
        
        if problematic_docs:
            print(f"\n⚠️  Found {len(problematic_docs)} documents with missing image files:\n")
            for doc in problematic_docs:
                print(f"  📄 Import {doc['id']}: {doc['filename']}")
                print(f"     Total images: {doc['total_images']}")
                print(f"     ✓ Files exist: {doc['existing']}")
                print(f"     ✗ Files missing: {doc['missing']}")
                print()
        else:
            print("\n✅ All imported image files exist on disk!")
        
        print("\n" + "="*70)
        print("💡 RECOMMENDATIONS:")
        print("="*70)
        
        if problematic_docs:
            print("""
If images are missing:

1. Check if the import process completed successfully
   - Look for errors in the import process logs
   
2. Check if images were stored but in wrong location
   - Backend expects: backend/static/images/imports/{doc_id}/{filename}
   - Frontend expects: frontend/public/images/imports/{doc_id}/{filename}
   
3. The fix now applied:
   - API endpoints now validate files exist before returning them
   - Frontend will only see images that actually exist on disk
   - No more 404 errors for phantom images
   
4. For old imports with missing images:
   - You may need to re-import the document to re-extract images
   - Or manually upload the image files to the correct locations
""")
        else:
            print("""
✅ No issues found! All imported images have corresponding files on disk.

If you're still seeing placeholder images in the Document Builder:
1. Clear your browser cache and reload
2. Check the browser console for any remaining 404 errors
3. Verify the static file serving route is working correctly
""")

if __name__ == '__main__':
    check_import_status()
