from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from datetime import datetime, timezone, timedelta
from ..models import db, Collection, Topic, collection_topic_tree, Project, Publication, PublicationNode, build_variable_mapping_for_collection, substitute_variables_in_text
from ..utils.audit import log_audit

collections_bp = Blueprint('collections', __name__, url_prefix='/api/collections')

@collections_bp.route('', methods=['GET'])
@collections_bp.route('/', methods=['GET'])
@jwt_required()
def list_collections():
    current_app.logger.debug(f" Collections GET request received")
    try:
        from sqlalchemy.orm import joinedload
        from sqlalchemy import func as sqlfunc

        # Load all collections with their projects in one query (no topics JOIN)
        all_cols = Collection.query \
            .options(joinedload(Collection.project)) \
            .order_by(Collection.position).all()

        # Count topics per collection in a single GROUP BY query
        topic_counts = dict(
            db.session.query(
                collection_topic_tree.c.collection_id,
                sqlfunc.count(collection_topic_tree.c.topic_id)
            ).group_by(collection_topic_tree.c.collection_id).all()
        )

        col_map = {c.id: c for c in all_cols}

        def build_col_dict(col):
            return {
                'id': col.id,
                'name': col.name,
                'form_number': col.form_number,
                'description': col.description,
                'position': col.position,
                'parentId': col.parent_id,
                'projectId': col.project_id,
                'archived': col.archived,
                'topics_count': topic_counts.get(col.id, 0),
                'created_at': col.created_at.isoformat() if col.created_at else None,
                'updated_at': col.updated_at.isoformat() if col.updated_at else None,
                'projectName': col.project.name if col.project else None,
                'topics': [],  # Full topic tree loaded per-collection on the detail page
                'children': [
                    build_col_dict(col_map[c.id])
                    for c in sorted(
                        [c for c in all_cols if c.parent_id == col.id],
                        key=lambda x: x.position
                    )
                ]
            }

        roots = sorted([c for c in all_cols if c.parent_id is None], key=lambda x: x.position)
        tree = [build_col_dict(c) for c in roots]
        current_app.logger.info(f" Returning {len(roots)} root collections ({len(all_cols)} total)")
        return jsonify(tree), 200
    except Exception as e:
        current_app.logger.error(f" Error in list_collections: {e}")
        return jsonify({"error": str(e)}), 500

@collections_bp.route('/<int:collection_id>', methods=['GET'])
@jwt_required()
def get_collection(collection_id):
    """Get a single collection with its full topic hierarchy."""
    try:
        col = db.session.get(Collection, collection_id)
        if not col:
            return jsonify({"error": "Collection not found"}), 404
        return jsonify(col.to_dict(include_children=True, include_topics=True)), 200
    except Exception as e:
        current_app.logger.exception(f"Error in get_collection {collection_id}: {e}")
        return jsonify({"error": str(e)}), 500


@jwt_required()
def get_collections_stats():
    """Get statistics for collections dashboard"""
    try:
        from sqlalchemy import func as sqlfunc

        total_collections = db.session.query(sqlfunc.count(Collection.id)).scalar() or 0
        root_collections = db.session.query(sqlfunc.count(Collection.id)).filter_by(parent_id=None).scalar() or 0

        # Count total topics via pivot table (single query, no lazy loading)
        total_topics = db.session.query(sqlfunc.count(collection_topic_tree.c.topic_id)).scalar() or 0

        now = datetime.utcnow()
        one_week_ago = now - timedelta(days=7)
        new_this_week = db.session.query(sqlfunc.count(Collection.id))\
            .filter(Collection.created_at >= one_week_ago).scalar() or 0

        avg_topics = round(total_topics / total_collections) if total_collections > 0 else 0

        stats = {
            'total': total_collections,
            'active': total_collections,
            'totalTopics': total_topics,
            'newThisWeek': new_this_week,
            'avgTopics': avg_topics,
            'rootCollections': root_collections,
        }

        current_app.logger.debug(f"📊 Collections stats: {stats}")
        return jsonify(stats), 200

    except Exception as e:
        current_app.logger.error(f" Error calculating collections stats: {e}")
        return jsonify({"error": str(e)}), 500

