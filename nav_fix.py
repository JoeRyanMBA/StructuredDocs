import re

# Read the current file
with open(r'c:\Dev\StructuredDocs\backend\routes\publications.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Define the new build_nav_html function
new_function = '''    def build_nav_html(nodes, level=0, parent_path=""):
        import json
        import html as html_module
        html_content = ""
        for node in nodes:
            node_path = f"{parent_path}.{node['id']}" if parent_path else str(node['id'])
            
            # Show all levels with proper indentation
            indent = "    " * level
            icon = "📝"
            if node.get('children'):
                # Has children - clicking shows content and expands subtopics
                html_content += f'{indent}            <button class="nav-link nav-expandable" onclick="expandTopic(\\'{node["id"]}\\', this)">{icon} {node["title"]}</button>\\n'
                # Add hidden subtopics container
                html_content += f'{indent}            <div class="nav-subtopics" id="subtopics-{node["id"]}" style="display: none;">\\n'
                # Recursively add children with indentation
                html_content += build_nav_html(node.get('children', []), level + 1, node["id"])
                html_content += f'{indent}            </div>\\n'
            else:
                # No children - direct link to content
                html_content += f'{indent}            <button class="nav-link" onclick="showSection(\\'section-{node["id"]}\')">{icon} {node["title"]}</button>\\n'
            
        return html_content'''

# Find and replace the old function
pattern = r'def build_nav_html\(nodes, level=0, parent_path=""\):.*?return html_content'
new_content = re.sub(pattern, new_function.strip(), content, flags=re.DOTALL)

# Write back the modified content
with open(r'c:\Dev\StructuredDocs\backend\routes\publications.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Fixed navigation function - removed level restriction")
