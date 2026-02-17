#!/usr/bin/env python3
"""
Trace a specific image through the entire system
Shows database record, disk file, API response, and serving path
"""

import sys
from pathlib import Path

sys.path.insert(0, '/workspaces/StructuredDocs')

def trace_image(filename_pattern):
    """Trace a specific image through the system"""
    
    print("\n" + "=" * 90)
    print(f"🔍 IMAGE TRACE: {filename_pattern}")
    print("=" * 90 + "\n")
    
    try:
        from backend.app import create_app
        from backend.models import ImportImage, db
        
        app = create_app()
        with app.app_context():
            # Find image in database
            images = ImportImage.query.filter(ImportImage.filename.like(f'%{filename_pattern}%')).all()
            
            if not images:
                print(f"❌ No images matching '{filename_pattern}' found in database")
                
                # Try to find it on disk
                print("\n🔍 Searching disk...")
                backend_root = Path('/workspaces/StructuredDocs/backend/static/images/imports')
                if backend_root.exists():
                    found = list(backend_root.rglob(f'*{filename_pattern}*'))
                    if found:
                        print(f"   Found on disk: {[str(f) for f in found]}")
                        print("   But NOT in database - the import may have failed to save the record")
                    else:
                        print(f"   Also not found on disk")
                return
            
            # Trace each matching image
            for img in images:
                print(f"📋 DATABASE RECORD:")
                print(f"   ID: {img.id}")
                print(f"   Filename: {img.filename}")
                print(f"   Original name: {img.original_name}")
                print(f"   Document ID: {img.document_id}")
                print(f"   Public URL: {img.public_url}")
                print(f"   File size (DB): {img.file_size} bytes")
                print(f"   Format: {img.format}")
                print(f"   MIME type: {img.mime_type}")
                print(f"   Width x Height: {img.width} x {img.height}")
                print(f"   Created: {img.created_at}")
                
                # Check backend file
                backend_path = Path(img.backend_path)
                print(f"\n📁 BACKEND FILE:")
                print(f"   Expected path: {backend_path}")
                print(f"   Exists: {backend_path.exists()}")
                
                if backend_path.exists():
                    size = backend_path.stat().st_size
                    print(f"   Actual size: {size} bytes")
                    if size == 0:
                        print(f"   ⚠️  FILE IS ZERO-SIZED!")
                    elif size != img.file_size:
                        print(f"   ⚠️  Size mismatch! DB says {img.file_size} but file is {size}")
                    else:
                        print(f"   ✅ Size matches database")
                else:
                    print(f"   ❌ FILE MISSING")
                    
                    # Check if directory exists
                    parent = backend_path.parent
                    if parent.exists():
                        files_in_dir = list(parent.glob('*'))
                        print(f"   📁 Parent directory exists with {len(files_in_dir)} files")
                        if files_in_dir:
                            print(f"      Files in directory:")
                            for f in sorted(files_in_dir)[:5]:
                                print(f"        - {f.name}")
                            if len(files_in_dir) > 5:
                                print(f"        ... and {len(files_in_dir) - 5} more")
                    else:
                        print(f"   📁 Parent directory doesn't exist: {parent}")
                
                # Check frontend file
                frontend_path = Path(img.frontend_path)
                print(f"\n🌐 FRONTEND FILE:")
                print(f"   Expected path: {frontend_path}")
                print(f"   Exists: {frontend_path.exists()}")
                
                if frontend_path.exists():
                    size = frontend_path.stat().st_size
                    print(f"   Actual size: {size} bytes")
                    if size == 0:
                        print(f"   ⚠️  FILE IS ZERO-SIZED!")
                
                # Show API endpoint
                print(f"\n🔗 API ENDPOINTS:")
                print(f"   /api/images endpoint will return this record")
                print(f"   Response will include:")
                print(f"     - filename: {img.filename}")
                print(f"     - public_url: {img.public_url}")
                print(f"     - file_exists: {backend_path.exists() or frontend_path.exists()}")
                
                # Show serving endpoint
                print(f"\n📡 IMAGE SERVING:")
                print(f"   Frontend requests: {img.public_url}")
                print(f"   Backend serves from:")
                if backend_path.exists():
                    print(f"     ✅ {backend_path}")
                elif frontend_path.exists():
                    print(f"     ⚠️  {frontend_path} (frontend fallback)")
                else:
                    print(f"     ❌ NEITHER PATH EXISTS!")
                
                # Diagnosis
                print(f"\n🔎 DIAGNOSIS:")
                backend_ok = backend_path.exists() and backend_path.stat().st_size > 0
                frontend_ok = frontend_path.exists() and frontend_path.stat().st_size > 0
                
                if backend_ok or frontend_ok:
                    if backend_ok:
                        print(f"   ✅ Backend file is valid and can be served")
                    else:
                        print(f"   ⚠️  Backend missing but frontend exists")
                        print(f"      Frontend fallback should work")
                elif backend_path.exists() or frontend_path.exists():
                    print(f"   ❌ Files exist but are zero-sized")
                    print(f"      Cannot be displayed")
                    print(f"      SOLUTION: Run cleanup_broken_images.py and re-import")
                else:
                    print(f"   ❌ Files are completely missing")
                    print(f"      Database record exists but files were never created")
                    print(f"      SOLUTION: Run cleanup_broken_images.py and re-import")
                
                print()
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("\nUsage: python3 trace_image.py <filename_or_pattern>")
        print("\nExamples:")
        print("  python3 trace_image.py image1_63017649.png")
        print("  python3 trace_image.py image1")
        print("  python3 trace_image.py .jpeg")
        sys.exit(1)
    
    pattern = sys.argv[1]
    trace_image(pattern)
