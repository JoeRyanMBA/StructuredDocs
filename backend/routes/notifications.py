from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend import db
from backend.notifications import Notification
from backend.models import User

notifications_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')

@notifications_bp.route('', methods=['GET'])
@jwt_required()
def get_notifications():
    user_id = get_jwt_identity()
    # Fetch user-specific and global notifications
    notifications = Notification.query.filter(
        (Notification.user_id == user_id) | (Notification.user_id == None)
    ).order_by(Notification.date.desc()).all()
    return jsonify([n.to_dict() for n in notifications])

@notifications_bp.route('', methods=['POST'])
@jwt_required()
def create_notification():
    data = request.json
    message = data.get('message')
    link = data.get('link')
    type_ = data.get('type')
    user_id = data.get('user_id')  # Optional, None for global
    notification = Notification(
        message=message,
        link=link,
        type=type_,
        user_id=user_id
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

# Register this blueprint in your main app (usually in app.py)
# from backend.routes.notifications import notifications_bp
# app.register_blueprint(notifications_bp)
