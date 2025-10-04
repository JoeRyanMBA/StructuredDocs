#!/usr/bin/env python3
"""
Image Display Fix Tool - Automatically fix image display issues in existing topics

This script will:
1. Find topics with problematic image markdown
2. Fix the image paths and syntax
3. Provide options for manual image upload if needed
"""

import sys
import os
import re
from pathlib import Path

# Add backend to path
sys.path.insert(0, '/workspaces/StructuredDocs')
sys.path.insert(0, '/workspaces/StructuredDocs/backend')

def find_and_fix_image_issues():
    """Find topics with image display issues and fix them"""
    
    print("🔧 StructuredDocs Image Display Fix Tool")
    print("=" * 60)
    
    try:
        from backend.app import create_app
        from backend.models import Topic, db
        from backend.extensions import db as db_ext
        
        app = create_app()
        with app.app_context():
            
            # Find all topics with potential image issues
            print("🔍 Scanning for topics with image display issues...")
            
            # Search for various problematic patterns
            problematic_patterns = [
                "media/",           # Pandoc media paths
                ".emf",            # EMF files
                r"\{width=",       # Pandoc width attributes
                r"\{height=",      # Pandoc height attributes
            ]
            
            topics_to_fix = []
            
            for pattern in problematic_patterns:
                if pattern.startswith('\\'):
                    # Regex pattern
                    topics = Topic.query.filter(Topic.content.op('REGEXP')(pattern)).all()
                else:
                    # Simple string pattern
                    topics = Topic.query.filter(Topic.content.like(f'%{pattern}%')).all()
                
                for topic in topics:
                    if topic.id not in [t.id for t in topics_to_fix]:
                        topics_to_fix.append(topic)
            
            print(f"📊 Found {len(topics_to_fix)} topics with image issues")
            
            if not topics_to_fix:
                print("✅ No topics found with image display issues!")
                return True
            
            # Process each topic
            fixes_applied = 0
            
            for i, topic in enumerate(topics_to_fix, 1):
                print(f"\n📋 Processing Topic {i}/{len(topics_to_fix)}: {topic.title}")
                print(f"   Topic ID: {topic.id}")
                
                # Analyze the content
                original_content = topic.content
                fixed_content = fix_image_markdown(original_content)
                
                if fixed_content != original_content:
                    print("   🔧 Issues found and fixed:")
                    
                    # Show what changed
                    show_changes(original_content, fixed_content)
                    
                    # Ask user if they want to apply the fix
                    response = input(f"   Apply fix to '{topic.title}'? (y/n/a=all): ").lower().strip()
                    
                    if response in ['y', 'yes', 'a', 'all']:
                        topic.content = fixed_content
                        db.session.add(topic)
                        fixes_applied += 1
                        print("   ✅ Fix applied!")
                        
                        if response in ['a', 'all']:
                            # Apply to all remaining topics
                            for remaining_topic in topics_to_fix[i:]:
                                if remaining_topic.id != topic.id:
                                    remaining_fixed = fix_image_markdown(remaining_topic.content)
                                    if remaining_fixed != remaining_topic.content:
                                        remaining_topic.content = remaining_fixed
                                        db.session.add(remaining_topic)
                                        fixes_applied += 1
                                        print(f"   ✅ Auto-applied fix to '{remaining_topic.title}'")
                            break
                    else:
                        print("   ⏭️  Skipped")
                else:
                    print("   ℹ️  No fixable issues found (may need manual image upload)")
            
            # Commit changes
            if fixes_applied > 0:
                try:
                    db.session.commit()
                    print(f"\n🎉 Successfully applied fixes to {fixes_applied} topics!")
                except Exception as e:
                    db.session.rollback()
                    print(f"\n❌ Error saving changes: {e}")
                    return False
            else:
                print(f"\n📝 No changes were applied")
            
            # Provide next steps
            provide_next_steps(topics_to_fix, fixes_applied)
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def fix_image_markdown(content):
    """Fix problematic image markdown in content"""
    
    if not content:
        return content
    
    fixed_content = content
    
    # 1. Fix media/ paths to /images/ paths
    def replace_media_path(match):
        alt_text = match.group(1) if match.group(1) else "Image"
        media_path = match.group(2)
        
        # Extract filename and convert .emf to .png
        filename = os.path.basename(media_path)
        if filename.endswith('.emf'):
            filename = filename.replace('.emf', '.png')
        
        # Create a placeholder path - user will need to upload the actual image
        new_path = f"/images/{filename}"
        return f"![{alt_text}]({new_path})"
    
    # Apply media path fixes
    media_pattern = r'!\[([^\]]*)\]\(media/([^)]+)\)'
    fixed_content = re.sub(media_pattern, replace_media_path, fixed_content)
    
    # 2. Remove Pandoc attributes
    pandoc_attrs_patterns = [
        r'\{width="[^"]*"\}',
        r'\{height="[^"]*"\}',
        r'\{width="[^"]*"\s+height="[^"]*"\}',
        r'\{height="[^"]*"\s+width="[^"]*"\}',
        r'\{[^}]*width[^}]*\}',  # Any block containing width
    ]
    
    for pattern in pandoc_attrs_patterns:
        fixed_content = re.sub(pattern, '', fixed_content)
    
    # 3. Clean up extra whitespace
    fixed_content = re.sub(r'\n\s*\n\s*\n', '\n\n', fixed_content)
    
    return fixed_content

