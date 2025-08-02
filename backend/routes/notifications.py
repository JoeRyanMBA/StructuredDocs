from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from models import Notification
from models import User

notifications_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')

@notifications_bp.route('', methods=['GET'])
def get_notifications():
    # Fetch all notifications (user-specific logic disabled for debugging)
    notifications = Notification.query.order_by(Notification.date.desc()).all()
    return jsonify([n.to_dict() for n in notifications])

@notifications_bp.route('', methods=['POST'])
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
        user_id=user_id
    )
    db.session.add(notification)
    db.session.commit()
    return jsonify(notification.to_dict()), 201

@notifications_bp.route('/<int:notification_id>', methods=['PATCH'])
def mark_notification_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    notification.read = True
    db.session.commit()
    return jsonify(notification.to_dict())

# Register this blueprint in your main app (usually in app.py)
# from backend.routes.notifications import notifications_bp
# app.register_blueprint(notifications_bp)
