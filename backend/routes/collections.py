from flask import Blueprint, request, jsonify
from datetime import datetime, timezone, timedelta
from ..models import db, Collection, Topic, collection_topic_tree, Project, Publication, PublicationNode, build_variable_mapping_for_collection, substitute_variables_in_text

collections_bp = Blueprint('collections', __name__, url_prefix='/api/collections')

@collections_bp.route('', methods=['GET'])
@collections_bp.route('/', methods=['GET'])
def list_collections():
    print(f"🔄 Collections GET request received")
    try:
        roots = Collection.query.filter_by(parent_id=None)\
                  .order_by(Collection.position).all()
        tree = [c.to_dict() for c in roots]
        print(f"✅ Returning {len(tree)} collections")
        return jsonify(tree), 200
    except Exception as e:
        print(f"❌ Error in list_collections: {e}")
        return jsonify({"error": str(e)}), 500

@collections_bp.route('/stats', methods=['GET'])
def get_collections_stats():
    """Get statistics for collections dashboard"""
    try:
        # Get all collections (including children)
        all_collections = Collection.query.all()
        root_collections = Collection.query.filter_by(parent_id=None).all()
        
        total_collections = len(all_collections)
        # Since Collection doesn't have status field, assume all are active
        active_collections = total_collections
        
        # Calculate total topics across all collections
        total_topics = sum(len(c.topics) for c in all_collections)

        # Calculate new collections created within the last 7 days (inclusive)
        # Use naive UTC datetimes to match model columns (no timezone=True)
        now = datetime.utcnow()
        one_week_ago = now - timedelta(days=7)
        new_this_week = 0
        for c in all_collections:
            created = getattr(c, 'created_at', None)
            if created and created >= one_week_ago:
                new_this_week += 1
        
        # Calculate average topics per collection
        avg_topics = round(total_topics / total_collections) if total_collections > 0 else 0
        
        stats = {
            'total': total_collections,
            'active': active_collections,
            'totalTopics': total_topics,
            'newThisWeek': new_this_week,
            'avgTopics': avg_topics,
            'rootCollections': len(root_collections),
            'debug': {
                'all_collections_count': len(all_collections),
                'root_collections_count': len(root_collections),
                'topics_per_collection': [(c.name, len(c.topics)) for c in all_collections]
            }
        }
        
        print(f"📊 Collections stats: {stats}")
        return jsonify(stats), 200
        
    except Exception as e:
        print(f"❌ Error calculating collections stats: {e}")
        return jsonify({"error": str(e)}), 500