@collections_bp.route('', methods=['PUT'])
@collections_bp.route('/', methods=['PUT'])
@jwt_required()
def update_collections():
    """
    Expect payload: an array of nested nodes:
    [
      { id, parentId, position, children:[ ... ], topics: [...] },
      …
    ]
    """
    payload = request.get_json()
    current_app.logger.debug(f" Updating collections with payload: {payload}")

    def walk(nodes):
      for node in nodes:
        col = Collection.query.get(node['id'])
        if not col:
            current_app.logger.warning(f" Collection {node['id']} not found, skipping")
            continue
        
        # Update collection properties
        col.parent_id = node.get('parentId')
        col.position  = node.get('position', 0)
        
        # Handle topics assignment
        if 'topics' in node:
            current_app.logger.debug(f"📋 Updating topics for collection {col.id}: {node['topics']}")
            
            # Clear existing relationships for this collection
            db.session.execute(
                collection_topic_tree.delete().where(
                    collection_topic_tree.c.collection_id == col.id
                )
            )
            
            # Add new relationships with hierarchical support
            def add_topics_recursively(topics, parent_topic_id=None, collection=col):
                for idx, t in enumerate(topics):
                    current_app.logger.debug(f"➕ Adding topic {t['id']} to collection {collection.id} at position {idx}, parent: {parent_topic_id}")
                    db.session.execute(
                        collection_topic_tree.insert().values(
                            collection_id=collection.id,
                            topic_id=t['id'],
                            position=idx,
                            parent_topic_id=parent_topic_id
                        )
                    )
                    # Recursively add child topics
                    if 'children' in t and t['children']:
                        add_topics_recursively(t['children'], t['id'], collection)
            
            add_topics_recursively(node['topics'])
        
        # Recurse into children
        if node.get('children'):
          walk(node['children'])

    try:
        walk(payload)
        db.session.commit()
        current_app.logger.debug("✅ Collections updated successfully")
        return jsonify({'message': 'collection tree updated'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f" Error updating collections: {e}")
        return jsonify({'error': str(e)}), 500

@collections_bp.route('', methods=['POST'])
@jwt_required()
def create_collection():
    """
    Create a new collection.
    Expects JSON payload: { 
        "name": str, 
        "form_number": str,
        "description": str (optional),
        "parentId": int (optional), 
        "position": int (optional),
        "projectId": int (optional)
    }
    """
    data = request.get_json()
    name = data.get('name')
    form_number = data.get('form_number')
    description = data.get('description')
    parent_id = data.get('parentId')
    project_id = data.get('projectId')
    position = data.get('position', 0)

    if not name:
        return jsonify({'error': 'Collection name is required'}), 400
    
    if not form_number:
        return jsonify({'error': 'Collection ID (Form Number) is required'}), 400
    
    # Check if form_number already exists
    existing = Collection.query.filter_by(form_number=form_number).first()
    if existing:
        return jsonify({'error': f'Collection ID "{form_number}" already exists'}), 400

    new_collection = Collection(
        name=name, 
        form_number=form_number,
        description=description,
        parent_id=parent_id, 
        project_id=project_id,
        position=position
    )
    db.session.add(new_collection)
    db.session.commit()
    log_audit('create', 'collection', new_collection.id, details={'name': new_collection.name})
    return jsonify(new_collection.to_dict()), 201

@collections_bp.route('/<int:collection_id>', methods=['PUT'])
@jwt_required()
def update_collection(collection_id):
    """
    Update a specific collection's properties.
    Expects JSON payload with fields to update: { "name": str, "form_number": str, "description": str, etc. }
    """
    try:
        collection = Collection.query.get_or_404(collection_id)
        data = request.get_json()
        
        # Update allowed fields
        if 'name' in data:
            collection.name = data['name']
        
        if 'form_number' in data:
            # Check if form_number already exists (excluding current collection)
            existing = Collection.query.filter(
                Collection.form_number == data['form_number'],
                Collection.id != collection_id
            ).first()
            if existing:
                return jsonify({'error': f'Collection ID "{data["form_number"]}" already exists'}), 400
            collection.form_number = data['form_number']
        
        if 'description' in data:
            collection.description = data['description']
        
        if 'project_id' in data:
            collection.project_id = data['project_id']
        
        if 'parent_id' in data:
            collection.parent_id = data['parent_id']
        
        if 'position' in data:
            collection.position = data['position']
        
        db.session.commit()
        log_audit('update', 'collection', collection_id, details={'name': collection.name})
        return jsonify(collection.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@collections_bp.route('/<int:collection_id>/publish', methods=['POST'])
@jwt_required()
def publish_collection(collection_id):
    """
    Convert a collection to a publication for publishing.
    This creates a Publication and PublicationNode structure from the Collection.
    """
    current_app.logger.debug(f"🎯 PUBLISH: Starting publish for collection {collection_id}")
    try:
        collection = Collection.query.get_or_404(collection_id)
        current_app.logger.debug(f"🎯 PUBLISH: Found collection '{collection.name}' with {len(collection.topics)} topics")
        title_pattern = collection.name
        existing_pub = Publication.query.filter_by(title=title_pattern).first()

        # Determine which variable slugs are actually used in this collection's content
        current_app.logger.debug(f"🎯 PUBLISH: Scanning for variable tokens in collection content")
        import re
        token_re = re.compile(r'\{\{([A-Za-z0-9_\-]+)\}\}')
        used_slugs = set()
        def gather_used_slugs(coll):
            # Scan topics directly in this collection
            for t in coll.topics:
                for field in ((t.title or ''), (t.content or '')):
                    for slug in token_re.findall(field):
                        used_slugs.add(slug)
            # Recurse into child collections
            for child in getattr(coll, 'children', []) or []:
                gather_used_slugs(child)
        gather_used_slugs(collection)
        current_app.logger.debug(f"🎯 PUBLISH: Found variable tokens: {used_slugs}")

        if existing_pub:
            current_app.logger.debug(f"🎯 PUBLISH: Found existing publication '{existing_pub.title}' (id={existing_pub.id})")
            var_mapping, unresolved = build_variable_mapping_for_collection(collection.id)
            current_app.logger.debug(f"🎯 PUBLISH: Variable mapping: {var_mapping}, unresolved: {unresolved}")
            # Only consider unresolved variables that are actually used in this collection
            unresolved_in_use = [s for s in unresolved if s in used_slugs]
            current_app.logger.debug(f"🎯 PUBLISH: Unresolved variables in use: {unresolved_in_use}")
            if unresolved_in_use:
                current_app.logger.debug(f"🎯 PUBLISH: Blocking publish - unresolved variables detected")
                # Get detailed variable information for the frontend
                from ..models import Variable
                variables_info = []
                for var_slug in unresolved_in_use:
                    var = Variable.query.filter_by(slug=var_slug).first()
                    if var:
                        variables_info.append({
                            'id': var.id,
                            'slug': var.slug,
                            'name': var.name,
                            'description': var.description,
                            'values': [{'id': v.id, 'value': v.value, 'is_default': v.is_default} for v in var.values]
                        })
                
                return jsonify({
                    'error': 'Variables must be configured before publishing.',
                    'requires_variable_selection': True,
                    'unresolved_variables': unresolved_in_use,
                    'variables_info': variables_info,
                    'publish_setup_endpoint': f'/api/variables/collections/{collection.id}/publish-setup',
                    'collection_id': collection.id,
                    'message': f'This collection contains {len(unresolved_in_use)} variable(s) that need to be configured before publishing.'
                }), 400
            current_app.logger.debug(f"🎯 PUBLISH: Updating existing publication")
            existing_pub.description = collection.description or f"Published from Collection '{collection.name}' containing {len(collection.topics)} topics"
            existing_pub.form_number = collection.form_number
            # Use naive UTC to match DB column
            existing_pub.created_at = datetime.utcnow()
            current_app.logger.debug(f"🎯 PUBLISH: Deleting existing publication nodes")
            PublicationNode.query.filter_by(publication_id=existing_pub.id).delete()

            def rebuild_nodes(coll, parent_pub_node_id=None):
                current_app.logger.debug(f"🎯 PUBLISH: Rebuilding nodes for collection '{coll.name}'")
                nodes_created = []
                hierarchical_topics = coll.to_tree()
                current_app.logger.debug(f"🎯 PUBLISH: Collection tree has {len(hierarchical_topics)} top-level topics")

                def recurse(topics, parent_node_id):
                    for idx, topic_data in enumerate(topics):
                        current_app.logger.debug(f"🎯 PUBLISH: Processing topic {topic_data['id']} at position {idx}")
                        topic_obj = Topic.query.get(topic_data['id'])
                        if not topic_obj:
                            current_app.logger.debug(f"🎯 PUBLISH: WARNING - Topic {topic_data['id']} not found in database")
                            continue
                        title_sub = substitute_variables_in_text(getattr(topic_obj, 'title', '') or '', var_mapping) if topic_obj else ''
                        content_sub = substitute_variables_in_text(getattr(topic_obj, 'content', '') or '', var_mapping) if topic_obj else ''
                        # Create node with or without snapshots (for backwards compatibility)
                        try:
                            node = PublicationNode(
                                publication_id=existing_pub.id,
                                topic_id=topic_data['id'],
                                parent_id=parent_node_id,
                                position=idx,
                                title_snapshot=title_sub,
                                content_snapshot=content_sub
                            )
                        except Exception as e:
                            current_app.logger.debug(f"🎯 PUBLISH: Snapshot columns not available, creating without snapshots: {e}")
                            node = PublicationNode(
                                publication_id=existing_pub.id,
                                topic_id=topic_data['id'],
                                parent_id=parent_node_id,
                                position=idx
                            )
                        db.session.add(node)
                        db.session.flush()
                        nodes_created.append(node)
                        current_app.logger.debug(f"🎯 PUBLISH: Created node {node.id} for topic {topic_data['id']}")
                        if topic_data.get('children'):
                            recurse(topic_data['children'], node.id)

                recurse(hierarchical_topics, parent_pub_node_id)
                current_app.logger.debug(f"🎯 PUBLISH: Processing {len(coll.children)} child collections")
                for child_coll in sorted(coll.children, key=lambda x: x.position):
                    child_nodes = rebuild_nodes(child_coll, parent_pub_node_id)
                    nodes_created.extend(child_nodes)
                return nodes_created

            current_app.logger.debug(f"🎯 PUBLISH: Starting node rebuild for existing publication")
            nodes = rebuild_nodes(collection)
            current_app.logger.debug(f"🎯 PUBLISH: Committing {len(nodes)} nodes to database")
            db.session.commit()
            current_app.logger.debug(f"🎯 PUBLISH: Successfully updated existing publication {existing_pub.id}")
            return jsonify({
                'message': 'Publication updated with current collection content',
                'publication_id': existing_pub.id,
                'nodes_created': len(nodes),
                'redirect_url': f'/publications/{existing_pub.id}',
                'variable_mapping_used': var_mapping,
                'unresolved_variables': []
            }), 200

        # New publication path
        current_app.logger.debug(f"🎯 PUBLISH: Creating new publication")
        var_mapping, unresolved = build_variable_mapping_for_collection(collection.id)
        current_app.logger.debug(f"🎯 PUBLISH: Variable mapping: {var_mapping}, unresolved: {unresolved}")
        # Only consider unresolved variables that are actually used in this collection
        unresolved_in_use = [s for s in unresolved if s in used_slugs]
        current_app.logger.debug(f"🎯 PUBLISH: Unresolved variables in use: {unresolved_in_use}")
        if unresolved_in_use:
            current_app.logger.debug(f"🎯 PUBLISH: Blocking new publication - unresolved variables detected")
            # Get detailed variable information for the frontend
            from ..models import Variable
            variables_info = []
            for var_slug in unresolved_in_use:
                var = Variable.query.filter_by(slug=var_slug).first()
                if var:
                    variables_info.append({
                        'id': var.id,
                        'slug': var.slug,
                        'name': var.name,
                        'description': var.description,
                        'values': [{'id': v.id, 'value': v.value, 'is_default': v.is_default} for v in var.values]
                    })
            
            return jsonify({
                'error': 'Variables must be configured before publishing.',
                'requires_variable_selection': True,
                'unresolved_variables': unresolved_in_use,
                'variables_info': variables_info,
                'publish_setup_endpoint': f'/api/variables/collections/{collection.id}/publish-setup',
                'collection_id': collection.id,
                'message': f'This collection contains {len(unresolved_in_use)} variable(s) that need to be configured before publishing.'
            }), 400
        current_app.logger.debug(f"🎯 PUBLISH: Creating new publication object")
        publication = Publication(
            title=f"{collection.name}",
            description=collection.description or f"Published from Collection '{collection.name}' containing {len(collection.topics)} topics",
            form_number=collection.form_number
        )
        db.session.add(publication)
        db.session.flush()
        current_app.logger.debug(f"🎯 PUBLISH: Created publication {publication.id} titled '{publication.title}'")

        def build_nodes(coll, parent_pub_node_id=None):
            current_app.logger.debug(f"🎯 PUBLISH: Building nodes for collection '{coll.name}'")
            nodes_created = []
            hierarchical_topics = coll.to_tree()
            current_app.logger.debug(f"🎯 PUBLISH: Collection tree has {len(hierarchical_topics)} top-level topics")

            def recurse(topics, parent_node_id):
                for idx, topic_data in enumerate(topics):
                    current_app.logger.debug(f"🎯 PUBLISH: Processing topic {topic_data['id']} at position {idx}")
                    topic_obj = Topic.query.get(topic_data['id'])
                    if not topic_obj:
                        current_app.logger.debug(f"🎯 PUBLISH: WARNING - Topic {topic_data['id']} not found in database")
                        continue
                    title_sub = substitute_variables_in_text(getattr(topic_obj, 'title', '') or '', var_mapping) if topic_obj else ''
                    content_sub = substitute_variables_in_text(getattr(topic_obj, 'content', '') or '', var_mapping) if topic_obj else ''
                    node = PublicationNode(
                        publication_id=publication.id,
                        topic_id=topic_data['id'],
                        parent_id=parent_node_id,
                        position=idx,
                        title_snapshot=title_sub,
                        content_snapshot=content_sub
                    )
                    db.session.add(node)
                    db.session.flush()
                    nodes_created.append(node)
                    current_app.logger.debug(f"🎯 PUBLISH: Created node {node.id} for topic {topic_data['id']}")
                    if topic_data.get('children'):
                        recurse(topic_data['children'], node.id)

            recurse(hierarchical_topics, parent_pub_node_id)
            current_app.logger.debug(f"🎯 PUBLISH: Processing {len(coll.children)} child collections")
            for child_coll in sorted(coll.children, key=lambda x: x.position):
                child_nodes = build_nodes(child_coll, parent_pub_node_id)
                nodes_created.extend(child_nodes)
            return nodes_created

        current_app.logger.debug(f"🎯 PUBLISH: Starting node build for new publication")
        nodes = build_nodes(collection)
        current_app.logger.debug(f"🎯 PUBLISH: Committing {len(nodes)} nodes to database")
        db.session.commit()
        current_app.logger.debug(f"🎯 PUBLISH: Successfully created new publication {publication.id}")
        return jsonify({
            'message': 'Collection published successfully',
            'publication_id': publication.id,
            'nodes_created': len(nodes),
            'redirect_url': f'/publications/{publication.id}',
            'variable_mapping_used': var_mapping,
            'unresolved_variables': []
        }), 201
    except Exception as e:
        current_app.logger.debug(f"🎯 PUBLISH: ERROR - Exception during publish: {str(e)}")
        current_app.logger.debug(f"🎯 PUBLISH: ERROR - Exception type: {type(e).__name__}")
        import traceback
        current_app.logger.debug(f"🎯 PUBLISH: ERROR - Traceback: {traceback.format_exc()}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@collections_bp.route('/<int:collection_id>', methods=['DELETE'])
@jwt_required()
def delete_collection(collection_id):
    """Delete a collection (and its nested children) by ID.

    This performs a hard delete. Because the SQLAlchemy relationship on
    Collection.children uses cascade='all, delete-orphan', child collections
    will be deleted automatically. The association table entries in
    collection_topic_tree use ON DELETE CASCADE (if supported by the DB) so
    topic associations are removed. Topics themselves are NOT deleted; they
    simply become un-associated from this collection hierarchy.

    Returns JSON: { message: str, deleted_id: int }
    """
    try:
        collection = Collection.query.get_or_404(collection_id)

        # Safeguard: prevent hard delete if published (has a publication with same title)
        existing_pub = Publication.query.filter_by(title=collection.name).first()
        if existing_pub:
            return jsonify({'error': 'Collection is published. Archive it first or unpublish to delete.'}), 400

        db.session.delete(collection)
        db.session.commit()
        log_audit('delete', 'collection', collection_id)
        return jsonify({'message': 'Collection deleted', 'deleted_id': collection_id}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@collections_bp.route('/<int:collection_id>/archive', methods=['POST'])
@jwt_required()
def archive_collection(collection_id):
    """Soft archive (toggle) a collection.
    Request body (optional): {"archived": true|false}
    Returns updated collection object.
    """
    try:
        collection = Collection.query.get_or_404(collection_id)
        data = request.get_json(silent=True) or {}
        target_state = data.get('archived')
        if target_state is None:
            # toggle
            collection.archived = not collection.archived
        else:
            collection.archived = bool(target_state)
        db.session.commit()
        return jsonify({'message': 'Collection archive state updated', 'collection': collection.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@collections_bp.route('/<int:collection_id>/variables/check', methods=['GET'])
@jwt_required()
def check_collection_variables(collection_id):
    """
    Check what variables need to be configured before publishing this collection.
    Returns variable information to help users configure them.
    """
    try:
        collection = Collection.query.get_or_404(collection_id)
        var_mapping, unresolved = build_variable_mapping_for_collection(collection.id)
        
        if not unresolved:
            return jsonify({
                'ready_to_publish': True,
                'message': 'All variables are configured. Ready to publish!',
                'variables_configured': len(var_mapping)
            }), 200
        
        # Get detailed variable information for unresolved variables
        from ..models import Variable
        variables_info = []
        for var_slug in unresolved:
            var = Variable.query.filter_by(slug=var_slug).first()
            if var:
                variables_info.append({
                    'id': var.id,
                    'slug': var.slug,
                    'name': var.name,
                    'description': var.description,
                    'values': [{'id': v.id, 'value': v.value, 'is_default': v.is_default} for v in var.values]
                })
        
        return jsonify({
            'ready_to_publish': False,
            'unresolved_variables': unresolved,
            'variables_info': variables_info,
            'collection_id': collection.id,
            'message': f'Please configure {len(unresolved)} variable(s) before publishing.',
            'variables_endpoint': f'/api/variables/collections/{collection.id}/selections',
            'publish_setup_endpoint': f'/api/variables/collections/{collection.id}/publish-setup',
            'configure_endpoint': f'/api/variables/collections/{collection.id}/configure-for-publish'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@collections_bp.route('/<int:collection_id>/prepare-publish', methods=['GET'])
@jwt_required()
def prepare_collection_for_publish(collection_id):
    """
    Comprehensive endpoint to prepare a collection for publishing.
    Returns variable configuration status and collection preview.
    """
    try:
        collection = Collection.query.get_or_404(collection_id)
        
        # Get variable mapping status
        var_mapping, unresolved = build_variable_mapping_for_collection(collection.id)
        
        # Get topics with their hierarchical structure
        topics_tree = collection.to_tree()
        
        # If there are unresolved variables, get their details
        variables_info = []
        if unresolved:
            from ..models import Variable
            for var_slug in unresolved:
                var = Variable.query.filter_by(slug=var_slug).first()
                if var:
                    variables_info.append({
                        'id': var.id,
                        'slug': var.slug,
                        'name': var.name,
                        'description': var.description,
                        'values': [{'id': v.id, 'value': v.value, 'is_default': v.is_default} for v in var.values]
                    })
        
        return jsonify({
            'collection': {
                'id': collection.id,
                'name': collection.name,
                'description': collection.description,
                'topics_count': len(collection.topics)
            },
            'publishing_status': {
                'ready_to_publish': len(unresolved) == 0,
                'variables_configured': len(var_mapping),
                'variables_needed': len(unresolved),
                'unresolved_variables': unresolved
            },
            'variables_info': variables_info,
            'topics_preview': topics_tree,
            'actions': {
                'configure_variables': f'/api/variables/collections/{collection.id}/configure-for-publish',
                'publish': f'/api/collections/{collection.id}/publish',
                'preview_with_variables': f'/api/variables/collections/{collection.id}/preview'
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500