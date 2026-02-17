#!/usr/bin/env python3
"""Diagnose current image display issue after fresh import"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, '/workspaces/StructuredDocs')
sys.path.insert(0, '/workspaces/StructuredDocs/backend')

def diagnose():
    """Diagnose the image issue"""
    
    print("=" * 70)
    print("🔍 IMAGE DISPLAY DIAGNOSTICS - Fresh Import Analysis")
    print("=" * 70)
    
    try:
        from backend.app import create_app
        from backend.models import ImportImage, ImportDocument, db
        
        app = create_app()
        with app.app_context():
            
            # Check database records
            print("\n📊 DATABASE ANALYSIS:")
            print("-" * 70)
            
            total_docs = ImportDocument.query.count()
            total_images = ImportImage.query.count()
            
            print(f"✓ Total ImportDocuments: {total_docs}")
            print(f"✓ Total ImportImage records: {total_images}")
            
            if total_images == 0:
                print("\n⚠️  WARNING: No ImportImage records found!")
                print("   This means either:")
                print("   1. No documents have been imported yet")
                print("   2. Import is failing to save images to database")
                return
            
            # Analyze each document's images
            print("\n📋 DOCUMENT DETAILS:")
            print("-" * 70)
            
            docs = ImportDocument.query.all()
            for doc in docs:
                print(f"\n📁 Document ID {doc.id}: {doc.filename}")
                print(f"   Status: {doc.status}")
                print(f"   Images: {len(doc.images)}")
                
                # Check each image record
                for img in doc.images:
                    print(f"\n   📸 {img.filename}")
                    print(f"      Original: {img.original_name}")
                    print(f"      Public URL: {img.public_url}")
                    
                    # Check if backend file exists
                    backend_path = Path(img.backend_path)
                    backend_exists = backend_path.exists()
                    print(f"      Backend path: {img.backend_path}")
                    print(f"      Backend exists: {backend_exists}")
                    
                    if not backend_exists:
                        # List contents of backend images dir if it exists
                        parent_dir = backend_path.parent
                        if parent_dir.exists():
                            print(f"         📁 Contents of {parent_dir}:")
                            try:
                                items = list(parent_dir.iterdir())
                                if items:
                                    for item in items[:5]:
                                        print(f"            - {item.name}")
                                    if len(items) > 5:
                                        print(f"            ... and {len(items) - 5} more files")
                                else:
                                    print(f"            (empty directory)")
                            except Exception as e:
                                print(f"            Error listing: {e}")
                    
                    # Check frontend file
                    frontend_path = Path(img.frontend_path)
                    frontend_exists = frontend_path.exists()
                    print(f"      Frontend path: {img.frontend_path}")
                    print(f"      Frontend exists: {frontend_exists}")
                    
                    # Check file sizes
                    if backend_exists:
                        try:
                            file_size = backend_path.stat().st_size
                            print(f"      File size: {file_size} bytes")
                        except:
                            pass
                    
                    # Status summary
                    if backend_exists or frontend_exists:
                        print(f"      ✅ File is accessible")
                    else:
                        print(f"      ❌ FILE MISSING - This will cause 404 errors!")
            
            # Check disk storage locations
            print("\n\n💾 DISK STORAGE ANALYSIS:")
            print("-" * 70)
            
            # Backend images directory
            backend_images_root = Path(app.root_path) / 'static' / 'images'
            print(f"\nBackend images root: {backend_images_root}")
            print(f"Exists: {backend_images_root.exists()}")
            
            if backend_images_root.exists():
                try:
                    # Count images recursively
                    import_dirs = list((backend_images_root / 'imports').glob('*/')) if (backend_images_root / 'imports').exists() else []
                    print(f"Import directories: {len(import_dirs)}")
                    
                    total_files = sum(1 for _ in backend_images_root.rglob('*') if _.is_file())
                    print(f"Total image files: {total_files}")
                    
                    # Show structure
                    for import_dir in import_dirs[:3]:
                        files = list(import_dir.glob('*'))
                        print(f"  {import_dir.name}: {len(files)} files")
                        for f in files[:3]:
                            print(f"    - {f.name}")
                        if len(files) > 3:
                            print(f"    ... and {len(files) - 3} more")
                except Exception as e:
                    print(f"Error analyzing: {e}")
            
            # Frontend images directory
            frontend_images_root = Path(app.root_path).parent / 'frontend' / 'public' / 'images'
            print(f"\nFrontend images root: {frontend_images_root}")
            print(f"Exists: {frontend_images_root.exists()}")
            
            if frontend_images_root.exists():
                try:
                    import_dirs = list((frontend_images_root / 'imports').glob('*/')) if (frontend_images_root / 'imports').exists() else []
                    print(f"Import directories: {len(import_dirs)}")
                except Exception as e:
                    print(f"Error analyzing: {e}")
            
            # Check if the routes are configured
            print("\n\n🔌 API ROUTES CHECK:")
            print("-" * 70)
            
            # Check if public_images blueprint is registered
            has_public_images = any(
                rule.endpoint.startswith('public_images') 
                for rule in app.url_map.iter_rules()
            )
            print(f"✓ /images/imports/<doc_id>/<filename> route: {'✅ Registered' if has_public_images else '❌ NOT registered'}")
            
            # List all image-related routes
            image_routes = [rule for rule in app.url_map.iter_rules() if 'image' in rule.endpoint.lower()]
            print(f"✓ Total image-related routes: {len(image_routes)}")
            for route in image_routes:
                print(f"  - {route.rule} ({route.endpoint})")
            
            print("\n" + "=" * 70)
            print("✅ DIAGNOSTICS COMPLETE")
            print("=" * 70)
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose()
