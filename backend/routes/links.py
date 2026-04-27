from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from ..models import db, Link, Topic, TopicLink
from ..utils.link_reference_codes import assign_missing_link_reference_code, resolve_link_reference_code
from sqlalchemy import or_, and_, func
import re

links_bp = Blueprint('links', __name__, url_prefix='/api/links')

@links_bp.route('/', methods=['GET'])
@jwt_required()
def get_links():
    """Get all links with optional filtering"""
    try:
        # Query parameters
        link_type = request.args.get('type')
        is_active = request.args.get('active')
        search = request.args.get('search')
        reference_code = request.args.get('reference_code')
        include_usage = request.args.get('include_usage', 'false').lower() == 'true'
        
        # Build query
        query = Link.query
        
        if link_type:
            query = query.filter(Link.link_type == link_type)
        
        if is_active is not None:
            active_bool = is_active.lower() == 'true'
            query = query.filter(Link.is_active == active_bool)
        
        if reference_code:
            query = query.filter(Link.reference_code == reference_code)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Link.title.ilike(search_pattern),
                    Link.description.ilike(search_pattern),
                    Link.reference_code.ilike(search_pattern),
                    Link.url.ilike(search_pattern)
                )
            )
        
        # Order by most recently updated
        links = query.order_by(Link.updated_at.desc()).all()
        
        # Convert to dict
        links_data = [link.to_dict(include_usage=include_usage) for link in links]

        return jsonify({
            'links': links_data,
            'total_count': len(links_data)
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching links: {str(e)}")
        return jsonify({'error': f'Failed to fetch links: {str(e)}'}), 500

@links_bp.route('/', methods=['POST'])
@jwt_required()
def create_link():
    """Create a new reusable link"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('title'):
            return jsonify({'error': 'Title is required'}), 400
        
        if not data.get('url'):
            return jsonify({'error': 'URL is required'}), 400
        
        try:
            reference_code = resolve_link_reference_code(Link, data.get('reference_code'))
        except ValueError as exc:
            return jsonify({'error': str(exc)}), 400
        
        # Create new link
        link = Link(
            title=data['title'],
            url=data['url'],
            description=data.get('description'),
            reference_code=reference_code,
            link_type=data.get('link_type', 'other'),
            is_internal=data.get('is_internal', False),
            is_active=data.get('is_active', True),
            created_by=data.get('created_by')
        )
        
        db.session.add(link)
        db.session.commit()
        
        current_app.logger.info(f"Created new link: {link.title} ({link.reference_code})")
        return jsonify(link.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating link: {str(e)}")
        return jsonify({'error': f'Failed to create link: {str(e)}'}), 500

@links_bp.route('/<int:link_id>', methods=['GET'])
@jwt_required()
def get_link(link_id):
    """Get a specific link with usage information"""
    try:
        link = Link.query.get_or_404(link_id)
        return jsonify(link.to_dict(include_usage=True)), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching link {link_id}: {str(e)}")
        return jsonify({'error': f'Failed to fetch link: {str(e)}'}), 500

@links_bp.route('/<int:link_id>', methods=['PUT'])
@jwt_required()
def update_link(link_id):
    """Update an existing link"""
    try:
        link = Link.query.get_or_404(link_id)
        data = request.get_json()
        
        # Update fields
        if 'title' in data:
            link.title = data['title']
        if 'url' in data:
            link.url = data['url']
        if 'description' in data:
            link.description = data['description']
        if 'reference_code' in data:
            try:
                link.reference_code = resolve_link_reference_code(
                    Link,
                    data['reference_code'],
                    exclude_link_id=link.id,
                )
            except ValueError as exc:
                return jsonify({'error': str(exc)}), 400
        if 'link_type' in data:
            link.link_type = data['link_type']
        if 'is_internal' in data:
            link.is_internal = data['is_internal']
        if 'is_active' in data:
            link.is_active = data['is_active']

        if 'reference_code' not in data:
            assign_missing_link_reference_code(link, Link)
        
        db.session.commit()
        
        current_app.logger.info(f"Updated link: {link.title} ({link.reference_code})")
        return jsonify(link.to_dict(include_usage=True)), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating link {link_id}: {str(e)}")
        return jsonify({'error': f'Failed to update link: {str(e)}'}), 500

@links_bp.route('/<int:link_id>', methods=['DELETE'])
@jwt_required()
def delete_link(link_id):
    """Delete a link (will also remove from all topics)"""
    try:
        link = Link.query.get_or_404(link_id)
        
        # Get usage count before deletion
        usage_count = len(link.topic_links)
        title = link.title
        
        db.session.delete(link)
        db.session.commit()
        
        current_app.logger.info(f"Deleted link: {title} (was used in {usage_count} topics)")
        return jsonify({
            'message': f'Link deleted successfully (removed from {usage_count} topics)',
            'usage_count': usage_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting link {link_id}: {str(e)}")
        return jsonify({'error': f'Failed to delete link: {str(e)}'}), 500

@links_bp.route('/reference/<reference_code>', methods=['GET'])
@jwt_required()
def get_link_by_reference(reference_code):
    """Get a link by its reference code (e.g., AB-123)"""
    try:
        link = Link.query.filter_by(reference_code=reference_code).first()
        if not link:
            return jsonify({'error': f'Link with reference code "{reference_code}" not found'}), 404
        
        return jsonify(link.to_dict(include_usage=True)), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching link by reference {reference_code}: {str(e)}")
        return jsonify({'error': f'Failed to fetch link: {str(e)}'}), 500

@links_bp.route('/types', methods=['GET'])
@jwt_required()
def get_link_types():
    """Get available link types"""
    return jsonify({
        'link_types': Link.LINK_TYPES,
        'descriptions': {
            'form': 'Forms and applications',
            'document': 'Documentation and guides',
            'website': 'External websites',
            'policy': 'Policies and regulations',
            'procedure': 'Standard operating procedures',
            'regulation': 'Legal regulations',
            'other': 'Other types of links'
        }
    }), 200

# Topic-Link Association Routes

@links_bp.route('/topics/<int:topic_id>/links', methods=['GET'])
@jwt_required()
def get_topic_links(topic_id):
    """Get all links associated with a specific topic"""
    try:
        topic = Topic.query.get_or_404(topic_id)
        
        topic_links = TopicLink.query.filter_by(topic_id=topic_id)\
                                    .order_by(TopicLink.position)\
                                    .all()
        
        return jsonify({
            'topic_id': topic_id,
            'topic_title': topic.title,
            'links': [tl.to_dict() for tl in topic_links],
            'total_count': len(topic_links)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching links for topic {topic_id}: {str(e)}")
        return jsonify({'error': f'Failed to fetch topic links: {str(e)}'}), 500

@links_bp.route('/topics/<int:topic_id>/links', methods=['POST'])
@jwt_required()
def add_link_to_topic(topic_id):
    """Associate a link with a topic"""
    try:
        data = request.get_json()
        link_id = data.get('link_id')
        
        if not link_id:
            return jsonify({'error': 'link_id is required'}), 400
        
        # Verify topic and link exist
        topic = Topic.query.get_or_404(topic_id)
        link = Link.query.get_or_404(link_id)
        
        # Check if association already exists
        existing = TopicLink.query.filter_by(topic_id=topic_id, link_id=link_id).first()
        if existing:
            return jsonify({'error': 'Link is already associated with this topic'}), 400
        
        # Get next position
        max_position = db.session.query(func.max(TopicLink.position))\
                                .filter_by(topic_id=topic_id)\
                                .scalar() or 0
        
        # Create association
        topic_link = TopicLink(
            topic_id=topic_id,
            link_id=link_id,
            context=data.get('context'),
            position=max_position + 1
        )
        
        db.session.add(topic_link)
        db.session.commit()
        
        current_app.logger.info(f"Added link {link.title} to topic {topic.title}")
        return jsonify(topic_link.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error adding link to topic {topic_id}: {str(e)}")
        return jsonify({'error': f'Failed to add link to topic: {str(e)}'}), 500

@links_bp.route('/topics/<int:topic_id>/links/<int:link_id>', methods=['DELETE'])
@jwt_required()
def remove_link_from_topic(topic_id, link_id):
    """Remove a link association from a topic"""
    try:
        topic_link = TopicLink.query.filter_by(topic_id=topic_id, link_id=link_id).first()
        if not topic_link:
            return jsonify({'error': 'Link association not found'}), 404
        
        db.session.delete(topic_link)
        db.session.commit()
        
        current_app.logger.info(f"Removed link {link_id} from topic {topic_id}")
        return jsonify({'message': 'Link removed from topic successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error removing link from topic: {str(e)}")
        return jsonify({'error': f'Failed to remove link from topic: {str(e)}'}), 500

@links_bp.route('/search/content', methods=['POST'])
@jwt_required()
def search_link_references_in_content():
    """Search for potential link references in topic content"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        
        if not content:
            return jsonify({'potential_links': [], 'suggestions': []}), 200
        
        # Find potential reference codes (e.g., AB-123, FORM-456, DOC-789)
        reference_patterns = [
            r'\b[A-Z]{1,4}-\d{1,6}\b',  # AB-123, FORM-456
            r'\bFORM\s+[A-Z]?-?\d+\b',  # FORM 123, FORM A-123
            r'\bDOC\s+[A-Z]?-?\d+\b',   # DOC 456, DOC B-456
        ]
        
        potential_refs = set()
        for pattern in reference_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                potential_refs.add(match.group().upper())
        
        # Check which references already exist as links
        existing_links = []
        suggestions = []
        
        for ref in potential_refs:
            existing = Link.query.filter_by(reference_code=ref).first()
            if existing:
                existing_links.append({
                    'reference_code': ref,
                    'link': existing.to_dict(),
                    'found_in_content': True
                })
            else:
                suggestions.append({
                    'reference_code': ref,
                    'suggested_title': f"Document {ref}",
                    'needs_creation': True
                })
        
        return jsonify({
            'potential_links': existing_links,
            'suggestions': suggestions,
            'found_references': list(potential_refs)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error searching link references: {str(e)}")
        return jsonify({'error': f'Failed to search link references: {str(e)}'}), 500


@links_bp.route('/usage-summary', methods=['GET'])
@jwt_required()
def links_usage_summary():
    """Per-link collection + project usage, via topic_links → collection_topic_tree."""
    try:
        from sqlalchemy import select as sa_select
        from ..models import Collection, Project, collection_topic_tree

        # Fetch all topic-link associations with collection/project info in one query
        rows = db.session.execute(
            sa_select(
                TopicLink.link_id,
                Collection.id.label('col_id'),
                Collection.name.label('col_name'),
                Project.id.label('proj_id'),
                Project.name.label('proj_name'),
            )
            .join(collection_topic_tree, collection_topic_tree.c.topic_id == TopicLink.topic_id)
            .join(Collection, collection_topic_tree.c.collection_id == Collection.id)
            .outerjoin(Project, Collection.project_id == Project.id)
        ).fetchall()

        usage = {}
        for row in rows:
            lid = str(row.link_id)
            if lid not in usage:
                usage[lid] = {'collections': {}, 'projects': {}}
            usage[lid]['collections'][row.col_id] = row.col_name
            if row.proj_id:
                usage[lid]['projects'][row.proj_id] = row.proj_name

        result = {
            lid: {
                'collections': [{'id': k, 'name': v} for k, v in d['collections'].items()],
                'projects':    [{'id': k, 'name': v} for k, v in d['projects'].items()],
            }
            for lid, d in usage.items()
        }
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.exception("Failed to build link usage summary")
        return jsonify({'error': str(e)}), 500
