#!/usr/bin/env python3
"""
Test hierarchical import functionality
"""
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, '/workspaces/StructuredDocs/backend')

from flask import Flask
from models import db, Collection, Topic, Project
from routes.import_handler import _parse_hierarchical_structure
import io

# Create a minimal Flask app for testing
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////workspaces/StructuredDocs/structured_docs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)

def test_hierarchical_parsing():
    """Test the hierarchical parsing function"""
    
    # Create test markdown content simulating Word document conversion
    test_content = """# Main Topic

This is the content of the main topic.

## Subtopic 1

This is content under subtopic 1.

### Sub-subtopic 1.1

This is content under sub-subtopic 1.1.

## Subtopic 2

This is content under subtopic 2.

### Sub-subtopic 2.1

This is content under sub-subtopic 2.1.

### Sub-subtopic 2.2

This is content under sub-subtopic 2.2.

# Another Main Topic

This is the content of another main topic.

## Another Subtopic

This is content under another subtopic."""

    # Create a mock file object
    class MockFile:
        def __init__(self, content):
            self.content = content.encode('utf-8')
            self.filename = 'test_hierarchy.md'
            self.stream = io.BytesIO(self.content)
        
        def read(self):
            return self.content
    
    # Mock the _convert_word_to_markdown function for testing
    import routes.import_handler as import_handler
    original_convert = getattr(import_handler, '_convert_word_to_markdown', None)
    
    def mock_convert(content, doc_id):
        return test_content
    
    import_handler._convert_word_to_markdown = mock_convert
    
    try:
        # Test the hierarchical parsing
        mock_file = MockFile(test_content)
        hierarchical_items = _parse_hierarchical_structure(mock_file, 'word')
        
        print("=== HIERARCHICAL PARSING TEST ===")
        print(f"Total items parsed: {len(hierarchical_items)}")
        
        for i, item in enumerate(hierarchical_items):
            parent_info = f" (parent: {item['parent_index']})" if item['parent_index'] is not None else " (root)"
            print(f"{i}. Level {item['level']}: '{item['title']}'{parent_info}")
            if item['content']:
                print(f"   Content: {item['content'][:50]}...")
            print()
        
        print("=== HIERARCHY STRUCTURE ===")
        
        def print_hierarchy(items, parent_index=None, indent=0):
            for i, item in enumerate(items):
                if item['parent_index'] == parent_index:
                    prefix = "  " * indent + ("└─ " if indent > 0 else "")
                    print(f"{prefix}[{i}] {item['title']} (Level {item['level']})")
                    print_hierarchy(items, i, indent + 1)
        
        print_hierarchy(hierarchical_items)
        
    finally:
        # Restore original function if it existed
        if original_convert:
            import_handler._convert_word_to_markdown = original_convert

if __name__ == '__main__':
    with app.app_context():
        test_hierarchical_parsing()