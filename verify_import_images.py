#!/usr/bin/env python3
"""
Image Import Verification & Troubleshooting Guide

This script helps diagnose why images aren't appearing after Word document imports.
Run this AFTER importing a document and its collection appears but images don't show.

Usage:
  python3 verify_import_images.py
"""

import sys
import os
from pathlib import Path
from datetime import datetime

def check_database_images():
    """Check if ImportImage records exist in the database"""
    print("\n" + "=" * 70)
    print("📊 STEP 1: Checking Database for Image Records")
    print("=" * 70)
    
    try:
        # Try to connect via SQLAlchemy
        sys.path.insert(0, '/workspaces/StructuredDocs')
        from backend.app import create_app
        from backend.models import ImportImage, ImportDocument, db
        
        app = create_app()
        with app.app_context():
            total_images = ImportImage.query.count()
            total_docs = ImportDocument.query.count()
            
            print(f"\n✓ Total ImportDocument records: {total_docs}")
            print(f"✓ Total ImportImage records: {total_images}")
            
            if total_images == 0:
                print("\n⚠️  FINDING: No ImportImage records found in database")
                print("   Possible causes:")
                print("   1. No documents have been imported yet")
                print("   2. Images were extracted but not stored to database")
                print("   3. Image import process failed silently")
                return False
            
            # List recent images
            print(f"\n📋 Recent ImportImage records (last 10):")
            recent = ImportImage.query.order_by(ImportImage.created_at.desc()).limit(10).all()
            
            for img in recent:
                print(f"\n   📸 {img.filename}")
                print(f"      Document ID: {img.document_id}")
                print(f"      Public URL: {img.public_url}")
                print(f"      Created: {img.created_at}")
                
                # Check if file exists
                from pathlib import Path
                backend_file = Path(img.backend_path)
                frontend_file = Path(img.frontend_path)
                
                backend_exists = backend_file.exists()
                frontend_exists = frontend_file.exists()
                
                if backend_exists or frontend_exists:
                    print(f"      ✅ Files found on disk")
                    if backend_exists:
                        size = backend_file.stat().st_size
                        print(f"         - Backend: {size} bytes")
                else:
                    print(f"      ❌ FILES MISSING ON DISK - This is the problem!")
                    print(f"         Backend path: {img.backend_path}")
                    print(f"         Frontend path: {img.frontend_path}")
            
            return total_images > 0
            
    except Exception as e:
        print(f"\n❌ Error checking database: {e}")
        print("   Make sure the app is running and database is accessible")
        return False

def check_disk_files():
    """Check if image files exist on disk"""
    print("\n" + "=" * 70)
    print("💾 STEP 2: Checking Disk for Image Files")
    print("=" * 70)
    
    backend_root = Path('/workspaces/StructuredDocs/backend/static/images/imports')
    frontend_root = Path('/workspaces/StructuredDocs/frontend/public/images/imports')
    
    print(f"\nBackend import directory: {backend_root}")
    print(f"Exists: {backend_root.exists()}")
    
    if backend_root.exists():
        doc_dirs = list(backend_root.glob('*/'))
        print(f"Document folders found: {len(doc_dirs)}")
        
        total_files = 0
        for doc_dir in sorted(doc_dirs):
            files = list(doc_dir.glob('*'))
            total_files += len(files)
            print(f"  📁 {doc_dir.name}: {len(files)} files")
            for f in files[:3]:
                if f.is_file():
                    size = f.stat().st_size
                    print(f"     - {f.name} ({size} bytes)")
            if len(files) > 3:
                print(f"     ... and {len(files) - 3} more files")
        
        print(f"Total image files: {total_files}")
        if total_files == 0:
            print("\n⚠️  FINDING: No image files found on disk!")
            print("   This explains why images aren't showing!")
            return False
        
        return True
    else:
        print("\n❌ FINDING: Backend imports directory does not exist!")
        print("   Images are not being saved to disk")
        return False

def check_api_endpoint():
    """Check if /api/images endpoint returns imported images"""
    print("\n" + "=" * 70)
    print("🔌 STEP 3: Checking API Endpoint")
    print("=" * 70)
    
    print("\nTo check the API endpoint:")
    print("1. Open your browser's developer console (F12)")
    print("2. Go to your application's All Images page")
    print("3. In the Network tab, look for a request to /api/images")
    print("4. Check the response - it should include your imported images")
    print("\nAlternatively, cURL command:")
    print("  curl -s http://localhost:8080/api/images | grep -i import")

def check_image_routes():
    """Check if /images/imports/ route is configured"""
    print("\n" + "=" * 70)
    print("🛣️  STEP 4: Checking Image Serving Routes")
    print("=" * 70)
    
    try:
        sys.path.insert(0, '/workspaces/StructuredDocs')
        from backend.app import create_app
        
        app = create_app()
        
        image_routes = [
            rule for rule in app.url_map.iter_rules() 
            if 'image' in rule.endpoint.lower() or '/images' in rule.rule
        ]
        
        print(f"\n✓ Found {len(image_routes)} image-related routes:")
        for route in image_routes:
            print(f"  - {route.rule} ({route.endpoint})")
        
        # Check for the critical public_images route
        has_imports_route = any('/images/imports/<int:doc_id>' in str(rule.rule) for rule in image_routes)
        
        if has_imports_route:
            print("\n✅ /images/imports/<doc_id>/<filename> route: FOUND")
            return True
        else:
            print("\n❌ /images/imports/<doc_id>/<filename> route: NOT FOUND")
            print("   This route is needed to serve imported images!")
            return False
            
    except Exception as e:
        print(f"\n❌ Error checking routes: {e}")
        return False

def main():
    """Run all diagnostics"""
    print("\n" + "=" * 70)
    print("🔍 IMAGE IMPORT TROUBLESHOOTING GUIDE")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Run diagnostic checks
    db_ok = check_database_images()
    results.append(("Database Records", db_ok))
    
    disk_ok = check_disk_files()
    results.append(("Disk Files", disk_ok))
    
    routes_ok = check_image_routes()
    results.append(("API Routes", routes_ok))
    
    check_api_endpoint()
    
    # Summary
    print("\n" + "=" * 70)
    print("📋 DIAGNOSTIC SUMMARY")
    print("=" * 70)
    
    all_ok = all(ok for _, ok in results)
    
    for name, ok in results:
        status = "✅ OK" if ok else "❌ FAILED"
        print(f"  {name:<25} {status}")
    
    print("\n" + "=" * 70)
    if all_ok:
        print("✅ All checks passed! Images should be displaying.")
        print("   If they're still not showing, try:")
        print("   1. Hard refresh your browser (Ctrl+Shift+R or Cmd+Shift+R)")
        print("   2. Clear browser cache for the app domain")
        print("   3. Check browser console for 404 errors (press F12)")
    else:
        print("❌ Issues detected. Next steps:")
        print("\n   If Database Records are missing:")
        print("   - Images may not have been extracted by Pandoc")
        print("   - Check backend logs for 'PANDOC' messages")
        print("   - Make sure Word document has actual images in it")
        
        print("\n   If Disk Files are missing:")
        print("   - Image extraction succeeded but saving failed")
        print("   - Check backend logs for 'Storing image'or write permission errors")
        print("   - Verify disk space is available")
        print("   - Check /workspaces/StructuredDocs/backend/static/images/ permissions")
        
        print("\n   Try re-importing the document after checking logs:")
        print("   - Monitor the backend logs in a terminal")
        print("   - Look for messages containing 'PANDOC', 'Storing image', or errors")
        print("   - This will show exactly where the process is failing")
    
    print("\n" + "=" * 70)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
