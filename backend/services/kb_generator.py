import re
import os
import json
import base64
import mimetypes
from datetime import datetime
from .pdf_generator import convert_markdown_to_html
from .export_branding import get_export_branding_settings, resolve_brand_asset_path


def _resolve_html_logo_src(raw_value):
    """Resolve an admin-provided logo setting to a usable HTML img src."""
    candidate = (raw_value or '').strip()
    if not candidate:
        return ''
    if candidate.startswith(('http://', 'https://', 'data:')):
        return candidate

    local_path = resolve_brand_asset_path(candidate)
    if not local_path or not os.path.exists(local_path):
        return ''

    with open(local_path, 'rb') as image_file:
        image_data = image_file.read()
    mime_type = mimetypes.guess_type(local_path)[0] or 'image/png'
    encoded = base64.b64encode(image_data).decode('ascii')
    return f'data:{mime_type};base64,{encoded}'

def generate_mobile_kb_html(publication, tree):
    """Generate mobile-first HTML for knowledge base using template"""
    branding = get_export_branding_settings()
    html_logo_src = _resolve_html_logo_src(branding.get('html_logo', ''))
    header_logo_html = (
        f'<img class="kb-brand-logo" src="{html_logo_src}" alt="{branding["brand_name"]} logo" />'
        if html_logo_src else ''
    )
    
    # Read the template file - get the absolute path to the root directory
    import os
    # Get the root directory (StructuredDocs)
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    template_path = os.path.join(root_dir, 'collection_mobile_kb.html')
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
    except FileNotFoundError:
        # Fallback to old inline generation if template not found
        return generate_mobile_kb_html_inline(publication, tree)
    
    # Build navigation HTML for the sidebar
    def build_nav_html(nodes, level=0, parent_path=""):
        import json
        import html as html_module
        html_content = ""
        for node in nodes:
            node_path = f"{parent_path}.{node['id']}" if parent_path else str(node['id'])
            
            # Show all levels with proper indentation
            indent = "    " * level
            # Use different icons for topics with and without children
            if node.get('children') and len(node.get('children', [])) > 0:
                icon = "📂"  # Folder icon for topics with subtopics
            else:
                icon = "📝"  # Document icon for individual topics
                
            if node.get('children') and len(node.get('children', [])) > 0:
                # Has children - clicking shows content and expands subtopics
                html_content += f'{indent}            <button class="nav-link nav-expandable" onclick="expandTopic(\'{node["id"]}\', this)">{icon} {node["title"]}<span class="nav-expand-icon">▶</span></button>\n'
                # Add hidden subtopics container
                html_content += f'{indent}            <div class="nav-subtopics" id="subtopics-{node["id"]}" style="display: none;">\n'
                # Recursively add children with indentation
                html_content += build_nav_html(node.get('children', []), level + 1, node["id"])
                html_content += f'{indent}            </div>\n'
            else:
                # No children - direct link to content
                html_content += f'{indent}            <button class="nav-link" onclick="showSection(\'section-{node["id"]}\')">{icon} {node["title"]}</button>\n'
            
        return html_content
    
    # Build the complete Topics nav section
    def build_topics_section(nodes):
        nav_html = build_nav_html(nodes)
        return f'''        <div class="nav-section">
            <div class="nav-section-title">📚 Topics</div>
            <button class="nav-link" onclick="showSection('welcome')">🏠 Home</button>
{nav_html}        </div>'''
    
    # Build content sections HTML
    def build_content_html(nodes, parent=None):
        html = ""
        for idx, node in enumerate(nodes):
            # Clean and process content
            content = node.get('content', '')
            if content:
                # Convert markdown content to HTML using proper function
                content = convert_markdown_to_html(content)
            else:
                content = '<p>No content available.</p>'

            has_children = bool(node.get('children'))
            in_this_section_html = ''
            related_content_html = ''

            # If this topic has children, add "In this section..." navigation
            if has_children:
                in_this_section = '<div class="in-this-section">\n<h2>In this section</h2>\n<ul class="section-links">\n'
                for child in node['children']:
                    in_this_section += f'<li><a href="#" onclick="showSection(\'section-{child["id"]}\'); return false;" class="section-link">📝 {child["title"]}</a></li>\n'
                in_this_section += '</ul>\n</div>\n'
                # Add the section navigation after the main content
                if content == '<p>No content available.</p>':
                    # If no content, replace with section overview
                    content = f'<p>This section contains multiple topics. Use the links below to navigate to specific content.</p>\n{in_this_section}'
                else:
                    # If there is content, append the section navigation
                    content += f'\n{in_this_section}'
                in_this_section_html = in_this_section
            else:
                # No children: add Related content section if there are siblings or children
                # Siblings: other topics at the same level (from parent)
                siblings = []
                if parent and parent.get('children'):
                    siblings = [sib for sib in parent['children'] if sib['id'] != node['id']]
                # Children: always empty here (no children)
                # But for completeness, if node.get('children'), add them
                related_links = []
                # Add siblings
                for sib in siblings:
                    related_links.append(f'<li><a href="#" onclick="showSection(\'section-{sib["id"]}\'); return false;" class="section-link">📝 {sib["title"]}</a></li>')
                    # Also add their children (lower level)
                    if sib.get('children'):
                        for child in sib['children']:
                            related_links.append(f'<li class="sub-related"><a href="#" onclick="showSection(\'section-{child["id"]}\'); return false;" class="section-link">📝 {child["title"]}</a></li>')
                # Add own children (should be none, but for completeness)
                if node.get('children'):
                    for child in node['children']:
                        related_links.append(f'<li class="sub-related"><a href="#" onclick="showSection(\'section-{child["id"]}\'); return false;" class="section-link">📝 {child["title"]}</a></li>')
                if related_links:
                    related_content_html = '<div class="related-content">\n<h2>Related content</h2>\n<ul class="section-links">\n' + '\n'.join(related_links) + '\n</ul>\n</div>\n'
                    content += f'\n{related_content_html}'

            html += f'''
        <div id="section-{node["id"]}" class="content-section">
            <h1>{node["title"]}</h1>
            {content}
        </div>
'''
            if node.get('children'):
                html += build_content_html(node['children'], parent=node)
        return html
    
    # Generate navigation and content
    topics_section_html = build_topics_section(tree)
    content_html = build_content_html(tree)
    
    # Replace placeholders in template
    # Replace the entire Topics nav section
    topics_section_pattern = r'        <div class="nav-section">\s*<div class="nav-section-title">📚 Topics</div>\s*<button class="nav-link" onclick="showSection\(\'welcome\'\)">🏠 Home</button>\s*<!-- Dynamic content will be inserted here -->\s*</div>'
    result = re.sub(topics_section_pattern, topics_section_html, template_content, flags=re.MULTILINE | re.DOTALL)
    
    result = result.replace('<!-- Dynamic content sections will be inserted here -->', content_html)
    result = result.replace('{{ date }}', datetime.now().strftime('%B %d, %Y'))
    result = result.replace('{{ publication_title }}', publication.title)
    result = result.replace('{{ brand_name }}', branding['brand_name'])
    result = result.replace('{{ html_primary_color }}', branding['html_primary_color'])
    result = result.replace('{{ html_accent_color }}', branding['html_accent_color'])
    result = result.replace('{{ header_logo_html }}', header_logo_html)
    
    # Add tree data for breadcrumb navigation
    import json
    import base64
    tree_json = json.dumps(tree)
    tree_base64 = base64.b64encode(tree_json.encode('utf-8')).decode('utf-8')
    result = result.replace('{{ tree_data }}', tree_base64)
    
    return result


