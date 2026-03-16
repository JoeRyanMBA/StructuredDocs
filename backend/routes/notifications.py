from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, Notification, User

notifications_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')

@notifications_bp.route('', methods=['GET'])
@jwt_required()
def get_notifications():
    include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
    query = Notification.query
    if not include_inactive:
        query = query.filter_by(is_active=True)
    notifications = query.order_by(Notification.date.desc()).all()
    return jsonify([n.to_dict() for n in notifications])

@notifications_bp.route('', methods=['POST'])
@jwt_required()
def create_notification():
    data = request.json
    title = data.get('title')
    message = data.get('message')
    link = data.get('link')
    type_ = data.get('type')
    user_id = data.get('user_id')  # Optional, None for global
    notification = Notification(
        title=title,
        message=message,
        link=link,
        type=type_,
        user_id=user_id,
        is_active=data.get('is_active', True),
        target_audience=data.get('target_audience'),
    )
    db.session.add(notification)
    db.session.commit()
    return jsonify(notification.to_dict()), 201

@notifications_bp.route('/<int:notification_id>', methods=['PATCH'])
@jwt_required()
def mark_notification_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    notification.read = True
    db.session.commit()
    return jsonify(notification.to_dict())

@notifications_bp.route('/<int:notification_id>', methods=['GET'])
@jwt_required()
def get_notification(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    return jsonify(notification.to_dict())

@notifications_bp.route('/<int:notification_id>', methods=['PUT'])
@jwt_required()
def update_notification(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    data = request.json or {}
    # Update allowed fields
    if 'title' in data:
        notification.title = data['title']
    if 'message' in data:
        notification.message = data['message']
    if 'link' in data:
        notification.link = data['link']
    if 'type' in data:
        notification.type = data['type']
    if 'read' in data:
        notification.read = bool(data['read'])
    if 'is_active' in data:
        notification.is_active = bool(data['is_active'])
    if 'target_audience' in data:
        notification.target_audience = data['target_audience']
    db.session.commit()
    return jsonify(notification.to_dict())

@notifications_bp.route('/<int:notification_id>/toggle', methods=['POST'])
@jwt_required()
def toggle_notification(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    notification.is_active = not notification.is_active
    db.session.commit()
    return jsonify(notification.to_dict())

@notifications_bp.route('/<int:notification_id>', methods=['DELETE'])
@jwt_required()
def delete_notification(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    db.session.delete(notification)
    db.session.commit()
    return jsonify({'deleted': True})

# Register this blueprint in your main app (usually in app.py)
# from backend.routes.notifications import notifications_bp
# app.register_blueprint(notifications_bp)