@collections_bp.route('', methods=['PUT'])
@collections_bp.route('/', methods=['PUT'])
def update_collections():
    """
    Expect payload: an array of nested nodes:
    [
      { id, parentId, position, children:[ ... ], topics: [...] },
      …
    ]
    """
    payload = request.get_json()
    print(f"🔄 Updating collections with payload: {payload}")

    def walk(nodes):
      for node in nodes:
        col = Collection.query.get(node['id'])
        if not col:
            print(f"⚠️ Collection {node['id']} not found, skipping")
            continue
        
        # Update collection properties
        col.parent_id = node.get('parentId')
        col.position  = node.get('position', 0)
        
        # Handle topics assignment
        if 'topics' in node:
            print(f"📋 Updating topics for collection {col.id}: {node['topics']}")
            
            # Clear existing relationships for this collection
            db.session.execute(
                collection_topic_tree.delete().where(
                    collection_topic_tree.c.collection_id == col.id
                )
            )
            
            # Add new relationships with hierarchical support
            def add_topics_recursively(topics, parent_topic_id=None, collection=col):
                for idx, t in enumerate(topics):
                    print(f"➕ Adding topic {t['id']} to collection {collection.id} at position {idx}, parent: {parent_topic_id}")
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
        print("✅ Collections updated successfully")
        return jsonify({'message': 'collection tree updated'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error updating collections: {e}")
        return jsonify({'error': str(e)}), 500

@collections_bp.route('', methods=['POST'])
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
    return jsonify(new_collection.to_dict()), 201

@collections_bp.route('/<int:collection_id>', methods=['PUT'])
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
        return jsonify(collection.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@collections_bp.route('/<int:collection_id>/publish', methods=['POST'])
def publish_collection(collection_id):
    """
    Convert a collection to a publication for publishing.
    This creates a Publication and PublicationNode structure from the Collection.
    """
    try:
        collection = Collection.query.get_or_404(collection_id)
        title_pattern = collection.name
        existing_pub = Publication.query.filter_by(title=title_pattern).first()

        if existing_pub:
            var_mapping, unresolved = build_variable_mapping_for_collection(collection.id)
            if unresolved:
                # Get detailed variable information for the frontend
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
                    'error': 'Variables must be configured before publishing.',
                    'requires_variable_selection': True,
                    'unresolved_variables': unresolved,
                    'variables_info': variables_info,
                    'collection_id': collection.id,
                    'message': f'This collection contains {len(unresolved)} variable(s) that need to be configured before publishing.'
                }), 400
            existing_pub.description = f"Published from Collection '{collection.name}' containing {len(collection.topics)} topics"
            existing_pub.created_at = datetime.now(timezone.utc)
            PublicationNode.query.filter_by(publication_id=existing_pub.id).delete()

            def rebuild_nodes(coll, parent_pub_node_id=None):
                nodes_created = []
                hierarchical_topics = coll.to_tree()

                def recurse(topics, parent_node_id):
                    for idx, topic_data in enumerate(topics):
                        topic_obj = Topic.query.get(topic_data['id'])
                        title_sub = substitute_variables_in_text(getattr(topic_obj, 'title', '') or '', var_mapping) if topic_obj else ''
                        content_sub = substitute_variables_in_text(getattr(topic_obj, 'content', '') or '', var_mapping) if topic_obj else ''
                        node = PublicationNode(
                            publication_id=existing_pub.id,
                            topic_id=topic_data['id'],
                            parent_id=parent_node_id,
                            position=idx,
                            title_snapshot=title_sub,
                            content_snapshot=content_sub
                        )
                        db.session.add(node)
                        db.session.flush()
                        nodes_created.append(node)
                        if topic_data.get('children'):
                            recurse(topic_data['children'], node.id)

                recurse(hierarchical_topics, parent_pub_node_id)
                for child_coll in sorted(coll.children, key=lambda x: x.position):
                    child_nodes = rebuild_nodes(child_coll, parent_pub_node_id)
                    nodes_created.extend(child_nodes)
                return nodes_created

            nodes = rebuild_nodes(collection)
            db.session.commit()
            return jsonify({
                'message': 'Publication updated with current collection content',
                'publication_id': existing_pub.id,
                'nodes_created': len(nodes),
                'redirect_url': f'/publications/{existing_pub.id}',
                'variable_mapping_used': var_mapping,
                'unresolved_variables': []
            }), 200

        # New publication path
        var_mapping, unresolved = build_variable_mapping_for_collection(collection.id)
        if unresolved:
            # Get detailed variable information for the frontend
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
                'error': 'Variables must be configured before publishing.',
                'requires_variable_selection': True,
                'unresolved_variables': unresolved,
                'variables_info': variables_info,
                'collection_id': collection.id,
                'message': f'This collection contains {len(unresolved)} variable(s) that need to be configured before publishing.'
            }), 400
        publication = Publication(
            title=f"{collection.name}",
            description=f"Published from Collection '{collection.name}' containing {len(collection.topics)} topics"
        )
        db.session.add(publication)
        db.session.flush()

        def build_nodes(coll, parent_pub_node_id=None):
            nodes_created = []
            hierarchical_topics = coll.to_tree()

            def recurse(topics, parent_node_id):
                for idx, topic_data in enumerate(topics):
                    topic_obj = Topic.query.get(topic_data['id'])
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
                    if topic_data.get('children'):
                        recurse(topic_data['children'], node.id)

            recurse(hierarchical_topics, parent_pub_node_id)
            for child_coll in sorted(coll.children, key=lambda x: x.position):
                child_nodes = build_nodes(child_coll, parent_pub_node_id)
                nodes_created.extend(child_nodes)
            return nodes_created

        nodes = build_nodes(collection)
        db.session.commit()
        return jsonify({
            'message': 'Collection published successfully',
            'publication_id': publication.id,
            'nodes_created': len(nodes),
            'redirect_url': f'/publications/{publication.id}',
            'variable_mapping_used': var_mapping,
            'unresolved_variables': []
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@collections_bp.route('/<int:collection_id>', methods=['DELETE'])
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
        return jsonify({'message': 'Collection deleted', 'deleted_id': collection_id}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@collections_bp.route('/<int:collection_id>/archive', methods=['POST'])
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