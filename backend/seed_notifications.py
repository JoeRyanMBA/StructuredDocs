import os
import sys
from datetime import datetime
from backend.models import db, Notification
from backend.app import app

sample_notifications = [
    {
        'title': 'Welcome!',
        'message': 'Welcome to StructuredDocs! Your account was created.',
        'type': 'global',
        'read': False
    },
    {
        'title': 'Milestone Due',
        'message': 'Project Alpha has a new milestone due next week.',
        'type': 'admin',
        'read': False
    },
    {
        'title': 'Review Pending',
        'message': 'Your review for Topic Beta is pending.',
        'type': 'author',
        'read': False
    },
    {
        'title': 'System Update',
        'message': 'System maintenance completed successfully.',
        'type': 'global',
        'read': True
    },
    {
        'title': 'New Feature',
        'message': 'Check out the new document collaboration feature!',
        'type': 'global',
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
