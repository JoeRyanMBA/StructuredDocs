#!/usr/bin/env python3
"""
Test script to verify hierarchy preservation in imports
"""
import sys
import os
sys.path.append('/workspaces/StructuredDocs/backend')

# Read the test markdown file
with open('/workspaces/StructuredDocs/test_hierarchy.md', 'r') as f:
    raw_content = f.read()

print("=== TESTING HIERARCHY PRESERVATION ===\n")

print("Original content:")
print(raw_content)
print("\n" + "="*50 + "\n")

# Simulate the parsing logic for both scenarios
def test_header_processing(preserve_hierarchy):
    print(f"Testing with preserve_hierarchy={preserve_hierarchy}")
    
    lines = []
    for line in raw_content.splitlines():
        if line.strip().startswith('#'):
            hash_count = len(line) - len(line.lstrip('#'))
            if not preserve_hierarchy and hash_count > 1:
                # Promote to H1
                content = line.lstrip('#').strip()
                line = f"# {content}"
                print(f"PROMOTED: '{line.strip()}' (was H{hash_count})")
            elif preserve_hierarchy:
                print(f"PRESERVED: '{line.strip()}' (level H{hash_count})")
        lines.append(line)
    
    # Now test the parsing logic
    paras = [('md', line) for line in lines]
    items = []
    buffer = []
    order = 0
    current_title = None
    
    def commit_buffer():
        nonlocal order, current_title, buffer
        if current_title:
            content = '\n'.join(buffer).strip()
            if content:
                items.append((order, current_title, content))
                print(f"COMMITTED: order={order}, title='{current_title}', content_len={len(content)}")
                order += 1
            buffer = []
    
    for style, text in paras:
        if preserve_hierarchy:
            is_heading = text.strip().startswith('#')
        else:
            is_heading = text.strip().startswith('#') and not text.strip().startswith('##')
        
        if is_heading:
            commit_buffer()
            current_title = text.strip().lstrip('#').strip()
            print(f"NEW_TITLE: '{current_title}'")
        else:
            buffer.append(text)
    
    # Commit final buffer
    commit_buffer()
    
    print(f"\nFinal result: {len(items)} topics created")
    for order, title, content in items:
        print(f"  {order+1}. {title} ({len(content)} chars)")
    
    print("\n" + "="*50 + "\n")

# Test both scenarios
test_header_processing(preserve_hierarchy=False)
test_header_processing(preserve_hierarchy=True)