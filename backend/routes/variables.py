from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from ..models import db, Variable, VariableValue, CollectionVariableSelection, build_variable_mapping_for_collection, substitute_variables_in_text, Collection
from ..utils.settings import get_setting
import json

variables_bp = Blueprint('variables', __name__, url_prefix='/api/variables')


@variables_bp.route('/validate_slug', methods=['GET'])
@jwt_required()
def validate_slug():
    """Validate a proposed slug; returns normalized slug, availability, and auto-incremented suggestion."""
    import re
    raw = request.args.get('slug', '')
    original = raw
    # Normalize like frontend
    s = raw.lower()
    s = re.sub(r'\s+', '_', s)
    s = re.sub(r'[^a-z0-9_\-]', '', s)
    s = re.sub(r'^-+', '', s)
    s = re.sub(r'^[^a-z]+', '', s)  # must start with a letter
    if not s:
        return jsonify({'slug': '', 'available': False, 'suggested': ''}), 200
    base = s
    counter = 2
    available = True
    while Variable.query.filter_by(slug=s).first():
        available = False
        s = f"{base}-{counter}"
        counter += 1
    return jsonify({'slug': base, 'available': available, 'suggested': s if not available else base, 'original': original}), 200


@variables_bp.route('', methods=['GET'])
@variables_bp.route('/', methods=['GET'])
@jwt_required()
def list_variables():
    try:
        include_values = request.args.get('include_values', '1') == '1'
        vars_ = Variable.query.order_by(Variable.created_at.desc()).all()
        return jsonify([v.to_dict(include_values=include_values) for v in vars_]), 200
    except Exception as e:
        msg = str(e).lower()
        if 'no such table' in msg and 'variables' in msg:
            current_app.logger.warning('variables table missing; attempting create_all fallback')
            try:
                db.create_all()
                vars_ = Variable.query.order_by(Variable.created_at.desc()).all()
                return jsonify([v.to_dict(include_values=True) for v in vars_]), 200
            except Exception:
                current_app.logger.exception('Fallback create_all failed')
        current_app.logger.exception('Failed to list variables')
        return jsonify({'error': 'list_variables_failed', 'detail': str(e)}), 500


@variables_bp.route('', methods=['POST'])
@variables_bp.route('/', methods=['POST'])
@jwt_required()
def create_variable():
    data = request.get_json() or {}
    try:
        name = data.get('name') or 'Untitled'
        slug = data.get('slug') or name.lower().replace(' ', '_')
        description = data.get('description')
        scope = data.get('scope', 'global')
        # Basic slug normalization
        import re
        slug = re.sub(r'[^a-zA-Z0-9_\-]', '_', slug)
        # Auto-increment slug if collision: slug, slug-2, slug-3 ...
        base_slug = slug
        counter = 2
        while Variable.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        # Instantiate then assign attributes to satisfy static analysis (Pylance) that doesn't know dynamic constructor kwargs
        variable = Variable()
        variable.name = name  # type: ignore[attr-defined]
        variable.slug = slug  # type: ignore[attr-defined]
        variable.description = description  # type: ignore[attr-defined]
        variable.scope = scope  # type: ignore[attr-defined]
        db.session.add(variable)
        db.session.commit()
        return jsonify(variable.to_dict(include_values=True)), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception('Failed to create variable')
        return jsonify({'error': str(e)}), 500


@variables_bp.route('/<int:var_id>', methods=['PUT'])
@jwt_required()
def update_variable(var_id):
    variable = Variable.query.get(var_id)
    if not variable:
        return jsonify({'error': 'Variable not found'}), 404
    data = request.get_json() or {}
    try:
        if 'name' in data:
            variable.name = data['name']
        if 'description' in data:
            variable.description = data['description']
    # Slug changes disabled (immutability enforced); ignore if provided
        db.session.commit()
        return jsonify(variable.to_dict(include_values=True)), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception('Failed to update variable')
        return jsonify({'error': str(e)}), 500


