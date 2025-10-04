#!/usr/bin/env python3
"""
Fix markdown formatting issues in documentation files.
This script addresses the 34 markdown linting issues reported in VS Code.
"""

import os
import re

def fix_markdown_formatting(filepath):
    """Fix common markdown formatting issues"""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Fix 1: Add blank lines around headings (MD022)
    # This regex finds headings and ensures they have blank lines before and after
    content = re.sub(r'([^\n])\n(#{1,6}\s+)', r'\1\n\n\2', content)
    content = re.sub(r'(#{1,6}\s+[^\n]+)\n([^\n#])', r'\1\n\n\2', content)
    
    # Fix 2: Add blank lines around lists (MD032)
    # Find list items and ensure blank lines around them
    content = re.sub(r'([^\n])\n([•\-\*]\s+)', r'\1\n\n\2', content)
    content = re.sub(r'([^\n])\n(\d+\.\s+)', r'\1\n\n\2', content)
    content = re.sub(r'([•\-\*]\s+[^\n]+)\n([^•\-\*\d\n][^\n]*)', r'\1\n\n\2', content)
    content = re.sub(r'(\d+\.\s+[^\n]+)\n([^•\-\*\d\n][^\n]*)', r'\1\n\n\2', content)
    
    # Fix 3: Add blank lines around fenced code blocks (MD031)
    content = re.sub(r'([^\n])\n(```)', r'\1\n\n\2', content)
    content = re.sub(r'(```[^\n]*)\n([^`\n])', r'\1\n\n\2', content)
    
    # Fix 4: Remove trailing spaces (MD009) 
    content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)
    
    # Fix 5: Ensure single trailing newline (MD047)
    content = content.rstrip() + '\n'
    
    # Fix 6: Remove excessive blank lines (clean up our additions)
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    """Fix markdown formatting in all documentation files"""
    
    print("🔧 Fixing Markdown Formatting Issues")
    print("=" * 40)
    
    # Find all markdown files
    markdown_files = []
    for root, dirs, files in os.walk('/workspaces/StructuredDocs'):
        # Skip node_modules, .git, and other unnecessary directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv']]
        
        for file in files:
            if file.endswith('.md'):
                markdown_files.append(os.path.join(root, file))
    
    fixed_count = 0
    
    for filepath in markdown_files:
        try:
            if fix_markdown_formatting(filepath):
                print(f"✅ Fixed: {os.path.basename(filepath)}")
                fixed_count += 1
            else:
                print(f"⚪ OK: {os.path.basename(filepath)}")
        except Exception as e:
            print(f"❌ Error fixing {filepath}: {e}")
    
    print(f"\n📊 Summary: Fixed {fixed_count} out of {len(markdown_files)} markdown files")
    
    if fixed_count > 0:
        print("\n🎉 Markdown formatting issues should now be resolved!")
        print("   The 34 problems in VS Code Problems tab should be reduced significantly.")
    else:
        print("\n✅ No markdown formatting issues found.")

if __name__ == "__main__":
    main()