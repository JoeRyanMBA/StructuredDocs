from flask import Blueprint, request, jsonify
from ..models import db, User, PasswordResetToken
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from ..utils.email_service import email_service
import secrets
import os
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

users_bp = Blueprint('users', __name__, url_prefix='/api/users')

@users_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        # Normalize input to avoid case/whitespace mismatches
        email = (data.get('email') or '').strip().lower()
        password = data.get('password', None)

        print(f"🔐 Login attempt for: {email}")
        
        user = User.query.filter_by(email=email).first()
        print(f"👤 User found: {user is not None}")
        
        # Fail fast if no user or no password set
        if not user or not user.password_hash:
            print("❌ No user or no password hash")
            return jsonify({"msg": "Bad email or password"}), 401

        try:
            if check_password_hash(user.password_hash, password):
                access_token = create_access_token(identity=user.id)
                print("✅ Login successful")
                return jsonify(access_token=access_token, user=user.to_dict())
        except Exception as e:
            # Avoid 500s on malformed hashes; treat as invalid credentials
            print(f"❌ Password check error: {e}")
    except Exception as e:
        print(f"❌ Login error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Internal server error"}), 500
        
    print("❌ Invalid credentials")
    return jsonify({"msg": "Bad email or password"}), 401

@users_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user:
        return jsonify(user.to_dict()), 200
    return jsonify({"msg": "User not found"}), 404

@users_bp.route('', methods=['GET'])
@users_bp.route('/', methods=['GET'])
def list_users():
    """Get all users"""
    print("🔄 Users GET request received")
    try:
        users = User.query.order_by(User.name).all()
        users_data = [user.to_dict() for user in users]
        print(f"✅ Returning {len(users_data)} users")
        return jsonify(users_data), 200
    except Exception as e:
        print(f"❌ Error in list_users: {e}")
        return jsonify({"error": str(e)}), 500

