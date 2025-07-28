#!/usr/bin/env python3

import re

def test_markdown_parsing():
    # Test markdown content
    markdown_content = """# First Header
This is some content under the first header.
Another line of content.

# Second Header
Content for the second section.
More content here.

## This is H2, should be ignored
Some content under H2.

# Third Header
Final section content.
"""

    # Simulate the parsing logic
    source = 'markdown'
    paras = [('md', line) for line in markdown_content.splitlines()]
    
    items, buffer, order, current_title = [], [], 0, None
    
    def commit_buffer():
        nonlocal order, current_title, buffer
        if current_title:
            content = '\n'.join(buffer).strip()
            items.append((order, current_title, content))
            print(f"COMMITTED: order={order}, title='{current_title}', content_len={len(content)}")
            order += 1
            buffer = []

    print(f"PARSING: source={source}, lines={len(paras)}")
    
    for style, text in paras:
        is_h1 = (
            source == 'word' and style.startswith('Heading 1')
        ) or (
            source == 'markdown' and re.match(r'^\s*#(?!\s*#)', text)
        )
        print(f"LINE: '{text}' -> H1={is_h1}")
        if is_h1:
            commit_buffer()
            current_title = (
                text.strip() if source == 'word'
                else re.sub(r'^\s*#\s*', '', text).strip()
            )
            print(f"NEW_TITLE: '{current_title}'")
        else:
            buffer.append(text)

    commit_buffer()
    print(f"FINAL: {len(items)} items created")
    
    for i, (order, title, content) in enumerate(items):
        print(f"Item {i}: order={order}, title='{title}', content='{content[:50]}...'")

if __name__ == "__main__":
    test_markdown_parsing()
