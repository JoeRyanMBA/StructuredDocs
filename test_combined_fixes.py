#!/usr/bin/env python3
"""
Test both blank line removal and list indentation fixes working together.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.routes.import_handler import _remove_all_blank_lines, _fix_list_indentation

def test_combined_fixes():
    """Test both fixes working together on realistic Word document content"""
    
    # Simulate content that might come from a Word document after Pandoc conversion
    problematic_content = """# Project Guidelines

This document outlines the project guidelines.

<!-- HTML comment from conversion -->

## Task List

The following tasks need to be completed:

- Task 1: Initial setup

  - Task 1.1: Configure environment

    - Task 1.1.1: Install dependencies

      - Task 1.1.2: Set environment variables

        - Task 1.1.3: Configure database

          - Task 1.1.4: This is too deeply nested

- Task 2: Development phase


  - Task 2.1: Write code

<p></p>

    - Task 2.2: Test functionality

&nbsp;

      - Task 2.3: This keeps getting more nested

## Numbered Instructions

1. First instruction

   2. Second instruction (nested)

     3. Third instruction (more nested)

<p>

</p>

       4. Fourth instruction (way too nested)

         5. This should not be so deeply indented

## Regular Content

This is just regular paragraph text.

It should remain unchanged.


<!-- Another comment -->

The end."""

    print("=== Combined Test: Realistic Word Document Content ===")
    print("ORIGINAL CONTENT:")
    print(problematic_content)
    print("\n" + "="*60)
    
    # Apply list indentation fix first
    print("\nStep 1: Fixing list indentation...")
    fixed_indentation = _fix_list_indentation(problematic_content)
    print("AFTER LIST INDENTATION FIX:")
    print(fixed_indentation)
    print("\n" + "="*60)
    
    # Apply blank line removal
    print("\nStep 2: Removing blank lines...")
    final_result = _remove_all_blank_lines(fixed_indentation)
    print("FINAL RESULT (after both fixes):")
    print(final_result)
    print("\n" + "="*60)
    
    # Show the transformation
    print("\nSUMMARY OF CHANGES:")
    original_lines = problematic_content.split('\n')
    final_lines = final_result.split('\n')
    
    print(f"- Lines reduced from {len(original_lines)} to {len(final_lines)}")
    print(f"- Blank lines removed: {original_lines.count('') + original_lines.count('   ') + original_lines.count('<p></p>')}")
    
    # Count list items to show indentation was fixed
    original_list_items = len([line for line in original_lines if line.strip().startswith(('-', '*', '+')) or re.match(r'^\s*\d+\.', line.strip())])
    final_list_items = len([line for line in final_lines if line.strip().startswith(('-', '*', '+')) or re.match(r'^\s*\d+\.', line.strip())])
    print(f"- List items processed: {original_list_items} -> {final_list_items}")

if __name__ == '__main__':
    import re
    test_combined_fixes()
