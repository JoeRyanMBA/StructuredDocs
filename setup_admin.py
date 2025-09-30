#!/usr/bin/env python3
"""
Admin user setup script for StructuredDocs
Creates or resets the admin user password for testing
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app import create_app
from backend.models import db, User
from werkzeug.security import generate_password_hash

def setup_admin_user():
    """Create or update the admin user with known credentials"""
    app = create_app()
    
    with app.app_context():
        # Check if admin user exists
        admin = User.query.filter_by(email='admin@example.com').first()
        
        if not admin:
            print("Creating admin user...")
            admin = User(
                name='Admin User',
                email='admin@example.com',
                role='admin',
                active=True
            )
            db.session.add(admin)
        else:
            print("Admin user exists, updating...")
        
        # Set password to 'admin123'
        admin.password_hash = generate_password_hash('admin123')
        admin.role = 'admin'  # Ensure role is set correctly
        admin.active = True   # Ensure user is active
        
        db.session.commit()
        
        print(f"✅ Admin user setup complete:")
        print(f"   Email: {admin.email}")
        print(f"   Password: admin123")
        print(f"   Role: {admin.role}")
        print(f"   Active: {admin.active}")
        print(f"   ID: {admin.id}")

if __name__ == '__main__':
    setup_admin_user()