from flask import Blueprint, Flask, request, jsonify, render_template_string, make_response, current_app
from flask_jwt_extended import jwt_required
from ..models import db, Publication, PublicationNode, Topic, Snippet, EntityTag
from datetime import datetime
import re
import os
import base64
import mimetypes
import io
import json
import traceback
import tempfile
import shutil
import requests as _http
from bs4 import BeautifulSoup
import mistune

from ..services.pdf_generator import generate_pdf
from ..services.kb_generator import generate_mobile_kb_html



def resolve_snippets(content, selected_tag_ids):
    """Replace <div class="sd-snippet-ref" data-snippet-id="X"> placeholders.

    Snippets with no tags are universal and always included.
    Snippets with tags are only included when at least one of their tags
    appears in selected_tag_ids; otherwise the placeholder is removed.
    """
    if not content:
        return content
    soup = BeautifulSoup(content, 'html.parser')
    placeholders = soup.find_all('div', class_='sd-snippet-ref')
    if not placeholders:
        return content

    selected = set(int(t) for t in selected_tag_ids if str(t).isdigit()) if selected_tag_ids else set()

    def remove_adjacent_brs(element):
        """Remove <br> siblings (and blank text nodes) immediately before/after element."""
        nxt = element.next_sibling
        while nxt and (getattr(nxt, 'name', None) == 'br' or (isinstance(nxt, str) and not nxt.strip())):
            to_remove = nxt
            nxt = nxt.next_sibling
            to_remove.extract()
        prev = element.previous_sibling
        while prev and (getattr(prev, 'name', None) == 'br' or (isinstance(prev, str) and not prev.strip())):
            to_remove = prev
            prev = prev.previous_sibling
            to_remove.extract()

    for placeholder in placeholders:
        raw_id = placeholder.get('data-snippet-id')
        if not raw_id or not str(raw_id).isdigit():
            remove_adjacent_brs(placeholder)
            placeholder.decompose()
            continue

        snippet_id = int(raw_id)

        snippet_tag_ids = {
            et.tag_id for et in EntityTag.query.filter_by(entity_type='snippet', entity_id=snippet_id).all()
        }

        # Untagged snippets are universal — always include.
        # Tagged snippets only appear when at least one of their tags is selected.
        if snippet_tag_ids and not (snippet_tag_ids & selected):
            remove_adjacent_brs(placeholder)
            placeholder.decompose()
            continue

        snippet = Snippet.query.get(snippet_id)
        if snippet and snippet.content:
            snippet_html = mistune.html(snippet.content)
            placeholder.replace_with(BeautifulSoup(snippet_html, 'html.parser'))
        else:
            remove_adjacent_brs(placeholder)
            placeholder.decompose()

    return str(soup)

pubs_bp = Blueprint(
    'publications',
    __name__,
    url_prefix='/api/publications',
)

