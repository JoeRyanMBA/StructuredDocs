#!/usr/bin/env python3
"""
Diagnose missing image files - identify which images aren't displaying and why
"""

import sys
import os
from pathlib import Path
from datetime import datetime

sys.path.insert(0, '/workspaces/StructuredDocs')

def diagnose_missing_images():
    """Check which images are failing to display"""
    print("\n" + "=" * 80)
    print("🔍 MISSING IMAGES DIAGNOSTIC")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        from backend.app import create_app
        from backend.models import ImportImage, ImportDocument, db
        
        app = create_app()
        with app.app_context():
            # Get all import images
            all_images = ImportImage.query.all()
            
            print(f"📊 Total ImportImage records: {len(all_images)}\n")
            
            if not all_images:
                print("No images found in database")
                return
            
            missing_files = []
            found_files = []
            missing_both = []
            backend_ok = []
            frontend_only = []
            
            # Check each image
            for img in all_images:
                backend_path = Path(img.backend_path)
                frontend_path = Path(img.frontend_path)
                
                backend_exists = backend_path.exists() and backend_path.is_file()
                frontend_exists = frontend_path.exists() and frontend_path.is_file()
                
                status = {
                    'img': img,
                    'backend_exists': backend_exists,
                    'frontend_exists': frontend_exists,
                    'backend_path': str(backend_path),
                    'frontend_path': str(frontend_path),
                    'public_url': img.public_url,
                }
                
                if backend_exists:
                    backend_ok.append(status)
                elif frontend_exists:
                    frontend_only.append(status)
                elif backend_exists or frontend_exists:
                    found_files.append(status)
                else:
                    missing_both.append(status)
            
            # Print summary
            print("📋 SUMMARY:")
            print(f"  ✅ Backend files exist: {len(backend_ok)}")
            print(f"  ⚠️  Frontend only (no backend): {len(frontend_only)}")
            print(f"  ❌ Both files missing: {len(missing_both)}")
            
            # Show missing images
            if missing_both:
                print(f"\n🚨 MISSING IMAGE FILES ({len(missing_both)}):")
                print("-" * 80)
                
                for status in missing_both[:10]:  # Show first 10
                    img = status['img']
                    print(f"\n❌ {img.filename}")
                    print(f"   Original: {img.original_name}")
                    print(f"   Public URL: {img.public_url}")
                    print(f"   Document ID: {img.document_id}")
                    print(f"   File size (DB): {img.file_size} bytes")
                    print(f"   Format (DB): {img.format}")
                    print(f"   Backend path: {status['backend_path']}")
                    print(f"   Frontend path: {status['frontend_path']}")
                    
                    # Check parent directories
                    backend_dir = Path(status['backend_path']).parent
                    if backend_dir.exists():
                        print(f"   📁 Backend dir exists: {len(list(backend_dir.glob('*')))} files")
                    else:
                        print(f"   📁 Backend dir missing: {backend_dir}")
                
                if len(missing_both) > 10:
                    print(f"\n... and {len(missing_both) - 10} more missing images")
            
            # Show frontend-only images (might be a fallback issue)
            if frontend_only:
                print(f"\n\n⚠️  FRONTEND-ONLY IMAGES ({len(frontend_only)}):")
                print("-" * 80)
                print("These images exist in frontend/public but not in backend/static")
                print("They may still work if frontend is serving them directly.\n")
                
                for status in frontend_only[:5]:
                    img = status['img']
                    print(f"   {img.filename} -> {img.public_url}")
            
            # Group by document
            print(f"\n\n📁 IMAGES BY DOCUMENT:")
            print("-" * 80)
            
            docs = ImportDocument.query.all()
            for doc in docs:
                doc_images = ImportImage.query.filter_by(document_id=doc.id).all()
                doc_missing = [img for img in doc_images if not (Path(img.backend_path).exists() or Path(img.frontend_path).exists())]
                
                status_icon = "✅" if not doc_missing else "❌"
                print(f"\n{status_icon} Document {doc.id}: {doc.filename}")
                print(f"   Total images: {len(doc_images)}")
                print(f"   Working: {len(doc_images) - len(doc_missing)}")
                if doc_missing:
                    print(f"   Missing: {len(doc_missing)}")
                    for img in doc_missing[:3]:
                        print(f"     - {img.filename}")
                    if len(doc_missing) > 3:
                        print(f"     ... and {len(doc_missing) - 3} more")
            
            # Check for patterns
            print(f"\n\n🔍 ANALYZING FAILURE PATTERNS:")
            print("-" * 80)
            
            if missing_both:
                # Check file sizes
                sizes = [img['img'].file_size for img in missing_both if img['img'].file_size]
                if sizes:
                    print(f"Missing image file sizes: {min(sizes)} - {max(sizes)} bytes")
                    print(f"Average: {sum(sizes) / len(sizes):.0f} bytes")
                
                # Check formats
                formats = set(img['img'].format for img in missing_both if img['img'].format)
                if formats:
                    print(f"Missing image formats: {', '.join(formats)}")
                
                # Check if they're from a specific document
                docs_with_missing = set(img['img'].document_id for img in missing_both)
                print(f"Missing images from documents: {sorted(docs_with_missing)}")
            
            print("\n" + "=" * 80)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    diagnose_missing_images()
