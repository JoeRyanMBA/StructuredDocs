import os
import sys
from datetime import datetime
from backend.models import db, Notification
from backend.app import app

sample_notifications = [
    {
        'message': 'Welcome to StructuredDocs! Your account was created.',
        'read': False
    },
    {
        'message': 'Project Alpha has a new milestone due next week.',
        'read': False
    },
    {
        'message': 'Your review for Topic Beta is pending.',
        'read': False
    }
]

def seed_notifications():
    from datetime import datetime
    with app.app_context():
        for notif in sample_notifications:
            n = Notification(**notif)
            # Set created_at if the model has this attribute
            if hasattr(n, 'created_at'):
                n.created_at = datetime.utcnow()
            db.session.add(n)
        db.session.commit()
        print(f"Seeded {len(sample_notifications)} notifications.")

if __name__ == "__main__":
    seed_notifications()