@pubs_bp.route('', methods=['GET'])
@jwt_required()
def list_pubs():
    """List publications. Supports ?page=&limit= for pagination."""
    page = max(1, request.args.get('page', 1, type=int))
    limit = min(100, max(1, request.args.get('limit', 50, type=int)))

    all_pubs = Publication.query.order_by(Publication.created_at.desc()).all()

    # Group by title and keep only the latest version of each
    latest_pubs = {}
    for pub in all_pubs:
        if pub.title not in latest_pubs:
            latest_pubs[pub.title] = pub

    result = sorted(latest_pubs.values(), key=lambda p: p.created_at, reverse=True)
    total = len(result)
    paginated = result[(page - 1) * limit : page * limit]

    return jsonify({
        'publications': [p.to_dict() for p in paginated],
        'total': total,
        'page': page,
        'limit': limit,
        'pages': max(1, (total + limit - 1) // limit),
    }), 200

@pubs_bp.route('', methods=['POST'])
@jwt_required()
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
@jwt_required()
def get_pub(pub_id):
    p = Publication.query.get_or_404(pub_id)
    def serialize(node):
        # Prefer snapshots so the preview matches what would actually be exported
        title   = node.title_snapshot   or (node.topic.title   if node.topic else 'Untitled')
        content = node.content_snapshot or (node.topic.content if node.topic else '')
        return {
            'id': node.id,
            'title': title,
            'content': content,
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
@jwt_required()
def save_nodes(pub_id):
    payload = request.get_json()  # expect {"tree": [...]}
    PublicationNode.query.filter_by(publication_id=pub_id).delete()

    def walk(nodes, parent_id=None):
        for idx, n in enumerate(nodes):
            # Get the topic to capture snapshot data
            topic = Topic.query.get(n['topic_id'])
            if not topic:
                continue  # Skip if topic doesn't exist
                
            node = PublicationNode(
                publication_id=pub_id,
                topic_id=n['topic_id'],
                parent_id=parent_id,
                position=idx,
                title_snapshot=topic.title,
                content_snapshot=topic.content
            )
            db.session.add(node)
            db.session.flush()  # assign node.id
            if n.get('children'):
                walk(n['children'], node.id)

    walk(payload['tree'])
    db.session.commit()
    return jsonify({'message': 'saved'}), 200

@pubs_bp.route('/<int:pub_id>/export/mobile-kb', methods=['GET'])
@jwt_required()
def export_mobile_knowledge_base(pub_id):
    """Export publication as mobile-first knowledge base HTML"""
    pub = Publication.query.get_or_404(pub_id)
    tag_ids = [t for t in request.args.getlist('tag_ids') if str(t).isdigit()]

    # Build the hierarchical structure
    def serialize_node(node):
        # Prefer snapshots captured at publish time; fallback to current topic
        title = node.title_snapshot or (node.topic.title if node.topic else 'Untitled')
        content = node.content_snapshot or (node.topic.content if node.topic else '')
        content = resolve_snippets(content, tag_ids)
        return {
            'id': node.id,
            'topic_id': node.topic_id,
            'title': title or 'Untitled',
            'content': content or '',
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

@pubs_bp.route('/<int:pub_id>/preview/mobile-kb', methods=['GET'])
@jwt_required()
def preview_mobile_knowledge_base(pub_id):
    """Preview publication as mobile-first knowledge base HTML in browser"""
    pub = Publication.query.get_or_404(pub_id)
    tag_ids = [t for t in request.args.getlist('tag_ids') if str(t).isdigit()]

    # Build the hierarchical structure (same as export)
    def serialize_node(node):
        title = node.title_snapshot or (node.topic.title if node.topic else 'Untitled')
        content = node.content_snapshot or (node.topic.content if node.topic else '')
        content = resolve_snippets(content, tag_ids)
        return {
            'id': node.id,
            'topic_id': node.topic_id,
            'title': title or 'Untitled',
            'content': content or '',
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
    # No attachment header - this will display directly in browser
    return response

@pubs_bp.route('/<int:pub_id>/export/pdf', methods=['GET'])
@jwt_required()
def export_pdf(pub_id):
    """Export publication as PDF with optional formatting configuration and background image"""
    pub = Publication.query.get_or_404(pub_id)
    # Define config_type early to avoid unbound in except
    config_type = request.args.get('format', 'default')
    
    try:
        current_app.logger.debug(f"DEBUG: export_pdf start pub_id={pub_id}, config_type={config_type}")
        # Get format configuration from query parameter
        
        # Get optional background image path from query parameter
        background_image = request.args.get('background_image')
        background_image_path = None
        
        if background_image:
            # Build path to background image (assumes images are in a backgrounds folder)
            backgrounds_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'backgrounds')
            background_image_path = os.path.join(backgrounds_dir, background_image)
            
            # Security check: ensure the file exists and is an image
            if not (os.path.exists(background_image_path) and 
                   background_image.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))):
                background_image_path = None
        
        # Validate config type
        valid_configs = ['default', 'corporate', 'academic', 'compact', 'organization']
        if config_type not in valid_configs:
            config_type = 'default'

        # Audience tag IDs for snippet filtering
        tag_ids = [t for t in request.args.getlist('tag_ids') if str(t).isdigit()]

        # Build the hierarchical structure
        def serialize_node(node):
            # Prefer snapshots captured at publish time; fall back to live topic
            title = None
            content = None
            try:
                title = getattr(node, 'title_snapshot', None)
                content = getattr(node, 'content_snapshot', None)
            except Exception:
                title = None
                content = None

            if (title is None or title == '') or (content is None):
                topic = node.topic if hasattr(node, 'topic') else None
                if topic:
                    try:
                        td = topic.to_dict()
                        title = title if title not in (None, '') else td.get('title', 'Untitled')
                        # If snapshot missing, use topic content
                        content = content if content is not None else td.get('content', '')
                    except Exception:
                        title = title if title not in (None, '') else 'Untitled'
                        content = content if content is not None else ''
                else:
                    title = title if title not in (None, '') else 'Unknown'
                    content = content if content is not None else ''

            content = resolve_snippets(content, tag_ids)

            return {
                'id': node.id,
                'topic_id': node.topic_id,
                'title': title if (title is not None and title != '') else 'Untitled',
                'content': content or '',
                'position': node.position,
                'children': sorted([serialize_node(c) for c in node.children], key=lambda x: x['position'])
            }
        
        top_nodes = [n for n in pub.nodes if n.parent_id is None]
        tree = sorted([serialize_node(n) for n in top_nodes],
                      key=lambda x: x['position'])
        
        # Generate PDF with specified configuration and optional background image
        pdf_buffer = generate_pdf(pub, tree, config_type, background_image_path)
        try:
            pdf_bytes = pdf_buffer.getvalue()
        finally:
            try:
                pdf_buffer.close()
            except Exception:
                pass
        current_app.logger.debug(f"DEBUG: export_pdf generated bytes={len(pdf_bytes)}")

        # Validate PDF signature
        if not pdf_bytes or not pdf_bytes.startswith(b'%PDF'):
            prefix = pdf_bytes[:128] if pdf_bytes else b''
            current_app.logger.debug(f"ERROR: Invalid PDF output. size={0 if not pdf_bytes else len(pdf_bytes)}, prefix={prefix!r}")
            return make_response(jsonify({'error': 'Invalid PDF output'}), 500)

        response = make_response(pdf_bytes)
        response.headers['Content-Type'] = 'application/pdf'
        # Prefer inline display to help browsers render instead of download only
        response.headers['Content-Disposition'] = f'inline; filename="{pub.title}_{config_type}.pdf"'
        response.headers['Content-Length'] = str(len(pdf_bytes))
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
                .config-info {{ background: #d1ecf1; border: 1px solid #bee5eb; padding: 15px; border-radius: 5px; color: #0c5460; margin: 15px 0; }}
                .button {{ display: inline-block; margin-top: 15px; padding: 10px 20px; background: #00796B; color: white; text-decoration: none; border-radius: 3px; }}
            </style>
        </head>
        <body>
            <div class="error">
                <h2>PDF Export Error</h2>
                <p>Unable to generate PDF for "<strong>{pub.title}</strong>" with format "<strong>{config_type or 'default'}</strong>".</p>
                <p>Error: {str(e)}</p>
            </div>
            <div class="config-info">
                <h3>Available PDF Formats:</h3>
                <ul>
                    <li><strong>default</strong> - Standard formatting</li>
                    <li><strong>corporate</strong> - Formal business document style</li>
                    <li><strong>academic</strong> - Academic paper formatting</li>
                    <li><strong>compact</strong> - Condensed layout for dense content</li>
                </ul>
                <p>Usage: Add <code>?format=corporate</code> to the URL</p>
                <p>Example: <code>/api/publications/{pub_id}/export/pdf?format=corporate</code></p>
                <a href="/api/publications/{pub_id}/export/mobile-kb" class="button">Export as Mobile Knowledge Base</a>
            </div>
        </body>
        </html>
        """
        
    response = make_response(error_html, 500)
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    return response
