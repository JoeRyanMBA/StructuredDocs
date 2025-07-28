# Simple navigation replacement
def build_nav_html(nodes, level=0):
    html = ""
    for node in nodes:
        # Show all topics with appropriate icons
        icon = "📄" if level == 0 else "📝"
        html += f'            <button class="nav-link" onclick="showSection(\'section-{node["id"]}\')">{icon} {node["title"]}</button>\n'
        
        # Recursively add children to show all topics
        if node.get('children'):
            html += build_nav_html(node['children'], level + 1)
        
    return html
