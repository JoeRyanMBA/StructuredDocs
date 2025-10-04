#!/usr/bin/env python3
"""
Debug the hierarchical parsing parent index issue.
"""

import sys
import os
sys.path.insert(0, '/workspaces/StructuredDocs')
sys.path.insert(0, '/workspaces/StructuredDocs/backend')

def debug_hierarchical_parsing():
    """Debug the hierarchical parsing step by step"""
    
    print("🔍 Debugging Hierarchical Parsing")
    print("=" * 40)
    
    try:
        from backend.app import create_app
        from backend.routes.import_handler import _parse_hierarchical_content
        
        app = create_app()
        with app.app_context():
            # Test markdown with clear hierarchy
            test_markdown = """# Main Topic
This is main content.

## Subtopic A
This is subtopic A content.

### Sub-subtopic
This is sub-subtopic content.

## Subtopic B
This is subtopic B content.
"""
            
            print("📝 Testing markdown:")
            print(test_markdown)
            print("-" * 30)
            
            # Let's trace through the parsing manually
            lines = test_markdown.splitlines()
            hierarchical_items = []
            current_stack = []
            current_content = []
            
            print("🔄 Processing line by line:")
            
            for line_num, line in enumerate(lines):
                stripped = line.strip()
                print(f"Line {line_num + 1}: '{line}'")
                
                if stripped.startswith('#'):
                    # This is a heading
                    hash_count = len(line) - len(line.lstrip('#'))
                    title = stripped.lstrip('#').strip()
                    
                    print(f"  → Heading H{hash_count}: '{title}'")
                    
                    # Commit content to current item in stack
                    if current_stack and current_content:
                        content_text = '\n'.join(current_content).strip()
                        if content_text:
                            current_stack[-1]['content'] = content_text
                            print(f"    Committed content to '{current_stack[-1]['title']}'")
                        current_content = []
                    
                    # Pop items from stack that are at same or deeper level
                    while current_stack and current_stack[-1]['level'] >= hash_count:
                        completed_item = current_stack.pop()
                        hierarchical_items.append(completed_item)
                        print(f"    Completed item: '{completed_item['title']}' (level {completed_item['level']})")
                    
                    # Create new heading item
                    heading_item = {
                        'title': title,
                        'level': hash_count,
                        'content': '',
                        'parent_index': None
                    }
                    
                    # Set parent reference
                    if current_stack:
                        parent_item = current_stack[-1]
                        print(f"    Parent on stack: '{parent_item['title']}' (level {parent_item['level']})")
                        heading_item['parent_item'] = parent_item
                    else:
                        print(f"    No parent (root level)")
                    
                    current_stack.append(heading_item)
                    print(f"    Stack now has {len(current_stack)} items")
                    
                else:
                    # Content line
                    if stripped:  # Only add non-empty content
                        current_content.append(line)
                        print(f"  → Content: '{stripped}'")
            
            # Process remaining stack
            if current_stack and current_content:
                content_text = '\n'.join(current_content).strip()
                if content_text:
                    current_stack[-1]['content'] = content_text
                    print(f"Final content to '{current_stack[-1]['title']}'")
            
            while current_stack:
                completed_item = current_stack.pop()
                hierarchical_items.append(completed_item)
                print(f"Final completion: '{completed_item['title']}' (level {completed_item['level']})")
            
            print(f"\n📊 Before parent resolution:")
            for i, item in enumerate(hierarchical_items):
                has_parent_item = 'parent_item' in item
                print(f"  {i}: '{item['title']}' (level {item['level']}) - Has parent_item: {has_parent_item}")
            
            # Now resolve parent indices (corrected logic)
            print(f"\n🔗 Resolving parent indices:")
            for i, item in enumerate(hierarchical_items):
                if 'parent_item' in item:
                    parent_item = item['parent_item']
                    print(f"  Item {i} '{item['title']}' looking for parent '{parent_item['title']}' (level {parent_item['level']})")
                    
                    # Find the parent in the hierarchical_items list (it should appear AFTER this item)
                    found_parent = False
                    for j in range(i + 1, len(hierarchical_items)):
                        potential_parent = hierarchical_items[j]
                        if (potential_parent['title'] == parent_item['title'] and 
                            potential_parent['level'] == parent_item['level']):
                            item['parent_index'] = j
                            print(f"    → Found parent at index {j}")
                            found_parent = True
                            break
                    
                    if not found_parent:
                        print(f"    → Parent not found!")
                        
                    # Remove the temporary parent_item reference
                    del item['parent_item']
                else:
                    item['parent_index'] = None
                    print(f"  Item {i} '{item['title']}' is root level")
            
            print(f"\n✅ Final hierarchy:")
            for i, item in enumerate(hierarchical_items):
                level = item['level']
                parent_idx = item['parent_index']
                title = item['title']
                indent = "  " * (level - 1)
                parent_info = f" (parent: {parent_idx})" if parent_idx is not None else " (root)"
                print(f"{indent}{i}: H{level} {title}{parent_info}")
            
            return hierarchical_items
            
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    debug_hierarchical_parsing()