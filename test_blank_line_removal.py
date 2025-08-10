#!/usr/bin/env python3
"""
Test script to verify blank line removal functionality for Word document imports.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Import the function we just created
from backend.routes.import_handler import _remove_all_blank_lines

def test_blank_line_removal():
    """Test the blank line removal function with various content types"""
    
    # Test case 1: Content with multiple blank lines
    test_content_1 = """# Heading 1

This is some content.


Another paragraph.

    
Yet another paragraph.


## Subheading

More content here.

"""
    
    print("=== Test Case 1: Content with multiple blank lines ===")
    print("BEFORE:")
    print(repr(test_content_1))
    
    result_1 = _remove_all_blank_lines(test_content_1)
    print("\nAFTER:")
    print(repr(result_1))
    print("\nFormatted output:")
    print(result_1)
    
    # Test case 2: Content with HTML artifacts and blank lines
    test_content_2 = """# Introduction

This is the introduction.

<p></p>

Some more content.

&nbsp;

<p>

</p>

Final paragraph.
"""
    
    print("\n\n=== Test Case 2: Content with HTML artifacts and blank lines ===")
    print("BEFORE:")
    print(repr(test_content_2))
    
    result_2 = _remove_all_blank_lines(test_content_2)
    print("\nAFTER:")
    print(repr(result_2))
    print("\nFormatted output:")
    print(result_2)
    
    # Test case 3: Content with list items and blank lines
    test_content_3 = """# List Example

Here are some items:

- Item 1

- Item 2


- Item 3

1. Numbered item 1

2. Numbered item 2


3. Numbered item 3
"""
    
    print("\n\n=== Test Case 3: Content with list items and blank lines ===")
    print("BEFORE:")
    print(repr(test_content_3))
    
    result_3 = _remove_all_blank_lines(test_content_3)
    print("\nAFTER:")
    print(repr(result_3))
    print("\nFormatted output:")
    print(result_3)
    
    # Test case 4: Edge case - only blank lines and whitespace
    test_content_4 = """

   

&nbsp;

<p></p>

    
"""
    
    print("\n\n=== Test Case 4: Only blank lines and whitespace ===")
    print("BEFORE:")
    print(repr(test_content_4))
    
    result_4 = _remove_all_blank_lines(test_content_4)
    print("\nAFTER:")
    print(repr(result_4))
    print("\nFormatted output:")
    print(f"'{result_4}'")

if __name__ == '__main__':
    test_blank_line_removal()
