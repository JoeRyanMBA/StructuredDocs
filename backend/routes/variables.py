from flask import Blueprint, request, jsonify, current_app
from ..models import db, Variable, VariableValue, CollectionVariableSelection, build_variable_mapping_for_collection, substitute_variables_in_text, Collection

variables_bp = Blueprint('variables', __name__, url_prefix='/api/variables')


@variables_bp.route('/validate_slug', methods=['GET'])
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
def list_variables():
    try:
        include_values = request.args.get('include_values', '1') == '1'
        vars_ = Variable.query.order_by(Variable.created_at.desc()).all()
        return jsonify([v.to_dict(include_values=include_values) for v in vars_]), 200
    except Exception as e:
        current_app.logger.exception('Failed to list variables')
        return jsonify({'error': str(e)}), 500


@variables_bp.route('', methods=['POST'])
@variables_bp.route('/', methods=['POST'])
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
