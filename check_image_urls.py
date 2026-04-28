"""
Quick script to check what public_url values are stored in the database
"""
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app import create_app
from backend.models import ImportImage

app = create_app()

with app.app_context():
    # Get recent images
    recent_images = ImportImage.query.order_by(ImportImage.created_at.desc()).limit(10).all()
    
    print("=" * 80)
    print("RECENT IMPORT IMAGES - URL CHECK")
    print("=" * 80)
    
    for img in recent_images:
        print(f"\nID: {img.id} | Doc: {img.document_id} | File: {img.filename}")
        print(f"  public_url: {img.public_url}")
        print(f"  backend_path: {img.backend_path}")
        print(f"  frontend_path: {img.frontend_path}")
        
        # Check what type of URL it is
        if img.public_url.startswith('http'):
            print(f"  ✅ Remote object storage URL")
        elif img.public_url.startswith('/'):
            print(f"  ❌ LOCAL PATH (should be a remote object storage URL!)")
        else:
            print(f"  ⚠️  UNKNOWN FORMAT")
    
    print("\n" + "=" * 80)
    
    # Count by URL type
    all_images = ImportImage.query.all()
    spaces_count = sum(1 for img in all_images if img.public_url.startswith('http'))
    local_count = sum(1 for img in all_images if img.public_url.startswith('/'))
    
    print(f"TOTAL: {len(all_images)} images")
    print(f"  - Remote storage URLs: {spaces_count}")
    print(f"  - Local paths: {local_count}")
    print("=" * 80)
