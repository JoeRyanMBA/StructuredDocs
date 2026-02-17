#!/usr/bin/env python3
"""
Comprehensive image troubleshooting - compare database with disk
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, '/workspaces/StructuredDocs')

def comprehensive_image_check():
    """Check both database and disk"""
    
    print("\n" + "=" * 90)
    print("🔍 COMPREHENSIVE IMAGE TROUBLESHOOTING")
    print("=" * 90)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        from backend.app import create_app
        from backend.models import ImportImage, db
        
        app = create_app()
        with app.app_context():
            all_images = ImportImage.query.all()
            print(f"📊 Total images in database: {len(all_images)}\n")
            
            if not all_images:
                print("No images in database")
                return
            
            # Group by status
            working = []
            missing_backend = []
            missing_frontend = []
            missing_both = []
            zero_size = []
            
            for img in all_images:
                backend = Path(img.backend_path)
                frontend = Path(img.frontend_path)
                
                backend_exists = backend.exists() and backend.is_file()
                frontend_exists = frontend.exists() and frontend.is_file()
                
                # Check file size if backend exists
                if backend_exists:
                    size = backend.stat().st_size
                    if size == 0:
                        zero_size.append((img, backend))
                    else:
                        working.append((img, backend))
                elif frontend_exists:
                    missing_backend.append((img, frontend))
                elif backend.parent.exists():
                    # Directory exists but file doesn't
                    missing_frontend.append((img, backend))
                else:
                    missing_both.append((img, backend))
            
            # Print summary
            print("📋 STATUS BREAKDOWN:")
            print(f"  ✅ Working (exists & non-zero): {len(working)}")
            print(f"  ⚠️  Missing backend (frontend only): {len(missing_backend)}")
            print(f"  ⚠️  Missing frontend (backend only): {len(missing_frontend)}")
            print(f"  🚫 Zero-size files: {len(zero_size)}")
            print(f"  ❌ Both missing: {len(missing_both)}\n")
            
            # Show details of problematic images
            if zero_size:
                print("=" * 90)
                print(f"🚫 ZERO-SIZE FILES ({len(zero_size)}):")
                print("-" * 90)
                for img, path in zero_size[:10]:
                    print(f"\n❌ {img.filename}")
                    print(f"   Original: {img.original_name}")
                    print(f"   Document: {img.document_id}")
                    print(f"   Public URL: {img.public_url}")
                    print(f"   Path: {path}")
                    print(f"   File size: 0 bytes (THIS IS THE PROBLEM!)")
                    print(f"   DB recorded size: {img.file_size} bytes")
                    
                if len(zero_size) > 10:
                    print(f"\n   ... and {len(zero_size) - 10} more zero-size files")
            
            if missing_both:
                print("\n" + "=" * 90)
                print(f"❌ MISSING FILES - Both backend & frontend ({len(missing_both)}):")
                print("-" * 90)
                for img, path in missing_both[:10]:
                    print(f"\n❌ {img.filename}")
                    print(f"   Public URL: {img.public_url}")
                    print(f"   Expected path: {path}")
                    print(f"   Document: {img.document_id}")
                    
                if len(missing_both) > 10:
                    print(f"\n   ... and {len(missing_both) - 10} more missing files")
            
            if missing_backend:
                print("\n" + "=" * 90)
                print(f"⚠️  MISSING BACKEND (frontend only - {len(missing_backend)}):")
                print("-" * 90)
                for img, path in missing_backend[:5]:
                    print(f"{img.filename} exists in frontend/public")
            
            # Check for patterns
            if zero_size or missing_both:
                print("\n" + "=" * 90)
                print("🔎 ANALYZING FAILURES:")
                print("-" * 90)
                
                failed = zero_size + missing_both
                if failed:
                    formats = {}
                    sizes = []
                    for img, _ in failed:
                        fmt = img.format or 'unknown'
                        formats[fmt] = formats.get(fmt, 0) + 1
                        if img.file_size:
                            sizes.append(img.file_size)
                    
                    print(f"\nFormats of failed images:")
                    for fmt, count in sorted(formats.items(), key=lambda x: -x[1]):
                        print(f"  {fmt}: {count}")
                    
                    if sizes:
                        print(f"\nSize range of failed images:")
                        print(f"  Min: {min(sizes) / 1024:.1f} KB")
                        print(f"  Max: {max(sizes) / (1024*1024):.1f} MB")
                        print(f"  Avg: {sum(sizes) / len(sizes) / 1024:.1f} KB")
                    
                    # Check by document
                    docs = {}
                    for img, _ in failed:
                        docs[img.document_id] = docs.get(img.document_id, 0) + 1
                    print(f"\nFailing documents: {len(docs)}")
                    for doc_id, count in sorted(docs.items()):
                        print(f"  Document {doc_id}: {count} failures")
            
            # Check successful images as a comparison
            print("\n" + "=" * 90)
            print("✅ SUCCESSFUL IMAGES - Patterns that WORK:")
            print("-" * 90)
            
            if working:
                formats = {}
                sizes = []
                for img, _ in working:
                    fmt = img.format or 'unknown'
                    formats[fmt] = formats.get(fmt, 0) + 1
                    if img.file_size:
                        sizes.append(img.file_size)
                
                print(f"Total working: {len(working)}")
                print(f"\nWorking formats:")
                for fmt, count in sorted(formats.items(), key=lambda x: -x[1]):
                    print(f"  {fmt}: {count}")
                
                if sizes:
                    print(f"\nSize range of working images:")
                    print(f"  Min: {min(sizes) / 1024:.1f} KB")
                    print(f"  Max: {max(sizes) / (1024*1024):.1f} MB")
                    print(f"  Avg: {sum(sizes) / len(sizes) / 1024:.1f} KB")
            
            print("\n" + "=" * 90)
            
            # Recommendations
            if zero_size:
                print("\n📝 RECOMMENDATIONS FOR ZERO-SIZE FILES:")
                print("-" * 90)
                print("Zero-size files are completely empty - they cannot be displayed.")
                print("This happens when the file gets created but nothing is written to it.")
                print("\nPossible causes:")
                print("1. Image optimization failed and fallback copy didn't work")
                print("2. Disk ran out of space mid-write")
                print("3. File permissions issue")
                print("4. Source file was corrupted/empty")
                print("\nSolution:")
                print("1. Check backend logs for 'Storing image' errors during import")
                print("2. Verify disk space: 'df -h /workspaces/StructuredDocs/'")
                print("3. Try re-importing the document")
                print("4. If it persists, delete zero-size imports and retry")
            
            if missing_both:
                print("\n📝 RECOMMENDATIONS FOR MISSING FILES:")
                print("-" * 90)
                print("Files exist in database but not on disk.")
                print("This means image saving failed completely.")
                print("\nPossible causes:")
                print("1. Image directory wasn't created before save")
                print("2. File write failed silently")
                print("3. Directory got deleted after import")
                print("\nSolution: Re-import the document")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    comprehensive_image_check()
