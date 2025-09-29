#!/usr/bin/env python3
"""
Debug script to test the Word import promotion and topic creation logic.
This simulates what happens during Word document import.
"""

import re

def detect_heading_level_from_style(style_name: str):
    """Extract heading level (1-6) from a Word style name."""
    if not style_name:
        return None
    sn = style_name.lower()
    patterns = [
        r'(?:^|[\s,;:()\-])heading\s+level\s*(\d)\b',   # heading level 2
        r'(?:^|[\s,;:()\-])sc\s+heading\s*(\d)\b',      # sc heading 2
        r'(?:^|[\s,;:()\-])heading\s*(\d)\b',            # heading 2
    ]
    for pat in patterns:
        m = re.search(pat, sn)
        if m:
            try:
                lvl = int(m.group(1))
                if 1 <= lvl <= 6:
                    return lvl
            except ValueError:
                return None
    return None

def simulate_pandoc_conversion():
    """Simulate what pandoc might output for a Word document with headings"""
    # This simulates markdown output from pandoc for a document with:
    # - Heading 1: "Introduction" 
    # - Heading 2: "Overview"
    # - Heading 3: "Details"
    # - Some content under each
    
    mock_pandoc_output = """# Introduction

This is the introduction content.

## Overview

This section provides an overview of the topic.

### Details

Here are the detailed explanations.

More detailed content here."""
    
    return mock_pandoc_output

def simulate_docx_fallback():
    """Simulate what the python-docx fallback might produce"""
    # Simulate paragraphs with styles from a Word document
    mock_paragraphs = [
        ("# Introduction", "Heading 1"),
        ("This is the introduction content.", "Normal"),
        ("Overview", "Heading 2"), 
        ("This section provides an overview of the topic.", "Normal"),
        ("Details", "Heading 3"),
        ("Here are the detailed explanations.", "Normal"),
        ("More detailed content here.", "Normal")
    ]
    
    lines = []
    for text, style_name in mock_paragraphs:
        if not text.strip():
            continue
        
        level = detect_heading_level_from_style(style_name)
        if level == 1:
            lines.append(f"# {text}")
        elif level and level > 1:
            hashes = '#' * min(level, 6)
            lines.append(f"{hashes} {text}")
        else:
            lines.append(text)
    
    return '\n'.join(lines)

def test_promotion_logic(markdown_content, source_name):
    """Test the heading promotion logic"""
    print(f"\n🧪 Testing {source_name}")
    print("=" * 50)
    print("Input markdown:")
    print(markdown_content)
    print("\n" + "=" * 50)
    
    # Apply promotion logic (same as in the actual code)
    lines = []
    for line in markdown_content.splitlines():
        if line.strip().startswith('#'):
            hash_count = len(line) - len(line.lstrip('#'))
            if hash_count > 1:
                content = line.lstrip('#').strip()
                line = f"# {content}"
                print(f"PROMOTED: '{line.strip()}' (was H{hash_count})")
        lines.append(line)
    
    print(f"\nAfter promotion ({len(lines)} lines):")
    for i, line in enumerate(lines):
        print(f"{i:2d}: {repr(line)}")
    
    # Test topic creation logic (same as in actual code)
    paras = [('md', line) for line in lines]
    items, buffer, order, current_title = [], [], 0, None
    
    print(f"\n📊 Topic Creation Analysis:")
    print(f"Total paragraphs to process: {len(paras)}")
    
    def commit_buffer():
        nonlocal order, current_title, buffer
        if current_title:
            content = '\n'.join(buffer).strip()
            if content:
                items.append((order, current_title, content))
                print(f"✅ COMMITTED: order={order}, title='{current_title}', content_len={len(content)}")
                order += 1
            else:
                print(f"⚠️  SKIPPED EMPTY: title='{current_title}' (no substantive content)")
            buffer = []

    for style, text in paras:
        is_h1 = text.strip().startswith('#') and not text.strip().startswith('##')
        print(f"LINE: '{text}' -> H1={is_h1}")
        
        if is_h1:
            commit_buffer()
            current_title = text.strip().lstrip('#').strip()
            print(f"🎯 NEW_TITLE: '{current_title}'")
        else:
            buffer.append(text)

    commit_buffer()
    print(f"\n📚 FINAL RESULT: {len(items)} topics created")
    
    for i, (order, title, content) in enumerate(items, 1):
        print(f"  {i}. '{title}' ({len(content)} chars)")
        preview = content[:100] + "..." if len(content) > 100 else content
        print(f"     Preview: {repr(preview)}")
    
    return items

def main():
    print("🔍 DEBUG: Word Import Heading Promotion & Topic Creation")
    print("=" * 60)
    
    # Test 1: Pandoc path simulation
    pandoc_output = simulate_pandoc_conversion()
    pandoc_topics = test_promotion_logic(pandoc_output, "Pandoc Conversion Path")
    
    # Test 2: Python-docx fallback simulation  
    docx_output = simulate_docx_fallback()
    docx_topics = test_promotion_logic(docx_output, "Python-docx Fallback Path")
    
    print("\n" + "=" * 60)
    print("📋 SUMMARY")
    print("=" * 60)
    print(f"Pandoc path would create: {len(pandoc_topics)} topics")
    print(f"Python-docx path would create: {len(docx_topics)} topics")
    
    if len(pandoc_topics) == 0 and len(docx_topics) == 0:
        print("❌ PROBLEM: Neither path creates topics!")
        print("This suggests a bug in the topic creation logic.")
    elif len(pandoc_topics) != len(docx_topics):
        print("⚠️  WARNING: Different paths create different numbers of topics!")
        print("This suggests inconsistent behavior between conversion methods.")
    else:
        print("✅ Both paths create the same number of topics.")
    
    print("\n💡 If this is working correctly but your import isn't, the issue might be:")
    print("  1. The Word document doesn't have recognizable heading styles")
    print("  2. Pandoc conversion is failing and fallback isn't working") 
    print("  3. The document structure is different than expected")
    print("  4. There's an error in the conversion process not covered by this simulation")

if __name__ == "__main__":
    main()