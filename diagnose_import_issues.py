#!/usr/bin/env python3
"""
Import Diagnostics Tool

This script helps diagnose why imports are not processing images correctly
and why hierarchical structure isn't being preserved.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, '/workspaces/StructuredDocs')
sys.path.insert(0, '/workspaces/StructuredDocs/backend')

def diagnose_import_issues():
    """Diagnose current import configuration and recent import activity"""
    
    print("🔍 Import Process Diagnostics")
    print("=" * 50)
    
    try:
        from backend.app import create_app
        from backend.models import Topic, ImportDocument, ImportImage, Collection, db
        
        app = create_app()
        with app.app_context():
            
            print("📊 1. Recent Import Activity Analysis")
            print("-" * 40)
            
            # Check recent imports
            recent_imports = ImportDocument.query.order_by(ImportDocument.created_at.desc()).limit(5).all()
            print(f"Recent imports: {len(recent_imports)}")
            
            for imp in recent_imports:
                print(f"\n📋 Import {imp.id}: {imp.filename}")
                print(f"   Created: {imp.created_at}")
                print(f"   Status: {imp.status}")
                
                # Check images processed
                images = ImportImage.query.filter_by(document_id=imp.id).all()
                print(f"   📸 Images processed: {len(images)}")
                
                if images:
                    for img in images[:2]:
                        print(f"      • {img.filename} → {img.public_url}")
            
            print(f"\n📊 2. Topics with Image Issues")
            print("-" * 40)
            
            # Find topics with media/ references (the problem)
            media_topics = Topic.query.filter(Topic.content.like('%media/%')).all()
            print(f"Topics with media/ paths: {len(media_topics)}")
            
            # Find topics that should have had image processing
            import re
            all_topics = Topic.query.order_by(Topic.created_at.desc()).limit(10).all()
            
            problematic_topics = []
            for topic in all_topics:
                issues = []
                
                # Check for media/ paths
                if 'media/' in topic.content:
                    issues.append("media/ paths")
                
                # Check for Pandoc attributes
                if re.search(r'\{[^}]*width[^}]*\}', topic.content):
                    issues.append("Pandoc attributes")
                
                # Check for .emf references
                if '.emf' in topic.content:
                    issues.append("EMF format")
                
                if issues:
                    problematic_topics.append((topic, issues))
            
            print(f"Topics with issues: {len(problematic_topics)}")
            
            for topic, issues in problematic_topics[:3]:
                print(f"\n❌ Topic: {topic.title}")
                print(f"   Issues: {', '.join(issues)}")
                print(f"   Created: {topic.created_at}")
                
                # Show sample problematic content
                lines = topic.content.split('\n')
                for i, line in enumerate(lines):
                    if any(pattern in line for pattern in ['media/', '.emf', '{width']):
                        print(f"   Line {i+1}: {line.strip()[:80]}...")
                        break
            
            print(f"\n📊 3. Collections and Hierarchical Import")
            print("-" * 40)
            
            collections = Collection.query.order_by(Collection.created_at.desc()).limit(3).all()
            print(f"Recent collections: {len(collections)}")
            
            for coll in collections:
                print(f"\n📚 Collection: {coll.name}")
                print(f"   Topics: {len(coll.topics)}")
                print(f"   Created: {coll.created_at}")
                
                # Check if collection topics have image issues
                collection_image_issues = 0
                for topic in coll.topics:
                    if 'media/' in topic.content or '.emf' in topic.content:
                        collection_image_issues += 1
                
                if collection_image_issues > 0:
                    print(f"   ⚠️  {collection_image_issues} topics with image issues")
                else:
                    print(f"   ✅ No image issues found")
            
            return True
            
    except Exception as e:
        print(f"❌ Error during diagnostics: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_import_function_config():
    """Verify that import functions are configured correctly"""
    
    print(f"\n🔧 Import Function Configuration Check")
    print("=" * 50)
    
    try:
        from backend.routes import import_handler
        import inspect
        
        # Check the key functions
        functions_to_check = [
            '_convert_word_to_markdown',
            '_parse_and_store', 
            '_parse_hierarchical_structure_with_images',
            '_import_as_topics'
        ]
        
        for func_name in functions_to_check:
            if hasattr(import_handler, func_name):
                func = getattr(import_handler, func_name)
                
                print(f"\n✅ {func_name}")
                
                # Check function signature
                sig = inspect.signature(func)
                params = list(sig.parameters.keys())
                print(f"   Parameters: {params}")
                
                # Check if it handles import_doc_id for image processing
                if 'import_doc_id' in params:
                    print(f"   ✅ Supports image processing (has import_doc_id)")
                else:
                    print(f"   ⚠️  No import_doc_id parameter")
                
                # Check source code for key patterns
                try:
                    source = inspect.getsource(func)
                    
                    if 'ImageHandler' in source:
                        print(f"   ✅ Uses ImageHandler")
                    
                    if '_convert_word_to_markdown(' in source and 'import_doc_id' in source:
                        print(f"   ✅ Calls image-enabled conversion")
                    
                    if 'media/' in source:
                        print(f"   📝 Mentions media/ paths")
                        
                except Exception as e:
                    print(f"   ⚠️  Could not analyze source: {e}")
            else:
                print(f"\n❌ {func_name} - NOT FOUND")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking functions: {e}")
        return False

def provide_import_recommendations():
    """Provide specific recommendations for fixing import issues"""
    
    print(f"\n💡 Import Issue Recommendations")
    print("=" * 50)
    
    recommendations = [
        "\n🎯 **For Image Processing Issues:**",
        "1. Ensure you're using hierarchical import (preserve_hierarchy=true)",
        "   - This calls _parse_hierarchical_structure_with_images()",
        "   - Regular import should also work but may have issues",
        "",
        "2. Check that your Word document contains embedded images",
        "   - Pandoc can only extract embedded images, not linked ones",
        "   - Images should be inserted directly into the document",
        "",
        "3. Verify file upload method:",
        "   - Use the Collection import feature for best results",
        "   - This automatically enables hierarchical processing",
        "",
        "\n🌲 **For Hierarchical Structure Issues:**",
        "1. Use Collection import instead of Topics import",
        "2. Ensure your document has proper heading structure (H1, H2, H3)",
        "3. Check that headings are formatted as Word styles, not just bold text",
        "",
        "\n🔧 **Immediate Action Items:**",
        "1. Run the fix tool to clean up existing problematic topics:",
        "   python fix_image_display_tool.py",
        "",
        "2. Re-import your document using Collection import:",
        "   - Go to Collections page",
        "   - Click 'Import Collection from Document'",
        "   - Upload your Word document",
        "   - This enables proper image and hierarchy processing",
        "",
        "3. Verify the import worked:",
        "   - Check that images use /images/imports/{id}/ paths",
        "   - Check that headings maintain their hierarchy",
        "   - Check that EMF files are converted to PNG"
    ]
    
    for rec in recommendations:
        print(rec)

def test_image_processing():
    """Test the image processing functions directly"""
    
    print(f"\n🧪 Image Processing Function Test")
    print("=" * 50)
    
    try:
        from backend.utils.image_handler import ImageHandler
        from backend.app import create_app
        
        app = create_app()
        with app.app_context():
            
            print("✅ ImageHandler class available")
            
            # Test instantiation
            test_handler = ImageHandler(999)  # Test import doc ID
            print(f"✅ ImageHandler can be instantiated")
            print(f"   Backend dir: {test_handler.backend_images_dir}")
            print(f"   Frontend dir: {test_handler.frontend_images_dir}")
            print(f"   Supported formats: {test_handler.SUPPORTED_FORMATS}")
            
            # Test markdown validation
            test_markdown = """
