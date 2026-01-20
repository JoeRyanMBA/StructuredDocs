#!/usr/bin/env python3
"""
Diagnostic tool to check why imported document content and images are missing.
Run this on your server to analyze the last import.
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, '/app')
sys.path.insert(0, '/app/backend')

def diagnose_import_issues():
    """Diagnose why imports are missing content/images"""
    print("🔍 Analyzing Import Issues")
    print("=" * 60)
    
    try:
        from backend.models import db, ImportDocument, ImportItem, ImportImage
        from flask import Flask
        import tempfile
        
        # Create a minimal Flask app for context
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
            'DATABASE_URL',
            'sqlite:////app/instance/structured_docs.db'
        )
        db.init_app(app)
        
        with app.app_context():
            print("\n📊 Database Statistics")
            print("-" * 60)
            
            # Check import documents
            total_imports = ImportDocument.query.count()
            print(f"Total ImportDocuments: {total_imports}")
            
            # Get the most recent import
            last_import = ImportDocument.query.order_by(ImportDocument.created_at.desc()).first()
            if not last_import:
                print("❌ No import documents found in database")
                return
            
            print(f"\n📄 Last Import: {last_import.filename}")
            print(f"   ID: {last_import.id}")
            print(f"   Created: {last_import.created_at}")
            print(f"   Source: {last_import.source_type}")
            
            # Check imported items
            items = ImportItem.query.filter_by(document_id=last_import.id).all()
            print(f"\n📝 Imported Content Items: {len(items)}")
            for item in items[:5]:  # Show first 5
                content_preview = item.content[:100] if item.content else "(empty)"
                print(f"   • {item.title}: {len(item.content or '')} chars")
                print(f"     Preview: {content_preview}...")
            
            if len(items) == 0:
                print("   ⚠️  NO CONTENT ITEMS FOUND - This is the problem!")
                print("   Likely causes:")
                print("      1. Pandoc conversion failed (check server logs)")
                print("      2. No H1 headings in the document")
                print("      3. Word document structure not supported")
            
            # Check images
            images = ImportImage.query.filter_by(document_id=last_import.id).all()
            print(f"\n🖼️  Imported Images: {len(images)}")
            
            for img in images[:5]:  # Show first 5
                exists_backend = os.path.exists(img.backend_path) if img.backend_path else False
                exists_frontend = os.path.exists(img.frontend_path) if img.frontend_path else False
                
                status = "✅" if (exists_backend or exists_frontend) else "❌"
                print(f"   {status} {img.filename}")
                print(f"      Backend: {img.backend_path}")
                print(f"         Exists: {exists_backend}")
                print(f"      Frontend: {img.frontend_path}")
                print(f"         Exists: {exists_frontend}")
            
            if len(images) == 0:
                print("   ⚠️  NO IMAGES FOUND - Check if images exist in document")
            
            print("\n" + "=" * 60)
            print("📋 Summary & Recommendations:")
            print("-" * 60)
            
            if len(items) == 0 and len(images) == 0:
                print("❌ Both content AND images are missing")
                print("\nLikely causes:")
                print("  1. Import parsing completely failed")
                print("  2. Check Docker logs: docker compose logs app | grep -i 'error\\|pandoc'")
                print("  3. Verify Pandoc is installed: docker exec structureddocs_app pandoc --version")
                print("  4. Try re-importing with a simpler Word document")
                
            elif len(items) == 0:
                print("❌ Content missing but images present")
                print("\nLikely causes:")
                print("  1. Document has no recognizable H1 headings (# Title format)")
                print("  2. Pandoc conversion failed for content")
                print("  3. Word document structure not compatible")
                
            elif len(images) == 0:
                print("❌ Content imported but images missing")
                print("\nLikely causes:")
                print("  1. Word document has no images")
                print("  2. Image extraction failed")
                print("  3. Volume mount not working: ls -la /opt/structureddocs/data/images/")
                print("  4. Check container logs for image extraction errors")
                
            else:
                print("✅ Import appears successful!")
                if any(not (os.path.exists(img.backend_path) if img.backend_path else False) for img in images):
                    print("\n⚠️  But some image files are missing from disk!")
                    print("   Check volume mount: docker compose logs app | grep -i 'image'")
            
    except Exception as e:
        print(f"❌ Diagnostic failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose_import_issues()
