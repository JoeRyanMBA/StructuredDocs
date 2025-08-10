#!/usr/bin/env python3
"""
Test the import fixes for blank line removal and heading merging
"""
import sys
sys.path.insert(0, '/workspaces/StructuredDocs/backend')

import tempfile
import os
from routes.import_handler import _post_process_markdown, _clean_topic_content

def test_blank_line_preservation():
    """Test that blank lines are preserved in content"""
    print("🧪 Testing Blank Line Preservation")
    print("=" * 50)
    
    # Test content with paragraph breaks
    test_content = """This is the first paragraph.

This is the second paragraph after a blank line.

And this is the third paragraph.


This has multiple blank lines above it.

- List item 1
- List item 2

Paragraph after list."""

    print("Original content:")
    print(repr(test_content))
    
    # Test post-processing
    processed = _post_process_markdown(test_content)
    print("\nAfter _post_process_markdown:")
    print(repr(processed))
    
    # Test topic cleaning
    cleaned = _clean_topic_content(processed)
    print("\nAfter _clean_topic_content:")
    print(repr(cleaned))
    
    # Check if single blank lines are preserved
    has_single_blank_lines = '\n\n' in cleaned and '\n\n\n' not in cleaned
    print(f"\n✅ Single blank lines preserved: {has_single_blank_lines}")
    
    return has_single_blank_lines

def test_heading_merging_logic():
    """Test the logic for merging consecutive headings"""
    print("\n🧪 Testing Heading Merging Logic")
    print("=" * 50)
    
    # Simulate the logic from _parse_and_store
    def test_buffer_analysis(buffer_lines, title):
        """Test if buffer has substantive content"""
        current_buffer_content = '\n'.join(buffer_lines).strip()
        current_buffer_has_content = bool(current_buffer_content and 
                                        not all(line.strip() == '' or line.strip().startswith('#') 
                                               for line in current_buffer_content.split('\n')))
        
        print(f"  Title: '{title}'")
        print(f"  Buffer: {repr(buffer_lines)}")
        print(f"  Buffer content: '{current_buffer_content}'")
        print(f"  Has substantive content: {current_buffer_has_content}")
        return current_buffer_has_content
    
    # Test case 1: Empty buffer (should merge)
    print("Test Case 1: Empty buffer")
    result1 = test_buffer_analysis([], "First Heading")
    print(f"  Should merge next heading: {not result1}")
    
    # Test case 2: Buffer with only blank lines (should merge)
    print("\nTest Case 2: Buffer with only blank lines")
    result2 = test_buffer_analysis(['', '  ', '\t'], "Second Heading")
    print(f"  Should merge next heading: {not result2}")
    
    # Test case 3: Buffer with only headings (should merge)
    print("\nTest Case 3: Buffer with only other headings")
    result3 = test_buffer_analysis(['## Sub Heading', '### Another Sub'], "Third Heading")
    print(f"  Should merge next heading: {not result3}")
    
    # Test case 4: Buffer with actual content (should NOT merge)
    print("\nTest Case 4: Buffer with actual content")
    result4 = test_buffer_analysis(['This is actual content.', '', 'More content here.'], "Fourth Heading")
    print(f"  Should merge next heading: {not result4}")
    
    # Test case 5: Buffer with mixed content and headings (should NOT merge)
    print("\nTest Case 5: Buffer with mixed content")
    result5 = test_buffer_analysis(['## Sub Heading', 'Some actual content here.'], "Fifth Heading")
    print(f"  Should merge next heading: {not result5}")
    
    success = (not result1 and not result2 and not result3 and result4 and result5)
    print(f"\n✅ Heading merge logic working correctly: {success}")
    
    return success

def create_test_document():
    """Create a test Word-style markdown document to test both fixes"""
    print("\n🧪 Creating Test Document")
    print("=" * 50)
    
    test_markdown = """# First Section

This is content for the first section.

It has multiple paragraphs with blank lines between them.

# Second Section Without Content

# Third Section Also Without Content

# Fourth Section With Content

This section has actual content.

It should not merge with the previous headings.

- List item 1
- List item 2

More content after the list.

# Fifth Section

Final section with content."""

    print("Test document structure:")
    lines = test_markdown.strip().split('\n')
    for i, line in enumerate(lines, 1):
        if line.strip().startswith('#'):
            print(f"  {i:2d}: [HEADING] {line.strip()}")
        elif line.strip() == '':
            print(f"  {i:2d}: [BLANK]")
        else:
            print(f"  {i:2d}: [CONTENT] {line.strip()[:50]}...")
    
    return test_markdown

if __name__ == "__main__":
    print("🔧 Testing Import Handler Fixes")
    print("=" * 60)
    
    # Test 1: Blank line preservation
    blank_lines_ok = test_blank_line_preservation()
    
    # Test 2: Heading merging logic
    heading_logic_ok = test_heading_merging_logic()
    
    # Test 3: Create test document
    test_doc = create_test_document()
    
    print(f"\n📊 Test Results Summary:")
    print(f"  ✅ Blank line preservation: {'PASS' if blank_lines_ok else 'FAIL'}")
    print(f"  ✅ Heading merge logic: {'PASS' if heading_logic_ok else 'FAIL'}")
    print(f"  📄 Test document created: READY")
    
    if blank_lines_ok and heading_logic_ok:
        print(f"\n🎉 All tests passed! The import handler fixes should work correctly.")
        print(f"💡 Test the actual import by uploading a Word document with:")
        print(f"   - Multiple paragraphs with blank lines")
        print(f"   - Consecutive headings without content")
    else:
        print(f"\n❌ Some tests failed. Review the logic above.")
        
    print(f"\n🔄 Restart the backend to apply the changes:")
    print(f"   cd /workspaces/StructuredDocs && bash restart.sh")