# Test Document
Here's an image:
![](media/image1.png){width="6in"}
Another image:
![](media/chart.emf)
"""
            
            issues = test_handler.validate_markdown_images(test_markdown)
            print(f"\n📝 Markdown validation test:")
            print(f"   Test markdown has {len(issues)} image issues")
            
            for issue in issues:
                print(f"   • {issue['type']}: {issue['message']}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error testing image processing: {e}")
        return False

def main():
    """Main diagnostics function"""
    
    print("🖼️  StructuredDocs Import Diagnostics")
    print("=" * 60)
    
    # Run all diagnostic checks
    success1 = diagnose_import_issues()
    success2 = check_import_function_config()
    success3 = test_image_processing()
    
    # Provide recommendations
    provide_import_recommendations()
    
    if success1 and success2 and success3:
        print(f"\n🎯 Diagnostics Summary:")
        print("✅ Import system appears to be configured correctly")
        print("✅ Image processing functions are available")
        print("✅ Most likely issue: using wrong import method or re-importing old content")
        
        print(f"\n📋 Next Steps:")
        print("1. Clean up existing problematic topics with the fix tool")
        print("2. Use Collection import (not Topics import) for new documents")
        print("3. Verify your Word document has embedded (not linked) images")
        
        return True
    else:
        print(f"\n❌ Some diagnostics failed - check the output above for issues")
        return False

if __name__ == "__main__":
    main()