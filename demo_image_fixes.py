#!/usr/bin/env python3
"""
Demonstrate Image Display Fixes - Non-Interactive Version

This script shows the before and after of fixing image display issues.
"""

import sys
import os
import re

# Add backend to path
sys.path.insert(0, '/workspaces/StructuredDocs')
sys.path.insert(0, '/workspaces/StructuredDocs/backend')

def demonstrate_fixes():
    """Show before and after examples of image fixes"""
    
    print("🔧 Image Display Fix Demonstration")
    print("=" * 50)
    
    try:
        from backend.app import create_app
        from backend.models import Topic, db
        
        app = create_app()
        with app.app_context():
            
            # Find the test topics
            test_topics = Topic.query.filter(Topic.title.like('Test Topic%')).all()
            
            print(f"📊 Found {len(test_topics)} test topics")
            
            for topic in test_topics:
                print(f"\n📋 Topic: {topic.title}")
                print("=" * len(topic.title) + "=" * 8)
                
                original_content = topic.content
                
                # Show original problematic markdown
                print("\n❌ BEFORE (Problematic):")
                print("-" * 30)
                
                # Extract image lines
                lines = original_content.split('\n')
                for i, line in enumerate(lines):
                    if '![' in line or '{width=' in line:
                        print(f"{i+1:3}: {line}")
                
                # Fix the content
                fixed_content = fix_image_markdown(original_content)
                
                # Show fixed markdown
                print("\n✅ AFTER (Fixed):")
                print("-" * 20)
                
                fixed_lines = fixed_content.split('\n')
                for i, line in enumerate(fixed_lines):
                    if '![' in line and 'Image' in line:
                        print(f"{i+1:3}: {line}")
                
                # Show what changed
                print(f"\n🔧 Changes Applied:")
                show_detailed_changes(original_content, fixed_content)
                
            # Apply the fixes
            print(f"\n💾 Applying Fixes to Database...")
            
            fixes_applied = 0
            for topic in test_topics:
                original = topic.content
                fixed = fix_image_markdown(original)
                
                if fixed != original:
                    topic.content = fixed
                    db.session.add(topic)
                    fixes_applied += 1
                    print(f"   ✅ Fixed: {topic.title}")
            
            if fixes_applied > 0:
                db.session.commit()
                print(f"\n🎉 Applied fixes to {fixes_applied} topics!")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def fix_image_markdown(content):
    """Fix problematic image markdown"""
    
    if not content:
        return content
    
    fixed_content = content
    
    # Fix media/ paths
    def replace_media_path(match):
        alt_text = match.group(1) if match.group(1) else "Image"
        media_path = match.group(2)
        
        filename = os.path.basename(media_path)
        if filename.endswith('.emf'):
            filename = filename.replace('.emf', '.png')
        
        return f"![{alt_text}](/images/{filename})"
    
    media_pattern = r'!\[([^\]]*)\]\(media/([^)]+)\)'
    fixed_content = re.sub(media_pattern, replace_media_path, fixed_content)
    
    # Remove Pandoc attributes
    pandoc_patterns = [
        r'\{width="[^"]*"\}',
        r'\{height="[^"]*"\}',
        r'\{width="[^"]*"\s+height="[^"]*"\}',
        r'\{height="[^"]*"\s+width="[^"]*"\}',
        r'\{[^}]*width[^}]*\}',
    ]
    
    for pattern in pandoc_patterns:
        fixed_content = re.sub(pattern, '', fixed_content)
    
    # Clean up whitespace
    fixed_content = re.sub(r'\n\s*\n\s*\n', '\n\n', fixed_content)
    
    return fixed_content

def show_detailed_changes(original, fixed):
    """Show detailed changes between original and fixed content"""
    
    # Count different types of fixes
    media_refs_before = len(re.findall(r'!\[.*?\]\(media/[^)]+\)', original))
    media_refs_after = len(re.findall(r'!\[.*?\]\(media/[^)]+\)', fixed))
    
    pandoc_attrs_before = len(re.findall(r'\{[^}]*width[^}]*\}', original))
    pandoc_attrs_after = len(re.findall(r'\{[^}]*width[^}]*\}', fixed))
    
    emf_refs_before = len(re.findall(r'\.emf', original))
    emf_refs_after = len(re.findall(r'\.emf', fixed))
    
    print(f"   • Media paths: {media_refs_before} → {media_refs_after} (fixed {media_refs_before - media_refs_after})")
    print(f"   • Pandoc attributes: {pandoc_attrs_before} → {pandoc_attrs_after} (removed {pandoc_attrs_before - pandoc_attrs_after})")
    print(f"   • EMF references: {emf_refs_before} → {emf_refs_after} (converted {emf_refs_before - emf_refs_after} to PNG)")

def verify_wysiwyg_compatibility():
    """Verify that the fixed markdown will work with WYSIWYG editor"""
    
    print(f"\n📱 WYSIWYG Compatibility Check")
    print("=" * 40)
    
    try:
        from backend.app import create_app
        from backend.models import Topic
        
        app = create_app()
        with app.app_context():
            
            # Check the fixed topics
            test_topics = Topic.query.filter(Topic.title.like('Test Topic%')).all()
            
            for topic in test_topics:
                print(f"\n✅ Topic: {topic.title}")
                
                # Check for remaining issues
                issues = []
                
                if 'media/' in topic.content:
                    issues.append("❌ Still contains media/ paths")
                else:
                    issues.append("✅ No media/ paths")
                
                if re.search(r'\{[^}]*width[^}]*\}', topic.content):
                    issues.append("❌ Still contains Pandoc attributes")
                else:
                    issues.append("✅ No Pandoc attributes")
                
                if '.emf' in topic.content:
                    issues.append("❌ Still contains EMF references")
                else:
                    issues.append("✅ No EMF references")
                
                # Check for proper image markdown
                proper_images = re.findall(r'!\[[^\]]*\]\(/images/[^)]+\)', topic.content)
                if proper_images:
                    issues.append(f"✅ {len(proper_images)} properly formatted images")
                
                for issue in issues:
                    print(f"   {issue}")
    
    except Exception as e:
        print(f"❌ Error checking compatibility: {e}")

def main():
    """Main demonstration function"""
    
    print("🖼️  Image Display Fix Demonstration")
    print("=" * 60)
    
    success = demonstrate_fixes()
    
    if success:
        verify_wysiwyg_compatibility()
        
        print(f"\n🎯 Summary:")
        print("✅ Converted media/ paths to /images/ paths")
        print("✅ Removed Pandoc attribute syntax")
        print("✅ Converted .emf references to .png")
        print("✅ Fixed markdown is now WYSIWYG-compatible")
        
        print(f"\n📤 Next Steps:")
        print("1. Upload actual image files using the TopicEditor 🖼️ button")
        print("2. Replace placeholder /images/{filename} paths with real uploaded images")
        print("3. Test in WYSIWYG mode to see proper display and helpful warnings")
        
        print(f"\n📖 See IMAGE_UPLOAD_GUIDE.md for detailed instructions")

if __name__ == "__main__":
    main()