def generate_mobile_kb_html_inline(publication, tree):
    """Generate mobile-first HTML for knowledge base"""
    branding = get_export_branding_settings()
    html_logo_src = _resolve_html_logo_src(branding.get('html_logo', ''))
    header_logo_html = (
        f'<img class="kb-brand-logo" src="{html_logo_src}" alt="{branding["brand_name"]} logo" />'
        if html_logo_src else ''
    )
    branding_css = f"""
    <style>
        :root {{
            --sd-primary: {branding['html_primary_color']};
            --sd-accent: {branding['html_accent_color']};
        }}
        .kb-brand-logo {{
            height: 36px;
            max-width: 120px;
            object-fit: contain;
            border-radius: 4px;
            background: rgba(255, 255, 255, 0.16);
            padding: 2px 6px;
        }}
        .kb-header {{ background: var(--sd-primary) !important; }}
        .nav-link {{ color: var(--sd-primary) !important; }}
        .nav-link.sub-item {{ border-left-color: var(--sd-primary) !important; }}
        .content-section h1 {{ border-bottom-color: var(--sd-primary) !important; }}
        .content-section h2 {{ color: var(--sd-primary) !important; }}
        .content-section h1,
        .content-section h3,
        .content-section h4,
        .content-section h5,
        .content-section h6 {{ color: var(--sd-accent) !important; }}
    </style>
    """
    
    # Mobile-first CSS template
    mobile_css = """
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f8f9fa;
            padding: 0;
            margin: 0;
        }
        
        .kb-container {
            max-width: 100%;
            margin: 0 auto;
            background: white;
            min-height: 100vh;
        }
        
        .kb-header {
            background: #005a9c;
            color: white;
            padding: 0.75rem 1rem 1rem;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 300;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }
        .kb-header-logo-row {
            width: 100%;
            display: flex;
            justify-content: flex-start;
            align-items: center;
            padding: 0 0 0.25rem;
        }
        .kb-header-inner {
            width: 100%;
            max-width: 900px;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin: 0 auto;
        }
        img,
        svg,
        picture,
        video,
        canvas {
            max-width: 100%;
            height: auto;
            display: block;
        }
        .hamburger-btn {
            flex-shrink: 0;
            width: 40px;
            height: 40px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 6px;
            border: 1px solid rgba(255,255,255,0.25);
            background: rgba(255,255,255,0.1);
            color: #fff;
            font-size: 1.25rem;
            cursor: pointer;
        }
        .hamburger-btn:focus { outline: 2px solid #fff; outline-offset: 2px; }

        .search-btn {
            flex-shrink: 0;
            width: 40px;
            height: 40px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 6px;
            border: 1px solid rgba(255,255,255,0.25);
            background: rgba(255,255,255,0.1);
            color: #fff;
            font-size: 1.1rem;
            cursor: pointer;
        }
        .search-btn:focus { outline: 2px solid #fff; outline-offset: 2px; }

        /* Search overlay */
        .search-overlay {
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.88);
            z-index: 600;
            display: none;
            flex-direction: column;
            align-items: center;
            padding: 1rem;
            overflow-y: auto;
        }
        .search-overlay.active { display: flex; }
        .search-box {
            width: 100%;
            max-width: 620px;
            margin-top: 3.5rem;
        }
        .search-input-row {
            display: flex;
            gap: 0.5rem;
        }
        .search-input {
            flex: 1;
            padding: 0.75rem 1rem;
            font-size: 1rem;
            border: none;
            border-radius: 6px;
            outline: none;
        }
        .search-close-btn {
            padding: 0.75rem 1rem;
            background: rgba(255,255,255,0.15);
            border: 1px solid rgba(255,255,255,0.35);
            color: #fff;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.95rem;
            white-space: nowrap;
        }
        .search-close-btn:hover { background: rgba(255,255,255,0.25); }
        .search-hint {
            color: rgba(255,255,255,0.5);
            font-size: 0.78rem;
            margin-top: 0.4rem;
            padding-left: 0.25rem;
        }
        .search-results {
            width: 100%;
            max-width: 620px;
            margin-top: 1rem;
        }
        .search-result-item {
            background: #fff;
            border-radius: 6px;
            padding: 0.75rem 1rem;
            margin-bottom: 0.5rem;
            cursor: pointer;
            transition: background 0.15s;
        }
        .search-result-item:hover { background: #eef3ff; }
        .search-result-title {
            font-weight: 600;
            color: #005a9c;
            margin-bottom: 0.25rem;
            font-size: 0.95rem;
        }
        .search-result-snippet {
            font-size: 0.85rem;
            color: #444;
            line-height: 1.45;
        }
        .search-result-snippet mark {
            background: #fff3cd;
            padding: 0 2px;
            border-radius: 2px;
            font-style: normal;
        }
        .search-no-results {
            color: rgba(255,255,255,0.75);
            text-align: center;
            padding: 2rem;
            font-size: 0.95rem;
        }
        .search-result-count {
            color: rgba(255,255,255,0.6);
            font-size: 0.8rem;
            margin-bottom: 0.5rem;
            padding-left: 0.25rem;
        }
        
        .kb-title {
            font-size: 1.25rem;
            font-weight: 600;
            margin: 0;
        }
        
        .kb-subtitle {
            font-size: 0.875rem;
            opacity: 0.9;
            margin-top: 0.25rem;
        }

        .kb-title-group {
            flex: 1;
            text-align: center;
            min-width: 0;
            overflow: hidden;
        }
        
        /* Drawer navigation (initially collapsed) */
        .navigation.nav-drawer {
            position: fixed;
            top: 60px; /* approximate header height */
            left: 0;
            bottom: 0;
            width: 260px; /* Reduced from 280px */
            background: #e9ecef;
            border-right: 1px solid #dee2e6;
            padding: 0.75rem; /* Reduced from 1rem */
            box-shadow: 2px 0 8px rgba(0,0,0,0.08);
            transform: translateX(-100%);
            transition: transform 220ms cubic-bezier(0.2, 0.8, 0.2, 1);
            z-index: 250;
            overflow-y: auto;
            -webkit-overflow-scrolling: touch;
        }
        body.nav-open .navigation.nav-drawer { transform: translateX(0); }
        .drawer-backdrop {
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.35);
            z-index: 200;
            display: none;
        }
        body.nav-open .drawer-backdrop { display: block; }
        body.nav-open { overflow: hidden; }
        
        .nav-section {
            margin-bottom: 0.75rem; /* Reduced from 1rem */
        }
        
        .nav-section:last-child {
            margin-bottom: 0;
        }
        
        .nav-title {
            font-weight: 600;
            color: #495057;
            margin-bottom: 0.375rem; /* Reduced from 0.5rem */
            font-size: 0.85rem; /* Reduced from 0.9rem */
            text-transform: uppercase;
            letter-spacing: 0.3px; /* Reduced from 0.5px */
        }
        
        .nav-link {
            display: block;
            padding: 0.5rem 0.625rem; /* Reduced from 0.75rem */
            color: #005a9c;
            text-decoration: none;
            background: white;
            border-radius: 4px; /* Reduced from 6px */
            margin-bottom: 0.375rem; /* Reduced from 0.5rem */
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            transition: all 0.2s ease;
            font-size: 0.9rem; /* Added for better mobile readability */
            line-height: 1.3; /* Tighter line height */
        }
        
        .nav-link:hover {
            background: #f8f9fa;
            transform: translateY(-1px);
            box-shadow: 0 2px 6px rgba(0,0,0,0.15);
        }
        
        .nav-link:active {
            transform: translateY(0);
        }
        
        .nav-link.sub-item {
            margin-left: 0.75rem; /* Reduced from 1rem */
            background: #f8f9fa;
            border-left: 2px solid #005a9c; /* Reduced from 3px */
            padding: 0.4rem 0.5rem; /* Smaller padding for sub-items */
            font-size: 0.85rem; /* Smaller font for sub-items */
        }
        
        .nav-parent {
            position: relative;
            }
            .nav-parent > .nav-link {
                padding-right: 2rem; /* Add space for arrow toggle to prevent overlap */
        }
        
        .nav-parent-toggle {
            position: absolute;
            right: 0.375rem; /* Reduced from 0.5rem */
            top: 50%;
            transform: translateY(-50%);
            background: none;
            border: none;
            cursor: pointer;
            font-size: 0.75rem; /* Reduced from 0.8rem */
            color: #6c757d;
            width: 18px; /* Reduced from 20px */
            height: 18px; /* Reduced from 20px */
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.2s ease;
        }
        
        .nav-parent-toggle.expanded {
            transform: translateY(-50%) rotate(90deg);
        }
        
        .nav-children {
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease;
            margin-bottom: 0.25rem; /* Reduce gap below collapsed subtopics */
        }
        
        .nav-children.expanded {
                        max-height: 1200px; /* Increase to prevent cutoff for longer lists */
                        margin-bottom: 0.5rem; /* Moderate gap below expanded subtopics */
        }
        
        .content-section {
            display: none;
            padding: 1.5rem;
            animation: fadeIn 0.3s ease-in;
        }
        
        .content-section.active {
            display: block;
        }
        
        .content-section h1,
        .content-section h2,
        .content-section h3,
        .content-section h4,
        .content-section h5,
        .content-section h6 {
            color: #112E51;
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
            line-height: 1.3;
        }
        
        .content-section h1 {
            font-size: 1.5rem;
            border-bottom: 2px solid #005a9c;
            padding-bottom: 0.5rem;
            margin-top: 0;
        }
        
        .content-section h2 {
            font-size: 1.25rem;
            color: #005a9c;
        }
        
        .content-section h3 {
            font-size: 1.1rem;
        }
        
        .content-section p {
            margin-bottom: 1rem;
            line-height: 1.7;
        }
        
        .content-section ul,
        .content-section ol {
            margin-bottom: 1rem;
            padding-left: 1.5rem;
        }
        
        .content-section li {
            margin-bottom: 0.5rem;
        }
        
        .content-section code {
            background: #f8f9fa;
            padding: 0.25rem 0.5rem;
            border-radius: 3px;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 0.875rem;
        }
        
        .content-section pre {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 6px;
            overflow-x: auto;
            margin-bottom: 1rem;
            border: 1px solid #e9ecef;
        }
        
        .content-section pre code {
            background: none;
            padding: 0;
        }
        
        .content-section blockquote {
            border-left: 4px solid #005a9c;
            padding-left: 1rem;
            margin: 1rem 0;
            font-style: italic;
            color: #6c757d;
        }
        
        .content-section table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 1rem;
            font-size: 0.9rem;
        }
        
        .content-section th,
        .content-section td {
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }
        
        .content-section th {
            background: #f8f9fa;
            font-weight: 600;
            color: #495057;
        }
        
        .back-to-nav {
            background: #6c757d;
            color: white;
            border: none;
            padding: 0.75rem 1rem;
            border-radius: 6px;
            margin-bottom: 1rem;
            cursor: pointer;
            font-size: 0.9rem;
            transition: background 0.2s ease;
        }
        
        .back-to-nav:hover {
            background: #5a6268;
        }
        
        .footer {
            background: #f8f9fa;
            padding: 1rem;
            text-align: center;
            color: #6c757d;
            font-size: 0.8rem;
            border-top: 1px solid #e9ecef;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Tablet optimizations */
        @media (min-width: 768px) {
            .kb-container {
                max-width: 800px;
            }
            
            .kb-title {
                font-size: 1.5rem;
            }
            
            .content-section {
                padding: 2rem;
            }
            
            .navigation {
                padding: 1.5rem;
            }
        }
        
        /* Desktop optimizations (still mobile-first) */
        @media (min-width: 1024px) {
            .kb-container {
                max-width: 900px;
            }
            
            .content-section h1 {
                font-size: 1.75rem;
            }
        }
        
        /* iOS Safari specific fixes */
        @supports (-webkit-touch-callout: none) {
            .kb-header {
                -webkit-backdrop-filter: blur(20px);
                backdrop-filter: blur(20px);
            }
        }
        
        /* Mobile-specific optimizations for smaller screens */
        @media (max-width: 480px) {
            .navigation.nav-drawer {
                width: 240px; /* Even smaller on very small screens */
                padding: 0.5rem; /* Further reduced padding */
            }
            
            .nav-link {
                padding: 0.4rem 0.5rem; /* More compact on small screens */
                font-size: 0.85rem;
                margin-bottom: 0.25rem; /* Tighter spacing */
            }
            
            .nav-link.sub-item {
                margin-left: 0.5rem; /* Less indentation on small screens */
                padding: 0.3rem 0.4rem;
                font-size: 0.8rem;
            }
            
            .nav-title {
                font-size: 0.8rem;
                margin-bottom: 0.25rem;
            }
            
            .nav-section {
                margin-bottom: 0.5rem;
            }
        }

        /* High contrast mode support */
        @media (prefers-contrast: high) {
            .nav-link {
                border: 1px solid #000;
            }
            
            .kb-header {
                border-bottom: 2px solid #000;
            }
        }
        
        /* Dark mode support */
        @media (prefers-color-scheme: dark) {
            body {
                background: #1a1a1a;
                color: #e0e0e0;
            }
            
            .kb-container {
                background: #2d2d2d;
            }
            
            .navigation.nav-drawer {
                background: #3a3a3a;
                border-right-color: #555;
            }
            
            .nav-link {
                background: #4a4a4a;
                color: #87ceeb;
            }
            
            .nav-link:hover {
                background: #5a5a5a;
            }
            
            .content-section h1,
            .content-section h2,
            .content-section h3,
            .content-section h4,
            .content-section h5,
            .content-section h6 {
                color: #f0f0f0;
            }
            
            .content-section h2 {
                color: #87ceeb;
            }
            
            .content-section code,
            .content-section pre {
                background: #3a3a3a;
                color: #e0e0e0;
            }
            
            .footer {
                background: #3a3a3a;
                color: #b0b0b0;
            }
        }
    </style>
    """
    
    # JavaScript for navigation
    first_section = f"section-{tree[0]['id']}" if tree else ''
    # Use a plain string (not an f-string) to avoid Python interpreting JS braces
    mobile_js = """
    <script>
        function showSection(sectionId) {
            // Hide all sections
            const sections = document.querySelectorAll('.content-section');
            sections.forEach(section => {
                section.classList.remove('active');
            });
            
            // Close drawer and show selected section
            closeNav();
            const targetSection = document.getElementById(sectionId);
            if (targetSection) {
                targetSection.classList.add('active');
                window.scrollTo(0, 0);
            }
        }
        
        function toggleParent(parentId) {
            const children = document.querySelector(`[data-parent="${parentId}"]`);
            const toggle = document.querySelector(`[data-toggle="${parentId}"]`);
            
            if (children && toggle) {
                const isExpanded = children.classList.contains('expanded');
                if (isExpanded) {
                    children.classList.remove('expanded');
                    toggle.classList.remove('expanded');
                    toggle.textContent = '▶';
                } else {
                    children.classList.add('expanded');
                    toggle.classList.add('expanded');
                    toggle.textContent = '▼';
                }
            }
        }
        
        function openNav() { document.body.classList.add('nav-open'); updateHamburger(true); }
        function closeNav() { document.body.classList.remove('nav-open'); updateHamburger(false); }
        function toggleNav() { if (document.body.classList.contains('nav-open')) closeNav(); else openNav(); }
        function updateHamburger(open) {
            const btn = document.getElementById('hamburger-btn');
            if (btn) { btn.setAttribute('aria-expanded', open ? 'true' : 'false'); btn.textContent = open ? '✕' : '☰'; }
        }

        // ── Search ────────────────────────────────────────────────────────────
        let _searchIndex = null;

        function _buildIndex() {
            _searchIndex = [];
            document.querySelectorAll('.content-section').forEach(sec => {
                const h = sec.querySelector('h1,h2,h3');
                const title = h ? h.textContent.trim() : sec.id;
                // innerText gives plain text respecting visibility; fall back to textContent
                const raw = (sec.innerText || sec.textContent || '').trim();
                _searchIndex.push({ id: sec.id, title, text: raw });
            });
        }

        function _escapeRe(s) { return s.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&'); }

        function _highlight(text, query) {
            if (!query) return text;
            return text.replace(new RegExp('(' + _escapeRe(query) + ')', 'gi'), '<mark>$1</mark>');
        }

        function _snippet(text, query, maxLen) {
            maxLen = maxLen || 160;
            const lo = text.toLowerCase(), lq = query.toLowerCase();
            const idx = lo.indexOf(lq);
            if (idx === -1) return text.slice(0, maxLen) + (text.length > maxLen ? '\\u2026' : '');
            const s = Math.max(0, idx - 70), e = Math.min(text.length, idx + query.length + 90);
            return (s > 0 ? '\\u2026' : '') + text.slice(s, e) + (e < text.length ? '\\u2026' : '');
        }

        function performSearch(query) {
            const countEl   = document.getElementById('search-result-count');
            const resultsEl = document.getElementById('search-results');
            resultsEl.innerHTML = '';
            countEl.textContent = '';
            if (!query || query.length < 2) return;
            if (!_searchIndex) _buildIndex();

            const lq = query.toLowerCase();
            const hits = _searchIndex.filter(item =>
                item.title.toLowerCase().includes(lq) || item.text.toLowerCase().includes(lq)
            );
            // Title matches first
            hits.sort((a, b) => {
                const at = a.title.toLowerCase().includes(lq);
                const bt = b.title.toLowerCase().includes(lq);
                return (bt ? 1 : 0) - (at ? 1 : 0);
            });

            if (hits.length === 0) {
                resultsEl.innerHTML = '<div class="search-no-results">No results found for \\u201c' + query + '\\u201d</div>';
                return;
            }
            countEl.textContent = hits.length + (hits.length === 1 ? ' result' : ' results');
            hits.slice(0, 15).forEach(item => {
                const snippet  = _snippet(item.text, query);
                const div = document.createElement('div');
                div.className = 'search-result-item';
                div.innerHTML =
                    '<div class="search-result-title">' + _highlight(item.title, query) + '</div>' +
                    '<div class="search-result-snippet">' + _highlight(snippet, query) + '</div>';
                div.addEventListener('click', function() { closeSearch(); showSection(item.id); });
                resultsEl.appendChild(div);
            });
        }

        function openSearch() {
            closeNav();
            document.getElementById('search-overlay').classList.add('active');
            document.body.style.overflow = 'hidden';
            setTimeout(function() { document.getElementById('search-input').focus(); }, 50);
        }
        function closeSearch() {
            document.getElementById('search-overlay').classList.remove('active');
            document.getElementById('search-input').value = '';
            document.getElementById('search-results').innerHTML = '';
            document.getElementById('search-result-count').textContent = '';
            document.body.style.overflow = '';
        }
        // ── End Search ────────────────────────────────────────────────────────

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            // Default: show first section if available, keep drawer closed
            const FIRST_SECTION = '{FIRST_SECTION}';
            if (FIRST_SECTION) { showSection(FIRST_SECTION); }
            closeNav();
            const hb = document.getElementById('hamburger-btn');
            if (hb) hb.addEventListener('click', toggleNav);
            const bd = document.getElementById('drawer-backdrop');
            if (bd) bd.addEventListener('click', closeNav);
            const sb = document.getElementById('search-btn');
            if (sb) sb.addEventListener('click', openSearch);
            const sc = document.getElementById('search-close-btn');
            if (sc) sc.addEventListener('click', closeSearch);
            const si = document.getElementById('search-input');
            if (si) {
                si.addEventListener('input', function() { performSearch(this.value.trim()); });
                // Allow Enter to navigate to first result
                si.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter') {
                        const first = document.querySelector('.search-result-item');
                        if (first) first.click();
                    }
                });
            }
            document.addEventListener('keydown', function(e) {
                const overlay = document.getElementById('search-overlay');
                if (e.key === 'Escape') { closeNav(); closeSearch(); }
                // '/' opens search when not already typing in an input
                if (e.key === '/' && document.activeElement.tagName !== 'INPUT' &&
                        document.activeElement.tagName !== 'TEXTAREA') {
                    if (!overlay.classList.contains('active')) { e.preventDefault(); openSearch(); }
                }
            });
            // Pre-build search index after page settles
            setTimeout(_buildIndex, 200);
        });
    </script>
    """
    
    mobile_js = mobile_js.replace('{FIRST_SECTION}', first_section)
    
    # Build navigation HTML
    def build_nav_html(nodes, level=0):
        html = ""
        for node in nodes:
            if node["children"] and level == 0:  # Parent topic with children
                html += f'''
                <div class="nav-parent">
                    <a href="#" class="nav-link" onclick="showSection('section-{node["id"]}')">{node["title"]}</a>
                    <button class="nav-parent-toggle" data-toggle="{node["id"]}" onclick="toggleParent('{node["id"]}')" title="Toggle subtopics">▶</button>
                </div>
                <div class="nav-children" data-parent="{node["id"]}">
                    {build_nav_html(node["children"], level + 1)}
                </div>
                '''
            else:  # Regular topic or child topic
                css_class = "nav-link sub-item" if level > 0 else "nav-link"
                html += f'<a href="#" class="{css_class}" onclick="showSection(\'section-{node["id"]}\')">{node["title"]}</a>\n'
                if node["children"]:
                    html += build_nav_html(node["children"], level + 1)
        return html
    
    # Build content HTML
    def build_content_html(nodes):
        html = ""
        for node in nodes:
            # Convert markdown content to HTML (basic conversion)
            content_html = convert_markdown_to_html(node["content"])
            html += f'''
            <div id="section-{node["id"]}" class="content-section">
                <h1>{node["title"]}</h1>
                {content_html}
            </div>
            '''
            if node["children"]:
                html += build_content_html(node["children"])
        return html
    
    # Generate the complete HTML
    nav_html = build_nav_html(tree)
    content_html = build_content_html(tree)
    
    current_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    
    html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="apple-mobile-web-app-title" content="{publication.title}">
    <title>{publication.title} - Mobile Knowledge Base</title>
    {mobile_css}
    {branding_css}
