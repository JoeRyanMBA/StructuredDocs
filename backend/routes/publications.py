from flask import Blueprint, Flask, request, jsonify, render_template_string, make_response
from ..models import db, Publication, PublicationNode, Topic
import re
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
import io


# Pass strict_slashes here so both /api/publications and /api/publications/ match
pubs_bp = Blueprint(
    'publications',
    __name__,
    url_prefix='/api/publications',
)

@pubs_bp.route('', methods=['GET'])
def list_pubs():
    all_pubs = Publication.query.order_by(Publication.created_at.desc()).all()
    
    # Group publications by title and return only the latest version of each
    latest_pubs = {}
    for pub in all_pubs:
        if pub.title not in latest_pubs:
            latest_pubs[pub.title] = pub
    
    # Convert to list and maintain newest-first order
    result = [pub.to_dict() for pub in latest_pubs.values()]
    # Sort by created_at descending to maintain newest first
    result.sort(key=lambda x: x['created_at'], reverse=True)
    
    return jsonify(result), 200

@pubs_bp.route('', methods=['POST'])
def create_publication():
    """Create a new publication"""
    data = request.get_json()
    
    pub = Publication(
        title=data.get('title', 'Untitled Publication'),
        description=data.get('description', '')
    )
    
    db.session.add(pub)
    db.session.commit()
    
    return jsonify(pub.to_dict()), 201

@pubs_bp.route('/<int:pub_id>', methods=['GET'])
def get_pub(pub_id):
    p = Publication.query.get_or_404(pub_id)
    def serialize(node):
        return {
            'id': node.id,
            'topic': node.topic.to_dict(),
            'position': node.position,
            'children': sorted([serialize(c) for c in node.children],
                               key=lambda x: x['position'])
        }
    top_nodes = [n for n in p.nodes if n.parent_id is None]
    tree = sorted([serialize(n) for n in top_nodes],
                  key=lambda x: x['position'])
    return jsonify({'id': p.id, 'title': p.title, 'description': p.description, 'tree': tree}), 200

@pubs_bp.route('/<int:pub_id>/nodes', methods=['POST'])
def save_nodes(pub_id):
    payload = request.get_json()  # expect {"tree": [...]}
    PublicationNode.query.filter_by(publication_id=pub_id).delete()

    def walk(nodes, parent_id=None):
        for idx, n in enumerate(nodes):
            node = PublicationNode(
                publication_id=pub_id,
                topic_id=n['topic_id'],
                parent_id=parent_id,
                position=idx
            )
            db.session.add(node)
            db.session.flush()  # assign node.id
            if n.get('children'):
                walk(n['children'], node.id)

    walk(payload['tree'])
    db.session.commit()
    return jsonify({'message': 'saved'}), 200

@pubs_bp.route('/<int:pub_id>/export/mobile-kb', methods=['GET'])
def export_mobile_knowledge_base(pub_id):
    """Export publication as mobile-first knowledge base HTML"""
    pub = Publication.query.get_or_404(pub_id)
    
    # Build the hierarchical structure
    def serialize_node(node):
        topic_data = node.topic.to_dict() if node.topic else {'title': 'Unknown', 'content': ''}
        return {
            'id': node.id,
            'topic_id': node.topic_id,
            'title': topic_data.get('title', 'Untitled'),
            'content': topic_data.get('content', ''),
            'position': node.position,
            'children': sorted([serialize_node(c) for c in node.children],
                             key=lambda x: x['position'])
        }
    
    top_nodes = [n for n in pub.nodes if n.parent_id is None]
    tree = sorted([serialize_node(n) for n in top_nodes],
                  key=lambda x: x['position'])
    
    # Generate mobile-optimized HTML
    html_content = generate_mobile_kb_html(pub, tree)
    
    response = make_response(html_content)
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename="{pub.title}_mobile_kb.html"'
    return response

def generate_mobile_kb_html(publication, tree):
    """Generate mobile-first HTML for knowledge base using template"""
    
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
    
    # Build the complete Topics nav section
    def build_topics_section(nodes):
        nav_html = build_nav_html(nodes)
        return f'''        <div class="nav-section">
            <div class="nav-section-title">📚 Topics</div>
            <button class="nav-link" onclick="showSection('welcome')">🏠 Home</button>
{nav_html}        </div>'''
    
    # Build content sections HTML
    def build_content_html(nodes):
        html = ""
        for node in nodes:
            # Clean and process content
            content = node.get('content', '')
            if content:
                # Convert markdown-style content to HTML if needed
                content = content.replace('\\n', '\n')
                # Simple markdown processing
                import re
                content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
                content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', content)
                content = re.sub(r'`(.*?)`', r'<code>\1</code>', content)
                # Convert line breaks to paragraphs
                paragraphs = content.split('\n\n')
                content = ''.join(f'<p>{p.strip()}</p>' for p in paragraphs if p.strip())
            else:
                content = '<p>No content available.</p>'
            
            html += f'''
        <div id="section-{node["id"]}" class="content-section">
            <h1>{node["title"]}</h1>
            {content}
        </div>
'''
            if node.get('children'):
                html += build_content_html(node['children'])
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
    
    # Add tree data for breadcrumb navigation
    import json
    import base64
    tree_json = json.dumps(tree)
    tree_base64 = base64.b64encode(tree_json.encode('utf-8')).decode('utf-8')
    result = result.replace('{{ tree_data }}', tree_base64)
    
    return result