@users_bp.route('', methods=['POST'])
@users_bp.route('/', methods=['POST'])
def create_user():
    """Create a new user and send password setup email"""
    print("🔄 Create user POST request received")
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({"error": "Name is required"}), 400
        if not data.get('email'):
            return jsonify({"error": "Email is required"}), 400
        
        # Check if password is provided (for direct creation) or if we should send setup email
        send_setup_email = not data.get('password')
        
        # Create new user
        user = User(
            name=data['name'].strip(),
            email=data['email'].strip().lower(),
            role=data.get('role', 'author'),
            active=data.get('active', True)
        )
        
        # If password is provided, hash it directly
        if data.get('password'):
            user.password_hash = generate_password_hash(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        print(f"✅ Created user: {user.name} ({user.email})")
        
        # Send password setup email if no password was provided
        if send_setup_email:
            try:
                # Generate password setup token
                token = secrets.token_urlsafe(32)
                setup_token = PasswordResetToken(
                    token=token,
                    user_id=user.id,
                    token_type='setup',
                    expires_at=datetime.now() + timedelta(hours=24),  # 24 hour expiry for setup
                    created_by_admin=True
                )
                
                db.session.add(setup_token)
                db.session.commit()
                
                # Send setup email
                base_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
                setup_url = f"{base_url}/auth/setup-password/{token}"
                
                # Get admin name from session if available (for now, use generic)
                admin_name = "System Administrator"  # Could be enhanced to get actual admin name
                
                email_sent = email_service.send_password_setup_email(
                    user_email=user.email,
                    user_name=user.name,
                    setup_url=setup_url,
                    created_by_admin=True,
                    admin_name=admin_name
                )
                
                if email_sent:
                    print(f"✅ Password setup email sent to {user.email}")
                    message = f"User created successfully. Password setup email sent to {user.email}"
                else:
                    print(f"⚠️ Failed to send password setup email to {user.email}")
                    message = "User created successfully, but failed to send password setup email. Please contact the user directly."
                
            except Exception as email_error:
                print(f"❌ Error sending password setup email: {email_error}")
                message = "User created successfully, but failed to send password setup email. Please contact the user directly."
        else:
            message = "User created successfully with provided password."
        
        response_data = user.to_dict()
        response_data['message'] = message
        response_data['password_setup_required'] = send_setup_email
        
        return jsonify(response_data), 201
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Email already exists"}), 409
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creating user: {e}")
        return jsonify({"error": str(e)}), 500

@users_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update an existing user"""
    print(f"🔄 Update user {user_id} PUT request received")
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # Update fields if provided
        if 'name' in data:
            user.name = data['name'].strip()
        if 'email' in data:
            user.email = data['email'].strip().lower()
        if 'role' in data:
            user.role = data['role']
        if 'active' in data:
            user.active = data['active']
        
        db.session.commit()
        
        print(f"✅ Updated user: {user.name} ({user.email})")
        return jsonify(user.to_dict()), 200
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Email already exists"}), 409
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error updating user: {e}")
        return jsonify({"error": str(e)}), 500

@users_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user"""
    print(f"🔄 Delete user {user_id} DELETE request received")
    try:
        user = User.query.get_or_404(user_id)
        
        # Don't allow deleting the last admin
        if user.role == 'admin':
            admin_count = User.query.filter_by(role='admin', active=True).count()
            if admin_count <= 1:
                return jsonify({"error": "Cannot delete the last admin user"}), 409
        
        db.session.delete(user)
        db.session.commit()
        
        print(f"✅ Deleted user: {user.name} ({user.email})")
        return jsonify({"message": "User deleted successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error deleting user: {e}")
        return jsonify({"error": str(e)}), 500

@users_bp.route('/<int:user_id>/role', methods=['PUT'])
def update_user_role(user_id):
    """Update a user's role"""
    print(f"🔄 Update user {user_id} role PUT request received")
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        if not data.get('role'):
            return jsonify({"error": "Role is required"}), 400
        
        old_role = user.role
        new_role = data['role']
        
        # Don't allow removing admin role from the last admin
        if old_role == 'admin' and new_role != 'admin':
            admin_count = User.query.filter_by(role='admin', active=True).count()
            if admin_count <= 1:
                return jsonify({"error": "Cannot remove admin role from the last admin user"}), 409
        
        user.role = new_role
        db.session.commit()
        
        print(f"✅ Updated user role: {user.name} from {old_role} to {new_role}")
        return jsonify(user.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error updating user role: {e}")
        return jsonify({"error": str(e)}), 500


@users_bp.route('/request-password-reset', methods=['POST'])
def request_password_reset():
    """Request a password reset email"""
    print("🔄 Password reset request received")
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({"error": "Email is required"}), 400
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # For security, don't reveal if email exists or not
            return jsonify({"message": "If an account with that email exists, a password reset link has been sent."}), 200
        
        # Deactivate any existing reset tokens for this user
        existing_tokens = PasswordResetToken.query.filter_by(
            user_id=user.id, 
            is_active=True
        ).all()
        
        for token in existing_tokens:
            token.is_active = False
        
        # Generate new reset token
        token = secrets.token_urlsafe(32)
        reset_token = PasswordResetToken(
            token=token,
            user_id=user.id,
            token_type='reset',
            expires_at=datetime.now() + timedelta(hours=1),  # 1 hour expiry for reset
            created_by_admin=False
        )
        
        db.session.add(reset_token)
        db.session.commit()
        
        # Send reset email
        base_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
        reset_url = f"{base_url}/auth/reset-password/{token}"
        
        email_sent = email_service.send_password_reset_email(
            user_email=user.email,
            user_name=user.name,
            reset_url=reset_url
        )
        
        if email_sent:
            print(f"✅ Password reset email sent to {user.email}")
        else:
            print(f"⚠️ Failed to send password reset email to {user.email}")
        
        # Always return success message for security
        return jsonify({"message": "If an account with that email exists, a password reset link has been sent."}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error processing password reset request: {e}")
        return jsonify({"error": "Failed to process password reset request"}), 500


@users_bp.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    """Reset password using token"""
    print(f"🔄 Password reset with token: {token[:10]}...")
    try:
        data = request.get_json()
        new_password = data.get('password')
        
        if not new_password:
            return jsonify({"error": "Password is required"}), 400
        
        if len(new_password) < 8:
            return jsonify({"error": "Password must be at least 8 characters long"}), 400
        
        # Find and validate token
        reset_token = PasswordResetToken.query.filter_by(token=token).first()
        
        if not reset_token:
            return jsonify({"error": "Invalid or expired token"}), 400
        
        # Check if token is valid
        is_valid, error_message = reset_token.is_valid()
        if not is_valid:
            return jsonify({"error": error_message}), 400
        
        # Get user
        user = User.query.get(reset_token.user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Update password
        user.password_hash = generate_password_hash(new_password)
        
        # Mark token as used
        reset_token.used_at = datetime.now()
        reset_token.is_active = False
        
        db.session.commit()
        
        print(f"✅ Password reset successful for user: {user.email}")
        
        return jsonify({
            "message": "Password reset successful. You can now log in with your new password.",
            "token_type": reset_token.token_type
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error resetting password: {e}")
        return jsonify({"error": "Failed to reset password"}), 500


@users_bp.route('/validate-reset-token/<token>', methods=['GET'])
def validate_reset_token(token):
    """Validate a password reset token without using it"""
    print(f"🔄 Validating reset token: {token[:10]}...")
    try:
        # Find token
        reset_token = PasswordResetToken.query.filter_by(token=token).first()
        
        if not reset_token:
            return jsonify({"valid": False, "error": "Invalid token"}), 404
        
        # Check if token is valid
        is_valid, error_message = reset_token.is_valid()
        
        if is_valid:
            user = User.query.get(reset_token.user_id)
            return jsonify({
                "valid": True,
                "token_type": reset_token.token_type,
                "user_name": user.name if user else None,
                "user_email": user.email if user else None,
                "expires_at": reset_token.expires_at.isoformat()
            }), 200
        else:
            return jsonify({"valid": False, "error": error_message}), 400
        
    except Exception as e:
        print(f"❌ Error validating reset token: {e}")
        return jsonify({"valid": False, "error": "Failed to validate token"}), 500


@users_bp.route('/<int:user_id>/resend-setup-email', methods=['POST'])
def resend_setup_email(user_id):
    """Resend password setup email for a user"""
    print(f"🔄 Resending setup email for user {user_id}")
    try:
        user = User.query.get_or_404(user_id)
        
        # Check if user already has a password
        if user.password_hash:
            return jsonify({"error": "User already has a password set. Use password reset instead."}), 400
        
        # Deactivate any existing setup tokens for this user
        existing_tokens = PasswordResetToken.query.filter_by(
            user_id=user.id,
            token_type='setup',
            is_active=True
        ).all()
        
        for token in existing_tokens:
            token.is_active = False
        
        # Generate new setup token
        token = secrets.token_urlsafe(32)
        setup_token = PasswordResetToken(
            token=token,
            user_id=user.id,
            token_type='setup',
            expires_at=datetime.now() + timedelta(hours=24),  # 24 hour expiry
            created_by_admin=True
        )
        
        db.session.add(setup_token)
        db.session.commit()
        
        # Send setup email
        base_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
        setup_url = f"{base_url}/auth/setup-password/{token}"
        
        admin_name = "System Administrator"  # Could be enhanced to get actual admin name
        
        email_sent = email_service.send_password_setup_email(
            user_email=user.email,
            user_name=user.name,
            setup_url=setup_url,
            created_by_admin=True,
            admin_name=admin_name
        )
        
        if email_sent:
            print(f"✅ Setup email resent to {user.email}")
            return jsonify({"message": f"Password setup email sent to {user.email}"}), 200
        else:
            print(f"⚠️ Failed to resend setup email to {user.email}")
            return jsonify({"error": "Failed to send setup email"}), 500
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error resending setup email: {e}")
        return jsonify({"error": str(e)}), 500