</head>
<body>
    <div class="kb-container">
        <header class="kb-header">
            <div class="kb-header-logo-row">
                {header_logo_html}
            </div>
            <div class="kb-header-inner">
                <button id="hamburger-btn" class="hamburger-btn" aria-label="Toggle menu" aria-expanded="false">☰</button>
                <div class="kb-title-group">
                    <h1 class="kb-title">{publication.title}</h1>
                    <p class="kb-subtitle">Mobile Knowledge Base</p>
                </div>
                <button id="search-btn" class="search-btn" aria-label="Search">🔍</button>
            </div>
        </header>
        
        <div class="drawer-backdrop" id="drawer-backdrop" hidden></div>

        <!-- Search overlay -->
        <div id="search-overlay" class="search-overlay" role="dialog" aria-label="Search">
            <div class="search-box">
                <div class="search-input-row">
                    <input id="search-input" class="search-input" type="search"
                           placeholder="Search topics and content…" autocomplete="off" spellcheck="false">
                    <button id="search-close-btn" class="search-close-btn">✕ Close</button>
                </div>
                <div class="search-hint">Press <kbd style="color:#fff;border:1px solid rgba(255,255,255,0.4);padding:0 4px;border-radius:3px;font-size:0.75rem">/</kbd> to search · <kbd style="color:#fff;border:1px solid rgba(255,255,255,0.4);padding:0 4px;border-radius:3px;font-size:0.75rem">Esc</kbd> to close</div>
            </div>
            <div id="search-result-count" class="search-result-count"></div>
            <div id="search-results" class="search-results"></div>
        </div>
        <nav class="navigation nav-drawer" id="kb-nav" role="navigation" aria-label="Topics menu">
            <div class="nav-section">
                <div class="nav-title">Topics</div>
                {nav_html}
            </div>
        </nav>
        
        {content_html}
        
        <footer class="footer">
            Generated on {current_time}<br>
            {branding['brand_name']} - Optimized for mobile devices
        </footer>
    </div>
    
    {mobile_js}
</body>
</html>'''
    
    return html_template