def generate_mobile_kb_html_inline(publication, tree):
    """Generate mobile-first HTML for knowledge base"""
    
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
            padding: 1rem;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 100;
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
        
        .navigation {
            background: #e9ecef;
            border-bottom: 1px solid #dee2e6;
            padding: 1rem;
        }
        
        .nav-section {
            margin-bottom: 1rem;
        }
        
        .nav-section:last-child {
            margin-bottom: 0;
        }
        
        .nav-title {
            font-weight: 600;
            color: #495057;
            margin-bottom: 0.5rem;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .nav-link {
            display: block;
            padding: 0.75rem;
            color: #005a9c;
            text-decoration: none;
            background: white;
            border-radius: 6px;
            margin-bottom: 0.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            transition: all 0.2s ease;
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
            margin-left: 1rem;
            background: #f8f9fa;
            border-left: 3px solid #005a9c;
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
            color: #212529;
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
            
            .navigation {
                background: #3a3a3a;
                border-bottom-color: #555;
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
    mobile_js = """
    <script>
        function showSection(sectionId) {
            // Hide all sections
            const sections = document.querySelectorAll('.content-section');
            sections.forEach(section => {
                section.classList.remove('active');
            });
            
            // Show navigation if going back to nav
            const nav = document.querySelector('.navigation');
            if (sectionId === 'nav') {
                nav.style.display = 'block';
                return;
            }
            
            // Hide navigation and show selected section
            nav.style.display = 'none';
            const targetSection = document.getElementById(sectionId);
            if (targetSection) {
                targetSection.classList.add('active');
                window.scrollTo(0, 0);
            }
        }
        
        function goBackToNav() {
            showSection('nav');
        }
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            // Show navigation by default
            showSection('nav');
        });
    </script>
    """
    
    # Build navigation HTML
    def build_nav_html(nodes, level=0):
        html = ""
        for node in nodes:
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
                <button class="back-to-nav" onclick="goBackToNav()">← Back to Navigation</button>
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
</head>
<body>
    <div class="kb-container">
        <header class="kb-header">
            <h1 class="kb-title">{publication.title}</h1>
            <p class="kb-subtitle">Mobile Knowledge Base</p>
        </header>
        
        <nav class="navigation">
            <div class="nav-section">
                <div class="nav-title">Topics</div>
                {nav_html}
            </div>
        </nav>
        
        {content_html}
        
        <footer class="footer">
            Generated on {current_time}<br>
            Optimized for mobile devices
        </footer>
    </div>
    
    {mobile_js}
</body>
</html>'''
    
    return html_template

@pubs_bp.route('/<int:pub_id>/export/pdf', methods=['GET'])
def export_pdf(pub_id):
    """Export publication as PDF"""
    pub = Publication.query.get_or_404(pub_id)
    
    try:
        # Build the hierarchical structure
        def serialize_node(node):
            topic_data = node.topic.to_dict() if node.topic else {'title': 'Unknown', 'content': ''}
            return {
                'id': node.id,
                'topic_id': node.topic_id,
                'title': topic_data.get('title', 'Untitled'),
                'content': topic_data.get('content', ''),
                'position': node.position,
                'children': sorted([serialize_node(c) for c in node.children],
                                 key=lambda x: x['position'])
            }
        
        top_nodes = [n for n in pub.nodes if n.parent_id is None]
        tree = sorted([serialize_node(n) for n in top_nodes],
                      key=lambda x: x['position'])
        
        # Generate PDF
        pdf_buffer = generate_pdf(pub, tree)
        
        response = make_response(pdf_buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="{pub.title}.pdf"'
        
        pdf_buffer.close()
        return response
        
    except Exception as e:
        # Fallback to error message if PDF generation fails
        error_html = f"""
        <html>
        <head>
            <title>PDF Export Error - {pub.title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; }}
                .error {{ background: #f8d7da; border: 1px solid #f5c6cb; padding: 15px; border-radius: 5px; color: #721c24; }}
                .button {{ display: inline-block; margin-top: 15px; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 3px; }}
            </style>
        </head>
        <body>
            <div class="error">
                <h2>PDF Export Error</h2>
                <p>Unable to generate PDF for "<strong>{pub.title}</strong>".</p>
                <p>Error: {str(e)}</p>
                <p>Please try the Mobile Knowledge Base export instead:</p>
                <a href="/api/publications/{pub_id}/export/mobile-kb" class="button">Export as Mobile Knowledge Base</a>
            </div>
        </body>
        </html>
        """
        
        response = make_response(error_html)
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        return response

def generate_pdf(publication, tree):
    """Generate PDF document from publication tree"""
    buffer = io.BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )
    
    # Build content
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.grey
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        spaceBefore=20
    )
    
    content_style = ParagraphStyle(
        'CustomContent',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=12,
        alignment=TA_JUSTIFY,
        leftIndent=0,
        rightIndent=0
    )
    
    # Title page
    story.append(Paragraph(publication.title, title_style))
    if publication.description:
        story.append(Paragraph(publication.description, subtitle_style))
    
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", subtitle_style))
    story.append(PageBreak())
    
    # Table of contents
    story.append(Paragraph("Table of Contents", heading_style))
    story.append(Spacer(1, 12))
    
    def add_toc_entries(nodes, level=0):
        for node in nodes:
            # Create proper indentation and numbering for TOC
            indent = "    " * level
            # Use different bullet styles for different levels
            if level == 0:
                bullet = "•"
            elif level == 1:
                bullet = "◦"
            else:
                bullet = "▪"
            
            toc_style = ParagraphStyle(
                f'TOCLevel{level}',
                parent=content_style,
                leftIndent=level * 20,
                fontSize=11 - (level * 0.5),
                spaceAfter=6
            )
            story.append(Paragraph(f"{indent}{bullet} {node['title']}", toc_style))
            
            if node['children']:
                add_toc_entries(node['children'], level + 1)
    
    add_toc_entries(tree)
    story.append(PageBreak())
    
    # Content sections
    def add_content_nodes(nodes, level=0):
        for node in nodes:
            # Create proper heading hierarchy based on collection structure
            heading_text = node['title']
            
            # Define heading styles for different hierarchy levels
            if level == 0:
                # Top-level topics: Main headings (H1 equivalent)
                current_heading_style = ParagraphStyle(
                    'MainHeading',
                    parent=styles['Heading1'],
                    fontSize=18,
                    spaceAfter=16,
                    spaceBefore=24,
                    textColor=colors.black,
                    keepWithNext=1
                )
            elif level == 1:
                # Second-level topics: Sub-headings (H2 equivalent)
                current_heading_style = ParagraphStyle(
                    'SubHeading',
                    parent=styles['Heading2'],
                    fontSize=15,
                    spaceAfter=12,
                    spaceBefore=20,
                    leftIndent=0,
                    textColor=colors.black,
                    keepWithNext=1
                )
            elif level == 2:
                # Third-level topics: Minor headings (H3 equivalent)
                current_heading_style = ParagraphStyle(
                    'MinorHeading',
                    parent=styles['Heading3'],
                    fontSize=13,
                    spaceAfter=10,
                    spaceBefore=16,
                    leftIndent=0,
                    textColor=colors.black,
                    keepWithNext=1
                )
            else:
                # Deeper levels: Small headings (H4+ equivalent)
                current_heading_style = ParagraphStyle(
                    f'DeepHeading{level}',
                    parent=styles['Heading4'],
                    fontSize=max(11, 13 - (level - 2)),
                    spaceAfter=8,
                    spaceBefore=12,
                    leftIndent=0,
                    textColor=colors.black,
                    keepWithNext=1
                )
            
            story.append(Paragraph(heading_text, current_heading_style))
            
            # Add content with proper indentation for hierarchy
            if node['content']:
                # Convert markdown-like content to paragraphs
                content_paragraphs = convert_markdown_to_pdf_paragraphs(node['content'])
                for para in content_paragraphs:
                    # Create content style that matches the hierarchy level
                    level_content_style = ParagraphStyle(
                        f'ContentLevel{level}',
                        parent=content_style,
                        leftIndent=max(0, (level - 1) * 15),  # Slight indentation for sub-content
                        rightIndent=0,
                        spaceAfter=10,
                        alignment=TA_JUSTIFY
                    )
                    story.append(Paragraph(para, level_content_style))
            
            # Add spacing after content
            story.append(Spacer(1, 8))
            
            # Recursively add children with increased level
            if node['children']:
                add_content_nodes(node['children'], level + 1)
                
                # Add extra spacing after a section with children
                if level < 2:  # Only for top-level sections
                    story.append(Spacer(1, 16))
    
    add_content_nodes(tree)
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def convert_markdown_to_pdf_paragraphs(text):
    """Convert markdown-like text to PDF paragraphs with better hierarchy support"""
    if not text:
        return [""]
    
    lines = text.split('\n')
    paragraphs = []
    current_paragraph = []
    in_list = False
    list_items = []
    
    for line in lines:
        stripped = line.strip()
        
        # Handle headers (these will be rendered as bold text within content)
        if stripped.startswith('#'):
            # Finish any current paragraph or list
            if current_paragraph:
                paragraphs.append(' '.join(current_paragraph))
                current_paragraph = []
            if in_list:
                # Create a proper list paragraph
                list_content = '<br/>'.join([f"• {item}" for item in list_items])
                paragraphs.append(list_content)
                list_items = []
                in_list = False
            
            # Remove markdown headers since we're using the collection hierarchy
            # Convert to emphasized text instead
            header_level = len(stripped) - len(stripped.lstrip('#'))
            header_text = stripped.lstrip('#').strip()
            if header_text:
                paragraphs.append(f"<b><i>{header_text}</i></b>")
            
        # Handle bullet points and create proper lists
        elif stripped.startswith('-') or stripped.startswith('*'):
            if current_paragraph:
                paragraphs.append(' '.join(current_paragraph))
                current_paragraph = []
            
            bullet_text = stripped[1:].strip()
            list_items.append(bullet_text)
            in_list = True
            
        # Handle numbered lists
        elif any(stripped.startswith(f"{i}. ") for i in range(1, 10)):
            if current_paragraph:
                paragraphs.append(' '.join(current_paragraph))
                current_paragraph = []
            if in_list and list_items:
                # Finish the bullet list first
                list_content = '<br/>'.join([f"• {item}" for item in list_items])
                paragraphs.append(list_content)
                list_items = []
            
            numbered_text = stripped[3:].strip()  # Remove "1. " etc.
            list_items.append(numbered_text)
            in_list = True
            
        # Handle empty lines (paragraph breaks)
        elif not stripped:
            if current_paragraph:
                paragraphs.append(' '.join(current_paragraph))
                current_paragraph = []
            if in_list:
                # Finish the current list
                if list_items:
                    list_content = '<br/>'.join([f"• {item}" for item in list_items])
                    paragraphs.append(list_content)
                    list_items = []
                in_list = False
                
        # Regular text
        else:
            if in_list:
                # Finish the current list first
                if list_items:
                    list_content = '<br/>'.join([f"• {item}" for item in list_items])
                    paragraphs.append(list_content)
                    list_items = []
                in_list = False
            
            # Handle basic markdown formatting within text
            formatted_line = stripped
            # Bold text
            formatted_line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', formatted_line)
            # Italic text
            formatted_line = re.sub(r'\*(.*?)\*', r'<i>\1</i>', formatted_line)
            # Code
            formatted_line = re.sub(r'`(.*?)`', r'<font face="Courier">\1</font>', formatted_line)
            
            current_paragraph.append(formatted_line)
    
    # Add any remaining content
    if current_paragraph:
        paragraphs.append(' '.join(current_paragraph))
    if in_list and list_items:
        list_content = '<br/>'.join([f"• {item}" for item in list_items])
        paragraphs.append(list_content)
    
    return [p for p in paragraphs if p.strip()]

def convert_markdown_to_html(markdown_text):
    """Basic markdown to HTML conversion for mobile display"""
    if not markdown_text:
        return "<p>No content available.</p>"
    
    html = markdown_text
    
    # Headers
    html = re.sub(r'^### (.*$)', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*$)', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.*$)', r'<h2>\1</h2>', html, flags=re.MULTILINE)  # Convert h1 to h2 since page already has h1
    
    # Bold and italic
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    
    # Code
    html = re.sub(r'`(.*?)`', r'<code>\1</code>', html)
    
    # Links
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', html)
    
    # Lists
    lines = html.split('\n')
    in_list = False
    result_lines = []
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('- ') or stripped.startswith('* '):
            if not in_list:
                result_lines.append('<ul>')
                in_list = True
            result_lines.append(f'<li>{stripped[2:]}</li>')
        elif stripped.startswith(('1. ', '2. ', '3. ', '4. ', '5. ', '6. ', '7. ', '8. ', '9. ')):
            if not in_list:
                result_lines.append('<ol>')
                in_list = True
            result_lines.append(f'<li>{stripped[3:]}</li>')
        else:
            if in_list:
                result_lines.append('</ul>' if result_lines[-2].startswith('<li>') else '</ol>')
                in_list = False
            if stripped:
                result_lines.append(f'<p>{stripped}</p>')
            else:
                result_lines.append('<br>')
    
    if in_list:
        result_lines.append('</ul>')
    
    return '\n'.join(result_lines)
