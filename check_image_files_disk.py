#!/usr/bin/env python3
"""
Quick check of missing images - shows which files exist and which don't
"""

import os
from pathlib import Path

def check_missing_images():
    """Directly check disk without Flask dependencies"""
    
    print("\n" + "=" * 80)
    print("🔍 IMAGE FILE CHECK - Direct Disk Scan")
    print("=" * 80 + "\n")
    
    backend_root = Path('/workspaces/StructuredDocs/backend/static/images/imports')
    
    if not backend_root.exists():
        print(f"❌ Backend imports directory doesn't exist: {backend_root}")
        return
    
    print(f"Backend images directory: {backend_root}\n")
    
    # Scan all files
    total_files = 0
    total_size = 0
    files_by_doc = {}
    
    for doc_dir in sorted(backend_root.glob('*/')):
        if not doc_dir.is_dir():
            continue
        
        doc_id = doc_dir.name
        files = list(doc_dir.glob('*'))
        
        if not files_by_doc.get(doc_id):
            files_by_doc[doc_id] = []
        
        for f in sorted(files):
            if f.is_file():
                size = f.stat().st_size
                total_files += 1
                total_size += size
                files_by_doc[doc_id].append({
                    'name': f.name,
                    'size': size,
                    'path': str(f)
                })
    
    print(f"📊 Summary:")
    print(f"  Total documents: {len(files_by_doc)}")
    print(f"  Total image files: {total_files}")
    print(f"  Total size: {total_size / (1024*1024):.1f} MB\n")
    
    # Show details by document
    for doc_id in sorted(files_by_doc.keys()):
        files = files_by_doc[doc_id]
        size_mb = sum(f['size'] for f in files) / (1024*1024)
        
        print(f"📁 Document {doc_id}: {len(files)} files ({size_mb:.1f} MB)")
        
        # Group by size ranges
        zero_size = [f for f in files if f['size'] == 0]
        tiny = [f for f in files if 0 < f['size'] < 1024]
        small = [f for f in files if 1024 <= f['size'] < 100*1024]
        medium = [f for f in files if 100*1024 <= f['size'] < 1024*1024]
        large = [f for f in files if f['size'] >= 1024*1024]
        
        if zero_size:
            print(f"  ⚠️  ZERO-SIZE files: {len(zero_size)}")
            for f in zero_size[:3]:
                print(f"     - {f['name']}")
        
        if tiny:
            print(f"  🟡 Tiny (<1KB): {len(tiny)}")
        if small:
            print(f"  🟢 Small (1-100KB): {len(small)}")
        if medium:
            print(f"  🔵 Medium (100KB-1MB): {len(medium)}")
        if large:
            print(f"  🔴 Large (>1MB): {len(large)}")
            for f in large:
                print(f"     - {f['name']} ({f['size'] / (1024*1024):.1f} MB)")
        
        # Show all files
        print(f"     Files:")
        for f in sorted(files, key=lambda x: x['size'])[:10]:
            size_kb = f['size'] / 1024
            print(f"       - {f['name']} ({size_kb:.1f} KB)")
        if len(files) > 10:
            print(f"       ... and {len(files) - 10} more")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    check_missing_images()
