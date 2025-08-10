#!/usr/bin/env python3
"""
Test script to diagnose Word document import issues
"""

import sys
import os
sys.path.append('/workspaces/StructuredDocs/backend')

from routes.import_handler import _convert_word_to_markdown, _parse_and_store
from models import ImportDocument, ImportItem, db
from app import create_app
import tempfile

def test_word_conversion():
    """Test Word to Markdown conversion"""
    print("🔧 Testing Word document conversion...")
    
    # Load the test Word document
    test_docx_path = '/workspaces/StructuredDocs/backend/static/SC-50, Special Census Office Manual.docx'
    
    if not os.path.exists(test_docx_path):
        print(f"❌ Test file not found: {test_docx_path}")
        return False
    
    print(f"📁 Loading test file: {test_docx_path}")
    
    # Create Flask app context for the conversion
    app = create_app()
    
    with app.app_context():
        try:
            with open(test_docx_path, 'rb') as f:
                file_content = f.read()
            
            print(f"📊 File size: {len(file_content)} bytes")
            
            # Test conversion
            print("🔄 Converting Word to Markdown...")
            markdown_content = _convert_word_to_markdown(file_content, 9999)  # Use dummy ID
            
            print(f"✅ Conversion successful!")
            print(f"📝 Markdown length: {len(markdown_content)} characters")
            
            # Show first 500 characters
            print("\n📋 First 500 characters of converted Markdown:")
            print("-" * 50)
            print(markdown_content[:500])
            print("-" * 50)
            
            # Count headings
            lines = markdown_content.split('\n')
            h1_count = len([line for line in lines if line.strip().startswith('# ') and not line.strip().startswith('## ')])
            h2_count = len([line for line in lines if line.strip().startswith('## ')])
            h3_count = len([line for line in lines if line.strip().startswith('### ')])
            
            print(f"\n📊 Heading analysis:")
            print(f"  H1 headings: {h1_count}")
            print(f"  H2 headings: {h2_count}")
            print(f"  H3 headings: {h3_count}")
            
            if h1_count == 0:
                print("⚠️  WARNING: No H1 headings found! This will result in 'No content items found'")
                print("📝 The document structure might need manual inspection.")
                
                # Show some sample lines to help diagnose
                print("\n📋 Sample lines from the document:")
                for i, line in enumerate(lines[:20]):
                    if line.strip():
                        print(f"  {i+1:2d}: {line}")
            
            return True
            
        except Exception as e:
            print(f"❌ Conversion failed: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_parsing_logic():
    """Test the parsing logic with a sample markdown"""
    print("\n🔧 Testing parsing logic...")
    
    # Create a test app context
    app = create_app()
    
    with app.app_context():
        try:
            # Create a temporary import document
            test_imp_doc = ImportDocument(
                filename='test_document.docx',
                source_type='word'
            )
            db.session.add(test_imp_doc)
            db.session.flush()  # Get the ID
            
            print(f"📁 Created test ImportDocument with ID: {test_imp_doc.id}")
            
            # Create a test file-like object with some markdown content
            test_markdown = """# Introduction
This is the introduction section with some content.

# Main Section
This is the main section with more detailed content.
It has multiple paragraphs.

# Conclusion
This is the conclusion section.
"""
            
            class MockFile:
                def __init__(self, content):
                    self.content = content.encode('utf-8')
                    self.stream = self
                    self.position = 0
                
                def read(self):
                    return self.content
                
                def seek(self, pos):
                    self.position = pos
                
                def decode(self, encoding='utf-8'):
                    return self.content.decode(encoding)
            
            mock_file = MockFile(test_markdown)
            
            # Test the parsing function
            print("🔄 Testing _parse_and_store with mock data...")
            _parse_and_store(mock_file, test_imp_doc, 'markdown')
            
            # Check the results
            items = ImportItem.query.filter_by(document_id=test_imp_doc.id).all()
            print(f"✅ Created {len(items)} import items:")
            
            for item in items:
                print(f"  📝 {item.heading_order}: '{item.title}' ({len(item.content)} chars)")
            
            # Clean up
            db.session.rollback()
            
            return len(items) > 0
            
        except Exception as e:
            print(f"❌ Parsing test failed: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False

if __name__ == "__main__":
    print("🚀 Starting Word Import Diagnostic Tests")
    print("=" * 50)
    
    # Test 1: Word conversion
    conversion_success = test_word_conversion()
    
    # Test 2: Parsing logic
    parsing_success = test_parsing_logic()
    
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"  Word Conversion: {'✅ PASS' if conversion_success else '❌ FAIL'}")
    print(f"  Parsing Logic:   {'✅ PASS' if parsing_success else '❌ FAIL'}")
    
    if conversion_success and parsing_success:
        print("\n🎉 All tests passed! The issue may be elsewhere.")
    else:
        print("\n⚠️  Issues found. Check the output above for details.")
