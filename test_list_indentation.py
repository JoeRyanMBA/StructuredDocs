#!/usr/bin/env python3
"""
Test script to verify list indentation fixing functionality for Word document imports.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Import the function we just created
from backend.routes.import_handler import _fix_list_indentation

def test_list_indentation_fix():
    """Test the list indentation fix function with various problematic patterns"""
    
    # Test case 1: Progressive bullet indentation issue
    test_content_1 = """# List Example

Here are some items:

- Top level item
  - Second level item
    - Third level item
      - Fourth level item (too nested)
        - Fifth level item (too nested)
          - Sixth level item (too nested)

Regular paragraph text.

- Another top level item
    - This should be second level
        - This should be third level
            - This should stay at third level (capped)"""
    
    print("=== Test Case 1: Progressive bullet indentation ===")
    print("BEFORE:")
    print(test_content_1)
    
    result_1 = _fix_list_indentation(test_content_1)
    print("\nAFTER:")
    print(result_1)
    
    # Test case 2: Numbered lists with progressive indentation
    test_content_2 = """# Numbered List Example

Instructions:

1. First step
  2. Second step (nested)
    3. Third step (more nested)
      4. Fourth step (too nested)
        5. Fifth step (too nested)

1. New top level
    2. Should be nested level 1
        3. Should be nested level 2
            4. Should be capped at level 2"""
    
    print("\n\n=== Test Case 2: Progressive numbered list indentation ===")
    print("BEFORE:")
    print(test_content_2)
    
    result_2 = _fix_list_indentation(test_content_2)
    print("\nAFTER:")
    print(result_2)
    
    # Test case 3: Mixed lists with irregular spacing
    test_content_3 = """# Mixed List Example

- Item 1
      - Item 1.1 (over-indented)
            - Item 1.1.1 (way over-indented)
- Item 2
  - Item 2.1 (properly indented)
- Item 3

1. Step 1
        2. Step 1.1 (over-indented)
                3. Step 1.1.1 (way over-indented)
1. Step 2"""
    
    print("\n\n=== Test Case 3: Mixed lists with irregular spacing ===")
    print("BEFORE:")
    print(test_content_3)
    
    result_3 = _fix_list_indentation(test_content_3)
    print("\nAFTER:")
    print(result_3)

    # Test case 4: Regular text with no lists (should be unchanged)
    test_content_4 = """# Regular Text

This is just regular text.
No lists here.

Another paragraph.
- Just kidding, here's a list item
  - And a nested item"""
    
    print("\n\n=== Test Case 4: Regular text with minimal lists ===")
    print("BEFORE:")
    print(test_content_4)
    
    result_4 = _fix_list_indentation(test_content_4)
    print("\nAFTER:")
    print(result_4)

if __name__ == '__main__':
    test_list_indentation_fix()