@variables_bp.route('/<int:var_id>', methods=['DELETE'])
@jwt_required()
def delete_variable(var_id):
    variable = Variable.query.get(var_id)
    if not variable:
        return jsonify({'error': 'Variable not found'}), 404
    try:
        db.session.delete(variable)
        db.session.commit()
        return jsonify({'deleted': True}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception('Failed to delete variable')
        return jsonify({'error': str(e)}), 500


# ----- Variable Values -----
@variables_bp.route('/<int:var_id>/values', methods=['POST'])
@jwt_required()
def add_variable_value(var_id):
    variable = Variable.query.get(var_id)
    if not variable:
        return jsonify({'error': 'Variable not found'}), 404
    data = request.get_json() or {}
    try:
        value = data.get('value')
        if not value:
            return jsonify({'error': 'value required'}), 400
        is_default = bool(data.get('is_default'))
        if is_default:
            # Clear existing defaults
            for v in variable.values:
                if v.is_default:
                    v.is_default = False
        vv = VariableValue()
        vv.variable_id = variable.id  # type: ignore[attr-defined]
        vv.value = value  # type: ignore[attr-defined]
        vv.is_default = is_default  # type: ignore[attr-defined]
        db.session.add(vv)
        db.session.commit()
        return jsonify(vv.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception('Failed to add variable value')
        return jsonify({'error': str(e)}), 500


@variables_bp.route('/values/<int:value_id>', methods=['PUT'])
@jwt_required()
def update_variable_value(value_id):
    vv = VariableValue.query.get(value_id)
    if not vv:
        return jsonify({'error': 'Value not found'}), 404
    data = request.get_json() or {}
    try:
        if 'value' in data:
            vv.value = data['value']
        if 'is_default' in data:
            new_default = bool(data['is_default'])
            if new_default and not vv.is_default:
                # Clear other defaults
                others = VariableValue.query.filter(VariableValue.variable_id == vv.variable_id, VariableValue.id != vv.id, VariableValue.is_default == True).all()
                for o in others:
                    o.is_default = False
            vv.is_default = new_default
        db.session.commit()
        return jsonify(vv.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception('Failed to update variable value')
        return jsonify({'error': str(e)}), 500


@variables_bp.route('/values/<int:value_id>', methods=['DELETE'])
@jwt_required()
def delete_variable_value(value_id):
    vv = VariableValue.query.get(value_id)
    if not vv:
        return jsonify({'error': 'Value not found'}), 404
    try:
        db.session.delete(vv)
        db.session.commit()
        return jsonify({'deleted': True}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception('Failed to delete variable value')
        return jsonify({'error': str(e)}), 500


# ----- Collection Selections -----
@variables_bp.route('/collections/<int:collection_id>/selections', methods=['GET'])
@jwt_required()
def get_collection_variable_selections(collection_id):
    collection = Collection.query.get(collection_id)
    if not collection:
        return jsonify({'error': 'Collection not found'}), 404
    try:
        selections = CollectionVariableSelection.query.filter_by(collection_id=collection_id).all()
        selection_map = {s.variable_id: s.variable_value_id for s in selections}
        variables = Variable.query.all()
        return jsonify({
            'variables': [v.to_dict(include_values=True, selection_map=selection_map) for v in variables],
            'selections': [s.to_dict() for s in selections]
        }), 200
    except Exception as e:
        current_app.logger.exception('Failed to get selections')
        return jsonify({'error': str(e)}), 500


@variables_bp.route('/collections/<int:collection_id>/selections', methods=['POST', 'PUT'])
@jwt_required()
def upsert_collection_variable_selections(collection_id):
    collection = Collection.query.get(collection_id)
    if not collection:
        return jsonify({'error': 'Collection not found'}), 404
    payload = request.get_json() or {}
    selections = payload.get('selections', [])
    try:
        for sel in selections:
            var_id = sel.get('variable_id')
            value_id = sel.get('variable_value_id')
            if not var_id:
                continue
            row = CollectionVariableSelection.query.filter_by(collection_id=collection_id, variable_id=var_id).first()
            if not row:
                row = CollectionVariableSelection()
                row.collection_id = collection_id  # type: ignore[attr-defined]
                row.variable_id = var_id  # type: ignore[attr-defined]
                db.session.add(row)
            row.variable_value_id = value_id
        db.session.commit()
        return jsonify({'updated': True}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception('Failed to upsert selections')
        return jsonify({'error': str(e)}), 500


# ----- Utility / Preview -----
@variables_bp.route('/collections/<int:collection_id>/preview', methods=['POST'])
@jwt_required()
def preview_collection_with_variables(collection_id):
    """Return topics content with variable substitution applied for a preview selection map (not persisted)."""
    collection = Collection.query.get(collection_id)
    if not collection:
        return jsonify({'error': 'Collection not found'}), 404
    data = request.get_json() or {}
    temp_map = data.get('map', {})  # { slug: value }
    # Build base mapping from stored selections/defaults
    stored_map, _ = build_variable_mapping_for_collection(collection_id)
    # Overlay temp map
    final_map = {**stored_map, **temp_map}
    topic_payload = []
    for t in collection.topics:
        substituted = substitute_variables_in_text(t.content or '', final_map)
        topic_payload.append({'id': t.id, 'title': t.title, 'content': substituted})
    return jsonify({'topics': topic_payload, 'mapping': final_map}), 200


@variables_bp.route('/collections/<int:collection_id>/publish-setup', methods=['GET'])
@jwt_required()
def get_collection_publish_setup(collection_id):
    """
    Get comprehensive variable setup information for publishing a collection.
    Returns all variables that need to be configured, their current selections,
    and available options.
    """
    collection = Collection.query.get(collection_id)
    if not collection:
        return jsonify({'error': 'Collection not found'}), 404
    
    try:
        # Get current variable mapping and unresolved variables
        var_mapping, unresolved = build_variable_mapping_for_collection(collection_id)

        # Get all variables and their current selections
        selections = CollectionVariableSelection.query.filter_by(collection_id=collection_id).all()
        selection_map = {s.variable_id: s.variable_value_id for s in selections}

        # Get all variables that appear in collection content
        all_variables = Variable.query.all()
        variables_in_content = []

        # Check the complete collection subtree, matching the publish traversal.
        collection_topics = []

        def gather_collection_topics(current_collection):
            collection_topics.extend(current_collection.topics)
            for child_collection in current_collection.children:
                gather_collection_topics(child_collection)

        gather_collection_topics(collection)

        # Check which variables are actually used in this collection's content
        for var in all_variables:
            variable_pattern = f"{{{{{var.slug}}}}}"
            found_in_content = False

            # Check in topic titles and content
            for topic in collection_topics:
                if (variable_pattern in (topic.title or '') or
                    variable_pattern in (topic.content or '')):
                    found_in_content = True
                    break

            # Branding-only variables may not appear in topic text. Include them
            # when one of their allowed values is mapped to an export template.
            if not found_in_content:
                try:
                    templates = json.loads(get_setting('export_branding_templates', '[]') or '[]')
                except (TypeError, ValueError):
                    templates = []
                mapped_values = {
                    template.get('variable_value')
                    for template in templates
                    if isinstance(template, dict) and template.get('variable_value')
                }
                found_in_content = any(value.value in mapped_values for value in var.values)

            if found_in_content:
                current_selection = selection_map.get(var.id)
                current_value = None
                if current_selection:
                    value_obj = VariableValue.query.get(current_selection)
                    current_value = value_obj.to_dict() if value_obj else None

                variables_in_content.append({
                    'id': var.id,
                    'slug': var.slug,
                    'name': var.name,
                    'description': var.description,
                    'is_resolved': var.slug not in unresolved,
                    'current_selection': current_value,
                    'values': [v.to_dict() for v in var.values]
                })

        return jsonify({
            'collection_id': collection_id,
            'collection_name': collection.name,
            'ready_to_publish': len(unresolved) == 0,
            'variables_in_content': variables_in_content,
            'unresolved_count': len(unresolved),
            'resolved_count': len(var_mapping),
            'message': f'Collection uses {len(variables_in_content)} variable(s). {len(unresolved)} need configuration.' if unresolved else 'All variables are configured. Ready to publish!'
        }), 200

    except Exception as e:
        current_app.logger.exception('Failed to get publish setup')
        return jsonify({'error': str(e)}), 500


@variables_bp.route('/collections/<int:collection_id>/configure-for-publish', methods=['POST'])
@jwt_required()
def configure_collection_variables_for_publish(collection_id):
    """
    Configure variables for a collection in preparation for publishing.
    Accepts a batch of variable selections and validates them.
    """
    collection = Collection.query.get(collection_id)
    if not collection:
        return jsonify({'error': 'Collection not found'}), 404
    
    payload = request.get_json() or {}
    variable_selections = payload.get('variable_selections', [])
    
    if not variable_selections:
        return jsonify({'error': 'No variable selections provided'}), 400
    
    try:
        # Update all provided variable selections
        updated_count = 0
        for selection in variable_selections:
            var_id = selection.get('variable_id')
            value_id = selection.get('variable_value_id')
            
            if not var_id or not value_id:
                continue
                
            # Verify the variable and value exist
            variable = Variable.query.get(var_id)
            value = VariableValue.query.get(value_id)
            
            if not variable or not value:
                continue
                
            # Create or update selection
            selection_record = CollectionVariableSelection.query.filter_by(
                collection_id=collection_id, 
                variable_id=var_id
            ).first()
            
            if not selection_record:
                selection_record = CollectionVariableSelection()
                selection_record.collection_id = collection_id
                selection_record.variable_id = var_id
                db.session.add(selection_record)
            
            selection_record.variable_value_id = value_id
            updated_count += 1
        
        db.session.commit()
        
        # Check if collection is now ready to publish
        var_mapping, unresolved = build_variable_mapping_for_collection(collection_id)
        
        return jsonify({
            'success': True,
            'updated_variables': updated_count,
            'ready_to_publish': len(unresolved) == 0,
            'remaining_unresolved': unresolved,
            'publish_endpoint': f'/api/collections/{collection_id}/publish',
            'preview_endpoint': f'/api/variables/collections/{collection_id}/preview',
            'message': f'Updated {updated_count} variable(s). ' + 
                      ('Ready to publish!' if len(unresolved) == 0 else f'{len(unresolved)} still need configuration.')
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception('Failed to configure variables for publish')
        return jsonify({'error': str(e)}), 500


@variables_bp.route('/collections/batch-configure', methods=['POST'])
@jwt_required()
def batch_configure_variables_for_collections():
    """Apply the same variable selections to multiple collections.
    Payload: {
        "collection_ids": [int, ...],
        "variable_selections": [ { variable_id, variable_value_id }, ... ]
    }
    Returns per-collection status summary.
    """
    payload = request.get_json() or {}
    collection_ids = payload.get('collection_ids') or []
    variable_selections = payload.get('variable_selections') or []
    if not collection_ids:
        return jsonify({'error': 'No collection_ids provided'}), 400
    if not variable_selections:
        return jsonify({'error': 'No variable_selections provided'}), 400
    summaries = []
    try:
        # Preload variables/values for validation caching
        cache_variables = {v.id: v for v in Variable.query.all()}
        cache_values = {vv.id: vv for vv in VariableValue.query.all()}
        for cid in collection_ids:
            coll = Collection.query.get(cid)
            if not coll:
                summaries.append({'collection_id': cid, 'updated': 0, 'error': 'collection_not_found'})
                continue
            updated_count = 0
            for selection in variable_selections:
                var_id = selection.get('variable_id')
                value_id = selection.get('variable_value_id')
                if not var_id or not value_id:
                    continue
                if var_id not in cache_variables or value_id not in cache_values:
                    continue
                # Upsert
                record = CollectionVariableSelection.query.filter_by(collection_id=cid, variable_id=var_id).first()
                if not record:
                    record = CollectionVariableSelection()
                    record.collection_id = cid  # type: ignore[attr-defined]
                    record.variable_id = var_id  # type: ignore[attr-defined]
                    db.session.add(record)
                record.variable_value_id = value_id
                updated_count += 1
            # After applying, compute readiness
            var_mapping, unresolved = build_variable_mapping_for_collection(cid)
            summaries.append({
                'collection_id': cid,
                'collection_name': coll.name,
                'updated_variables': updated_count,
                'ready_to_publish': len(unresolved) == 0,
                'remaining_unresolved': unresolved
            })
        db.session.commit()
        return jsonify({'success': True, 'collections': summaries}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception('Failed batch variable configure')
        return jsonify({'error': str(e)}), 500
