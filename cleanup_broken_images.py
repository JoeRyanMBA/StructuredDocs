#!/usr/bin/env python3
"""
Cleanup script for zero-size and missing image files
Run this to fix existing broken image imports
"""

import sys
from pathlib import Path

sys.path.insert(0, '/workspaces/StructuredDocs')

def cleanup_broken_images():
    """Remove zero-size and missing image records from database"""
    
    print("\n" + "=" * 80)
    print("🧹 IMAGE CLEANUP - Removing broken image records")
    print("=" * 80 + "\n")
    
    try:
        from backend.app import create_app
        from backend.models import ImportImage, db
        
        app = create_app()
        with app.app_context():
            all_images = ImportImage.query.all()
            
            zero_size_images = []
            missing_images = []
            
            # Identify broken images
            for img in all_images:
                backend = Path(img.backend_path)
                frontend = Path(img.frontend_path)
                
                backend_exists = backend.exists() and backend.is_file()
                frontend_exists = frontend.exists() and frontend.is_file()
                
                # Check for zero-size
                if backend_exists:
                    size = backend.stat().st_size
                    if size == 0:
                        zero_size_images.append((img, backend))
                
                # Check for completely missing
                if not backend_exists and not frontend_exists:
                    missing_images.append((img, backend))
            
            # Show what we found
            print(f"📊 Found {len(zero_size_images)} zero-size files")
            print(f"📊 Found {len(missing_images)} completely missing files\n")
            
            if not zero_size_images and not missing_images:
                print("✅ No broken images found!")
                return
            
            # Show details
            all_broken = zero_size_images + missing_images
            
            print("🔍 Details of broken images:")
            print("-" * 80)
            for img, path in all_broken[:20]:
                status = "ZERO-SIZE" if (path.exists() and path.stat().st_size == 0) else "MISSING"
                print(f"  [{status}] {img.filename} (from document {img.document_id})")
            
            if len(all_broken) > 20:
                print(f"  ... and {len(all_broken) - 20} more")
            
            # Ask for confirmation
            if len(all_broken) > 0:
                print("\n" + "=" * 80)
                print("⚠️  These images will be DELETED from the database and disk:")
                print("   - Zero-size files will be removed from disk")
                print("   - All broken image records will be removed from database")
                print("   - This action CANNOT be undone")
                print("=" * 80 + "\n")
                
                response = input("Continue with cleanup? (type 'yes' to confirm): ").strip().lower()
                
                if response != 'yes':
                    print("❌ Cleanup cancelled")
                    return
                
                # Perform cleanup
                deleted = 0
                for img, path in zero_size_images:
                    try:
                        if path.exists():
                            path.unlink()
                            print(f"  🗑️  Deleted zero-size file: {path.name}")
                        db.session.delete(img)
                        deleted += 1
                    except Exception as e:
                        print(f"  ⚠️  Failed to delete {path.name}: {e}")
                
                for img, path in missing_images:
                    try:
                        db.session.delete(img)
                        deleted += 1
                        print(f"  🗑️  Deleted missing image record: {img.filename}")
                    except Exception as e:
                        print(f"  ⚠️  Failed to delete {img.filename}: {e}")
                
                # Commit changes
                db.session.commit()
                print(f"\n✅ Cleanup complete! Deleted {deleted} broken image records")
                
                # Show results
                remaining = ImportImage.query.count()
                print(f"📊 Images remaining: {remaining}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    cleanup_broken_images()
