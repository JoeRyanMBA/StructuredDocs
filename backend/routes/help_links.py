from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, HelpLink, User

help_links_bp = Blueprint('help_links', __name__, url_prefix='/api')


@help_links_bp.route('/help-links', methods=['GET'])
def get_help_links_map():
    """Return all enabled help links as a feature_key → data map. Public — no auth required."""
    try:
        links = HelpLink.query.filter_by(enabled=True).all()
        result = {link.feature_key: link.to_dict() for link in links}
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.exception('Error fetching help links map')
        return jsonify({'error': str(e)}), 500


@help_links_bp.route('/admin/help-links', methods=['GET'])
@jwt_required()
def list_help_links():
    """Return all help links (admin only)."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or getattr(user, 'role', None) != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        links = HelpLink.query.order_by(HelpLink.feature_key).all()
        return jsonify([link.to_dict() for link in links]), 200
    except Exception as e:
        current_app.logger.exception('Error listing help links')
        return jsonify({'error': str(e)}), 500


@help_links_bp.route('/admin/help-links', methods=['POST'])
@jwt_required()
def create_help_link():
    """Create a new help link entry (admin only)."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or getattr(user, 'role', None) != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        data = request.get_json() or {}
        feature_key = (data.get('feature_key') or '').strip()
        title = (data.get('title') or '').strip()

        if not feature_key or not title:
            return jsonify({'error': 'feature_key and title are required'}), 400

        if HelpLink.query.filter_by(feature_key=feature_key).first():
            return jsonify({'error': f"feature_key '{feature_key}' already exists"}), 409

        link = HelpLink(
            feature_key=feature_key,
            title=title,
            description=data.get('description', ''),
            kb_url=data.get('kb_url', ''),
            enabled=data.get('enabled', True),
        )
        db.session.add(link)
        db.session.commit()
        return jsonify(link.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception('Error creating help link')
        return jsonify({'error': str(e)}), 500


@help_links_bp.route('/admin/help-links/<int:link_id>', methods=['PUT'])
@jwt_required()
def update_help_link(link_id):
    """Update an existing help link (admin only)."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or getattr(user, 'role', None) != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        link = HelpLink.query.get_or_404(link_id)
        data = request.get_json() or {}

        if 'feature_key' in data:
            new_key = (data['feature_key'] or '').strip()
            if not new_key:
                return jsonify({'error': 'feature_key cannot be empty'}), 400
            existing = HelpLink.query.filter_by(feature_key=new_key).first()
            if existing and existing.id != link_id:
                return jsonify({'error': f"feature_key '{new_key}' already exists"}), 409
            link.feature_key = new_key

        if 'title' in data:
            title = (data['title'] or '').strip()
            if not title:
                return jsonify({'error': 'title cannot be empty'}), 400
            link.title = title

        if 'description' in data:
            link.description = data['description']
        if 'kb_url' in data:
            link.kb_url = data['kb_url']
        if 'enabled' in data:
            link.enabled = bool(data['enabled'])

        db.session.commit()
        return jsonify(link.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception('Error updating help link')
        return jsonify({'error': str(e)}), 500


@help_links_bp.route('/admin/help-links/<int:link_id>', methods=['DELETE'])
@jwt_required()
def delete_help_link(link_id):
    """Delete a help link (admin only)."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or getattr(user, 'role', None) != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        link = HelpLink.query.get_or_404(link_id)
        db.session.delete(link)
        db.session.commit()
        return jsonify({'message': 'Deleted'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception('Error deleting help link')
        return jsonify({'error': str(e)}), 500
