#!/usr/bin/env python3
"""
Test the hierarchical parsing function
"""

def test_hierarchical_parsing():
    """Test hierarchical parsing with sample markdown"""
    
    # Sample markdown with hierarchy
    test_markdown = """# Main Topic

This is content for main topic.

## Subtopic 1

Content for subtopic 1.

### Sub-subtopic 1.1

Content for sub-subtopic 1.1.

## Subtopic 2

Content for subtopic 2.

# Another Main Topic

Content for another main topic.

## Another Subtopic

Content for another subtopic.
"""
    
    print("=== Testing Hierarchical Parsing ===")
    print(f"Input markdown ({len(test_markdown)} chars):")
    print(test_markdown)
    print("-" * 50)
    
    # Simulate the parsing logic
    hierarchical_items = []
    current_stack = []
    current_content = []
    
    for line in test_markdown.splitlines():
        stripped = line.strip()
        
        if stripped.startswith('#'):
            # This is a heading
            hash_count = len(line) - len(line.lstrip('#'))
            title = stripped.lstrip('#').strip()
            
            # Commit content to current item in stack
            if current_stack and current_content:
                content_text = '\n'.join(current_content).strip()
                if content_text:
                    current_stack[-1]['content'] = content_text
                current_content = []
            
            # Pop items from stack that are at same or deeper level
            while current_stack and current_stack[-1]['level'] >= hash_count:
                completed_item = current_stack.pop()
                hierarchical_items.append(completed_item)
            
            # Create new heading item
            heading_item = {
                'title': title,
                'level': hash_count,
                'content': '',
                'parent_index': None,
                'parent_level': current_stack[-1]['level'] if current_stack else None
            }
            
            current_stack.append(heading_item)
            print(f"HEADING: Level {hash_count} - '{title}' (parent_level: {heading_item['parent_level']})")
            
        else:
            # Regular content line
            current_content.append(line)
    
    # Process remaining items
    if current_stack and current_content:
        content_text = '\n'.join(current_content).strip()
        if content_text:
            current_stack[-1]['content'] = content_text
    
    hierarchical_items.extend(current_stack)
    
    # Fix parent relationships
    for i, item in enumerate(hierarchical_items):
        if item.get('parent_level') is not None:
            # Find the most recent item with the parent level
            for j in range(i - 1, -1, -1):
                if hierarchical_items[j]['level'] == item['parent_level']:
                    item['parent_index'] = j
                    break
        # Remove temporary field
        item.pop('parent_level', None)
    
    print(f"\nPARSING RESULTS: {len(hierarchical_items)} items created")
    print("-" * 50)
    
    # Display results
    for i, item in enumerate(hierarchical_items):
        parent_info = f" (parent: {item['parent_index']})" if item['parent_index'] is not None else " (root)"
        print(f"{i}. Level {item['level']}: '{item['title']}'{parent_info}")
        if item['content']:
            print(f"   Content: {item['content'][:50]}...")
    
    print("\nHIERARCHY VISUALIZATION:")
    print("-" * 50)
    
    # Show hierarchy structure
    def print_item(index, indent=0):
        item = hierarchical_items[index]
        prefix = "  " * indent + ("└─ " if indent > 0 else "")
        print(f"{prefix}[{index}] {item['title']} (Level {item['level']})")
        
        # Find children
        for i, child_item in enumerate(hierarchical_items):
            if child_item.get('parent_index') == index:
                print_item(i, indent + 1)
    
    # Print root items (no parent)
    for i, item in enumerate(hierarchical_items):
        if item.get('parent_index') is None:
            print_item(i)
    
    return hierarchical_items

if __name__ == '__main__':
    test_hierarchical_parsing()