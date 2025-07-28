    # Build navigation HTML for the sidebar
    def build_nav_html(nodes, level=0, parent_path=""):
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
                html_content += f'{indent}            <button class="nav-link nav-expandable" onclick="expandTopic(\'{node["id"]}\', this)">{icon} {node["title"]}</button>\n'
                # Add hidden subtopics container
                html_content += f'{indent}            <div class="nav-subtopics" id="subtopics-{node["id"]}" style="display: none;">\n'
                # Recursively add children with indentation
                html_content += build_nav_html(node.get('children', []), level + 1, node["id"])
                html_content += f'{indent}            </div>\n'
            else:
                # No children - direct link to content
                html_content += f'{indent}            <button class="nav-link" onclick="showSection(\'section-{node["id"]}\')">{icon} {node["title"]}</button>\n'
            
        return html_content