def show_changes(original, fixed):
    """Show what changes will be applied"""
    
    # Find image references in both
    original_images = re.findall(r'!\[.*?\]\([^)]+\)', original)
    fixed_images = re.findall(r'!\[.*?\]\([^)]+\)', fixed)
    
    # Show Pandoc attributes that will be removed
    pandoc_attrs = re.findall(r'\{[^}]*width[^}]*\}', original)
    
    if original_images != fixed_images:
        print("      📎 Image references:")
        for i, (orig, fix) in enumerate(zip(original_images, fixed_images)):
            if orig != fix:
                print(f"         - '{orig}' → '{fix}'")
    
    if pandoc_attrs:
        print(f"      🗑️  Will remove {len(pandoc_attrs)} Pandoc attribute blocks")

def provide_next_steps(topics_to_fix, fixes_applied):
    """Provide guidance on next steps"""
    
    print(f"\n📋 Next Steps:")
    print("=" * 30)
    
    if fixes_applied > 0:
        print("✅ Markdown syntax has been fixed for proper WYSIWYG display")
        print("\n🔄 Still needed:")
        print("   1. Upload the actual image files using the TopicEditor image upload feature")
        print("   2. The fixed markdown now uses /images/{filename} paths")
        print("   3. When you upload images, they'll be accessible at those paths")
        
    print(f"\n💡 For images that still don't display:")
    print("   • Use the 🖼️ Image button in the TopicEditor")
    print("   • Upload your image files (convert .emf to .png first)")
    print("   • The editor will insert the correct markdown automatically")
    
    print(f"\n🔧 Alternative: Re-import with proper image processing")
    print("   • If you have the original document with images")
    print("   • Use the hierarchical import feature")
    print("   • Images will be automatically processed and stored correctly")

def create_image_upload_guide():
    """Create a guide for manual image upload"""
    
    guide_content = """# Image Upload Guide

## For Images That Don't Display in WYSIWYG Editor

### Quick Fix Steps:

1. **Open the Topic Editor**
   - Navigate to the topic with missing images
   - Switch to markdown mode to see the image references

2. **Upload Images Manually**
   - Click the 🖼️ Image button in the editor toolbar
   - Upload your image files (must be web formats: .png, .jpg, .gif, .webp)
   - For .emf files: convert them to .png first using an image editor

3. **Replace the Markdown**
   - Delete the old image markdown (e.g., `![](media/image1.png)`)
   - The upload will insert correct markdown (e.g., `![Image](/images/filename.png)`)

4. **Switch to WYSIWYG Mode**
   - Images should now display correctly
   - WYSIWYG editor can render standard markdown image syntax

### Why This Was Needed:

- `media/` paths don't work in web browsers
- `{width="..."}` syntax is Pandoc-specific, not standard markdown
- `.emf` files are not web-compatible formats

### Correct Image Markdown Format:
```markdown
![Alt Text](/images/filename.png)
```

### Avoid These Formats:
```markdown
![](media/image.png){width="6in" height="4in"}  ❌
![](image.emf)                                   ❌
```
"""
    
    try:
        with open('/workspaces/StructuredDocs/IMAGE_UPLOAD_GUIDE.md', 'w') as f:
            f.write(guide_content)
        print(f"\n📖 Created IMAGE_UPLOAD_GUIDE.md for reference")
    except Exception as e:
        print(f"\n⚠️  Could not create guide file: {e}")

def main():
    """Main function"""
    
    success = find_and_fix_image_issues()
    
    if success:
        create_image_upload_guide()
        print(f"\n🎯 Summary:")
        print("   ✅ Fixed markdown syntax for WYSIWYG compatibility")
        print("   📤 Next: Upload actual image files using the TopicEditor")
        print("   📖 See IMAGE_UPLOAD_GUIDE.md for detailed instructions")
    
    return success

if __name__ == "__main__":
    main()