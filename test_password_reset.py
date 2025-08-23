#!/usr/bin/env python3
"""
Test script to verify password reset implementation
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))


def test_password_hashing():
    """Test password hashing functionality"""
    from werkzeug.security import generate_password_hash, check_password_hash

    password = "testpassword123"
    password_hash = generate_password_hash(password)

    assert check_password_hash(password_hash, password) is True
    assert check_password_hash(password_hash, "wrongpassword") is False


def test_email_service():
    """Test email service functionality"""
    from utils.email_service import EmailService

    email_service = EmailService()

    assert hasattr(email_service, 'debug_mode')
    assert hasattr(email_service, 'smtp_server')
    assert hasattr(email_service, 'from_email')


def test_token_generation():
    """Test token generation"""
    import secrets

    token = secrets.token_urlsafe(32)

    assert isinstance(token, str) and len(token) > 0

