#!/usr/bin/env python3
"""
Test the image display fixes in the TopicEditor

This script creates test topics with problematic image markdown
to verify that the enhanced TopicEditor provides helpful warnings
and handles the issues correctly.
"""

import sys
sys.path.insert(0, '/workspaces/StructuredDocs')
sys.path.insert(0, '/workspaces/StructuredDocs/backend')

def create_test_topics():
    """Create test topics with various image issues"""
    
    print("🧪 Creating Test Topics with Image Issues")
    print("=" * 50)
    
    try:
        from backend.app import create_app
        from backend.models import Topic, db
        
        app = create_app()
        with app.app_context():
            
            # Test topic 1: Media paths with Pandoc attributes
            test_topic_1 = Topic(
                title="Test Topic - Media Paths & Pandoc Attributes",
                content="""# Process Diagrams

This topic demonstrates the image display issues you encountered:

Figure 2. Process flow diagram of the Informal Complaint Process (Under 29 C.F.R. 1614) Stage 1
![](media/image1.png){width="6.22369750656168in" height="4.611805555555556in"}

Figure 3. Process flow diagram of the Formal Complaint Process (Under 29 C.F.R. 1614) Stage 2
![](media/image2.emf)

These images won't display correctly in the WYSIWYG editor due to:
- media/ paths that don't resolve in browsers
- Pandoc-specific attribute syntax
- .emf format not supported by web browsers
""",
                frontmatter=""
            )
            
            # Test topic 2: Mixed image formats
            test_topic_2 = Topic(
                title="Test Topic - Mixed Image Formats",
                content="""# Mixed Image Examples

Good image (should work):
![Working Image](/images/sample.png)

Bad images (won't work):
![Bad Media Path](media/diagram.jpg){width="500px" height="300px"}
![EMF File](media/chart.emf)

These demonstrate the difference between working and non-working image markdown.
""",
                frontmatter=""
            )
            
            # Check if test topics already exist
            existing_1 = Topic.query.filter_by(title="Test Topic - Media Paths & Pandoc Attributes").first()
            existing_2 = Topic.query.filter_by(title="Test Topic - Mixed Image Formats").first()
            
            topics_created = 0
            
            if not existing_1:
                db.session.add(test_topic_1)
                topics_created += 1
                print("✅ Created test topic 1: Media Paths & Pandoc Attributes")
            else:
                print("ℹ️  Test topic 1 already exists")
            
            if not existing_2:
                db.session.add(test_topic_2)
                topics_created += 1
                print("✅ Created test topic 2: Mixed Image Formats")
            else:
                print("ℹ️  Test topic 2 already exists")
            
            if topics_created > 0:
                db.session.commit()
                print(f"\n🎉 Created {topics_created} test topics")
            else:
                print(f"\n📝 No new topics created (already exist)")
            
            return True
            
    except Exception as e:
        print(f"❌ Error creating test topics: {e}")
        return False

def test_fix_tool():
    """Test the fix tool on the created topics"""
    
    print(f"\n🔧 Testing Fix Tool on Created Topics")
    print("=" * 45)
    
    # Import and run the fix function
    try:
        from fix_image_display_tool import find_and_fix_image_issues
        
        # Run the fix (this will be interactive)
        print("Running image display fix tool...")
        success = find_and_fix_image_issues()
        
        if success:
            print("✅ Fix tool completed successfully")
        else:
            print("❌ Fix tool encountered issues")
            
        return success
        
    except Exception as e:
        print(f"❌ Error running fix tool: {e}")
        return False

def provide_testing_instructions():
    """Provide instructions for testing the fixes"""
    
    print(f"\n📋 Testing Instructions")
    print("=" * 30)
    
    instructions = """
To test the image display fixes:

1. **Start the Frontend Server:**
   ```bash
   cd /workspaces/StructuredDocs/frontend
   npm run dev
   ```

2. **Navigate to Test Topics:**
   - Go to the Topics page
   - Open "Test Topic - Media Paths & Pandoc Attributes"
   - Open "Test Topic - Mixed Image Formats"

3. **Check WYSIWYG Editor Behavior:**
   - Switch to WYSIWYG mode
   - You should see helpful warning messages for problematic images
   - Broken images should display with red dashed borders
   - Warning boxes should explain what's wrong and how to fix it

4. **Test Image Upload:**
   - Click the 🖼️ Image button
   - Upload a test image (use any .png, .jpg, or .gif file)
   - Verify it displays correctly in WYSIWYG mode

5. **Test the Fix Tool:**
   - Run the fix tool to convert problematic markdown
   - Check that media/ paths become /images/ paths
   - Verify Pandoc attributes are removed

Expected Results:
✅ Warning messages appear for problematic content
✅ Broken images show helpful error styling
✅ Image upload works and creates proper markdown
✅ Fix tool converts problematic patterns correctly
"""
    
    print(instructions)

def main():
    """Main function to set up testing environment"""
    
    print("🖼️  Image Display Fix Testing Setup")
    print("=" * 50)
    
    # Step 1: Create test topics
    success1 = create_test_topics()
    
    if success1:
        # Step 2: Provide testing instructions
        provide_testing_instructions()
        
        print(f"\n🎯 Next Steps:")
        print("   1. Start the frontend server to test the enhanced TopicEditor")
        print("   2. Open the test topics to see the new warning messages")
        print("   3. Try uploading images to see proper markdown generation")
        print("   4. Run the fix tool if you want to clean up the test content")
        
        return True
    else:
        return False

if __name__ == "__main__":
    main()