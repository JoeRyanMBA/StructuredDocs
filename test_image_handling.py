#!/usr/bin/env python3
"""
Test script to verify image handling in Word and Markdown imports
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add backend to path
backend_path = os.environ.get('BACKEND_PATH')
if not backend_path:
    backend_path = str((Path(__file__).parent / 'backend').resolve())
sys.path.insert(0, backend_path)

# Set Flask app module
os.environ['FLASK_APP'] = 'backend.app'

from backend.app import create_app
from backend.models import db, ImportDocument, ImportImage
from backend.utils.image_handler import ImageHandler
from PIL import Image

def create_test_image(filename, size=(300, 200), color='red'):
    """Create a test image file"""
    img = Image.new('RGB', size, color)
    img.save(filename)
    return filename

def test_image_handler():
    """Test the ImageHandler functionality"""
    app = create_app()
    
    with app.app_context():
        print("🧪 Testing ImageHandler...")
        
        # Create a test import document
        test_doc = ImportDocument(
            filename='test_document.docx',
            source_type='word'
        )
        db.session.add(test_doc)
        db.session.commit()
        
        print(f"✅ Created test document with ID: {test_doc.id}")
        
        # Initialize image handler
        image_handler = ImageHandler(test_doc.id)
        
        # Create temporary test images
        temp_dir = tempfile.mkdtemp()
        temp_media_dir = os.path.join(temp_dir, 'media')
        os.makedirs(temp_media_dir, exist_ok=True)
        
        # Create test images
        test_images = [
            create_test_image(os.path.join(temp_media_dir, 'test1.png'), (200, 150), 'blue'),
            create_test_image(os.path.join(temp_media_dir, 'test2.jpg'), (400, 300), 'green'),
        ]
        
        print(f"✅ Created {len(test_images)} test images in {temp_media_dir}")
        
        # Test markdown content with image references
        markdown_content = """
# Test Document

This is a test document with images.

![Test Image 1](media/test1.png)

Some content here.

![Test Image 2](media/test2.jpg)

More content.
"""
        
        # Test image extraction and storage
        updated_markdown, stored_images = image_handler.extract_and_store_images(
            temp_media_dir, markdown_content
        )
        
        print(f"✅ Processed {len(stored_images)} images")
        
        # Verify images were stored
        for image_info in stored_images:
            print(f"  📄 Stored: {image_info['filename']} ({image_info['width']}x{image_info['height']})")
            
            # Save to database
            import_image = ImportImage(
                document_id=test_doc.id,
                filename=image_info['filename'],
                original_name=image_info['original_name'],
                public_url=image_info['public_url'],
                backend_path=image_info['backend_path'],
                frontend_path=image_info['frontend_path'],
                width=image_info['width'],
                height=image_info['height'],
                format=image_info['format'],
                file_size=image_info['file_size'],
                mime_type=image_info['mime_type']
            )
            db.session.add(import_image)
        
        db.session.commit()
        print("✅ Saved image metadata to database")
        
        # Test markdown validation
        validation_issues = image_handler.validate_markdown_images(updated_markdown)
        print(f"✅ Validation found {len(validation_issues)} issues")
        
        for issue in validation_issues:
            print(f"  ⚠️  {issue['message']}")
        
        # Test retrieving images
        retrieved_images = image_handler.get_import_images()
        print(f"✅ Retrieved {len(retrieved_images)} images from filesystem")
        
        # Verify database records
        db_images = ImportImage.query.filter_by(document_id=test_doc.id).all()
        print(f"✅ Found {len(db_images)} images in database")
        
        print("\n📋 Updated Markdown Content:")
        print("=" * 50)
        print(updated_markdown)
        print("=" * 50)
        
        # Clean up
        image_handler.cleanup_temp_images(temp_dir)
        
        # Clean up database
        ImportImage.query.filter_by(document_id=test_doc.id).delete()
        db.session.delete(test_doc)
        db.session.commit()
        
        print("✅ Test completed successfully!")

def test_markdown_validation():
    """Test markdown image validation without actual files"""
    app = create_app()
    
    with app.app_context():
        print("\n🧪 Testing Markdown Validation...")
        
        test_markdown = """
# Test Document

![Valid Image](/images/imports/123/valid.png)
![External Image](https://example.com/image.jpg)
![Missing Image](missing_image.png)
![Another Missing](./assets/missing.jpg)
"""
        
        image_handler = ImageHandler(999)  # Fake document ID
        issues = image_handler.validate_markdown_images(test_markdown)
        
        print(f"✅ Found {len(issues)} validation issues:")
        for issue in issues:
            print(f"  ⚠️  Line {issue['line']}: {issue['message']}")

if __name__ == '__main__':
    print("🚀 Starting Image Handler Tests...")
    test_image_handler()
    test_markdown_validation()
    print("🎉 All tests completed!")
