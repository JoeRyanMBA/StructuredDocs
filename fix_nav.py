#!/usr/bin/env python3

# Read the publications.py file
with open('backend/routes/publications.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the build_nav_html function
start_marker = "    # Build navigation HTML for the sidebar"
end_marker = "        return html"

start_idx = content.find(start_marker)
if start_idx == -1:
    print("Could not find start marker")
    exit(1)

# Find the end of the function (the return statement)
temp_start = start_idx
end_idx = content.find(end_marker, temp_start)
if end_idx == -1:
    print("Could not find end marker")
    exit(1)

# Include the return statement
end_idx = content.find('\n', end_idx) + 1

# New function content
new_function = """    # Build navigation HTML for the sidebar - show all topics
    def build_nav_html(nodes, level=0):
        html = ""
        for node in nodes:
            # Show all topics with appropriate icons
            icon = "📄" if level == 0 else "📝"
            html += f'            <button class="nav-link" onclick="showSection(\\'section-{node["id"]}\\'))">{icon} {node["title"]}</button>\\n'
            
            # Recursively add children to show all topics
            if node.get('children'):
                html += build_nav_html(node['children'], level + 1)
            
        return html
"""

# Replace the function
new_content = content[:start_idx] + new_function + content[end_idx:]

# Write back to file
with open('backend/routes/publications.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Fixed navigation function - now shows all topics")
