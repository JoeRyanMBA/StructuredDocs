from datetime import datetime
from backend import db

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)  # Null for global notifications
    message = db.Column(db.String(256), nullable=False)
    link = db.Column(db.String(256), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'message': self.message,
            'link': self.link,
            'date': self.date.isoformat() if self.date else None,
            'read': self.read
        }
