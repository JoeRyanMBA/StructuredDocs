from flask import Blueprint, request, jsonify, current_app
from ..models import db, User, PasswordResetToken
from ..extensions import limiter
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from ..utils.email_service import email_service
import secrets
import os
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app, make_response
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity,
    set_access_cookies, set_refresh_cookies, unset_jwt_cookies,
)
from sqlalchemy import func

users_bp = Blueprint('users', __name__, url_prefix='/api/users')

VALID_ROLES = {'author', 'reviewer', 'admin'}


def _require_admin():
    """Return (user, None) when the caller is an authenticated admin.
    Return (None, error_response) when authentication or authorization fails.
    """
    uid = get_jwt_identity()
    try:
        uid = int(uid)
    except (TypeError, ValueError):
        pass
    user = User.query.get(uid) if uid is not None else None
    if not user or user.role != 'admin':
        return None, (jsonify({'error': 'Admin access required'}), 403)
    return user, None

@users_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json() or {}
        # Normalize input to avoid case/whitespace mismatches
        credential = (data.get('email') or data.get('username') or '').strip().lower()
        password = data.get('password', None)

        current_app.logger.debug(f" Login attempt for: {credential}")
        # Lookup by email if contains '@', otherwise by username
        if '@' in credential:
            user = User.query.filter(func.lower(User.email) == credential).first()
        else:
            user = User.query.filter(func.lower(User.name) == credential).first()

        current_app.logger.debug(f" User found: {user is not None}")

        # Fail fast if no user, no password provided, or no password hash set
        if (not user) or (not isinstance(password, str) or password == '') or (not user.password_hash):
            current_app.logger.debug("❌ No user or no password hash")
            return jsonify({"msg": "Bad email or password"}), 401

        try:
            if check_password_hash(user.password_hash, password):
                # Use string identity to avoid 422 "Subject must be a string" issues in some environments
                access_token = create_access_token(identity=str(user.id))
                refresh_token = create_refresh_token(identity=str(user.id))
                current_app.logger.debug("✅ Login successful")
                resp = make_response(jsonify(access_token=access_token, refresh_token=refresh_token, user=user.to_dict()))
                # Also set HttpOnly cookies so token is not accessible to JS
                set_access_cookies(resp, access_token)
                set_refresh_cookies(resp, refresh_token)
                return resp
        except Exception as e:
            # Avoid 500s on malformed hashes; treat as invalid credentials
            current_app.logger.error(f" Password check error: {e}")
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        current_app.logger.error(f"LOGIN ERROR: {type(e).__name__}: {e}\n{tb}")
        return jsonify({"error": "Internal server error", "detail": str(e)}), 500

    current_app.logger.debug("❌ Invalid credentials")
    return jsonify({"msg": "Bad email or password"}), 401

@users_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    user_id = get_jwt_identity()
    try:
        user_pk = int(user_id) if user_id is not None else None
    except (TypeError, ValueError):
        user_pk = None
    user = User.query.get(user_pk) if user_pk is not None else None
    if user:
        return jsonify(user.to_dict()), 200
    return jsonify({"msg": "User not found"}), 404


@users_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    """Issue a new short-lived access token using a valid refresh token."""
    identity = get_jwt_identity()
    new_access = create_access_token(identity=identity)
    resp = make_response(jsonify(access_token=new_access))
    set_access_cookies(resp, new_access)
    return resp, 200


@users_bp.route('/logout', methods=['POST'])
def logout():
    """Clear JWT HttpOnly cookies on logout."""
    resp = make_response(jsonify({'message': 'Logged out'}))
    unset_jwt_cookies(resp)
    return resp, 200

@users_bp.route('', methods=['GET'])
@users_bp.route('/', methods=['GET'])
@jwt_required()
def list_users():
    """Get all users. Supports ?page=&limit=&role=&active="""
    try:
        caller, err = _require_admin()
        if err:
            return err

        page = max(1, request.args.get('page', 1, type=int))
        limit = min(200, max(1, request.args.get('limit', 100, type=int)))
        role_filter = request.args.get('role')
        active_filter = request.args.get('active')

        q = User.query
        if role_filter:
            q = q.filter(User.role == role_filter)
        if active_filter is not None:
            q = q.filter(User.active == (active_filter.lower() in ('1', 'true', 'yes')))
        q = q.order_by(User.name)

        total = q.count()
        users = q.offset((page - 1) * limit).limit(limit).all()
        current_app.logger.info(f"list_users: returning {len(users)} of {total}")
        return jsonify({
            'users': [u.to_dict() for u in users],
            'total': total,
            'page': page,
            'limit': limit,
            'pages': max(1, (total + limit - 1) // limit),
        }), 200
    except Exception as e:
        current_app.logger.exception("Failed to list users")
        return jsonify({"error": "Failed to list users"}), 500

@users_bp.route('', methods=['POST'])
@users_bp.route('/', methods=['POST'])
@jwt_required()
def create_user():
    """Create a new user and send password setup email (admin only)"""
    current_app.logger.debug("🔄 Create user POST request received")
    try:
        caller, err = _require_admin()
        if err:
            return err

        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({"error": "Name is required"}), 400
        if not data.get('email'):
            return jsonify({"error": "Email is required"}), 400

        requested_role = data.get('role', 'author')
        if requested_role not in VALID_ROLES:
            return jsonify({"error": f"Invalid role. Must be one of: {', '.join(sorted(VALID_ROLES))}"}), 400

        # Check if password is provided (for direct creation) or if we should send setup email
        send_setup_email = not data.get('password')
        
        # Create new user
        user = User(
            name=data['name'].strip(),
            email=data['email'].strip().lower(),
            role=requested_role,
            active=data.get('active', True)
        )
        
        # If password is provided, hash it directly
        if data.get('password'):
            user.password_hash = generate_password_hash(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        current_app.logger.info(f" Created user: {user.name} ({user.email})")
        
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
                    current_app.logger.info(f" Password setup email sent to {user.email}")
                    message = f"User created successfully. Password setup email sent to {user.email}"
                else:
                    current_app.logger.warning(f" Failed to send password setup email to {user.email}")
                    message = "User created successfully, but failed to send password setup email. Please contact the user directly."
                
            except Exception as email_error:
                current_app.logger.error(f" Error sending password setup email: {email_error}")
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
        current_app.logger.error(f" Error creating user: {e}")
        return jsonify({"error": str(e)}), 500

@users_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Update an existing user (admin only)"""
    current_app.logger.debug(f" Update user {user_id} PUT request received")
    try:
        caller, err = _require_admin()
        if err:
            return err

        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # Update fields if provided
        if 'name' in data:
            user.name = data['name'].strip()
        if 'email' in data:
            user.email = data['email'].strip().lower()
        if 'role' in data:
            if data['role'] not in VALID_ROLES:
                return jsonify({"error": f"Invalid role. Must be one of: {', '.join(sorted(VALID_ROLES))}"}), 400
            user.role = data['role']
        if 'active' in data:
            user.active = data['active']
        
        db.session.commit()
        
        current_app.logger.info(f" Updated user: {user.name} ({user.email})")
        return jsonify(user.to_dict()), 200
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Email already exists"}), 409
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f" Error updating user: {e}")
        return jsonify({"error": str(e)}), 500

@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """Delete a user (admin only)"""
    current_app.logger.debug(f" Delete user {user_id} DELETE request received")
    try:
        caller, err = _require_admin()
        if err:
            return err

        user = User.query.get_or_404(user_id)
        
        # Don't allow deleting the last admin
        if user.role == 'admin':
            admin_count = User.query.filter_by(role='admin', active=True).count()
            if admin_count <= 1:
                return jsonify({"error": "Cannot delete the last admin user"}), 409
        
        db.session.delete(user)
        db.session.commit()
        
        current_app.logger.info(f" Deleted user: {user.name} ({user.email})")
        return jsonify({"message": "User deleted successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f" Error deleting user: {e}")
        return jsonify({"error": str(e)}), 500

@users_bp.route('/<int:user_id>/role', methods=['PUT'])
@jwt_required()
def update_user_role(user_id):
    """Update a user's role (admin only)"""
    current_app.logger.debug(f" Update user {user_id} role PUT request received")
    try:
        caller, err = _require_admin()
        if err:
            return err

        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        if not data.get('role'):
            return jsonify({"error": "Role is required"}), 400

        new_role = data['role']
        if new_role not in VALID_ROLES:
            return jsonify({"error": f"Invalid role. Must be one of: {', '.join(sorted(VALID_ROLES))}"}), 400
        
        # Don't allow removing admin role from the last admin
        old_role = user.role
        if old_role == 'admin' and new_role != 'admin':
            admin_count = User.query.filter_by(role='admin', active=True).count()
            if admin_count <= 1:
                return jsonify({"error": "Cannot remove admin role from the last admin user"}), 409
        
        user.role = new_role
        db.session.commit()
        
        current_app.logger.info(f" Updated user role: {user.name} from {old_role} to {new_role}")
        return jsonify(user.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f" Error updating user role: {e}")
        return jsonify({"error": str(e)}), 500


@users_bp.route('/request-password-reset', methods=['POST'])
@limiter.limit("5 per hour")
def request_password_reset():
    """Request a password reset email"""
    current_app.logger.debug("🔄 Password reset request received")
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
            current_app.logger.info(f" Password reset email sent to {user.email}")
        else:
            current_app.logger.warning(f" Failed to send password reset email to {user.email}")
        
        # Always return success message for security
        return jsonify({"message": "If an account with that email exists, a password reset link has been sent."}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f" Error processing password reset request: {e}")
        return jsonify({"error": "Failed to process password reset request"}), 500


@users_bp.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    """Reset password using token"""
    current_app.logger.debug(f" Password reset with token: {token[:10]}...")
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
        
        current_app.logger.info(f" Password reset successful for user: {user.email}")
        
        return jsonify({
            "message": "Password reset successful. You can now log in with your new password.",
            "token_type": reset_token.token_type
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f" Error resetting password: {e}")
        return jsonify({"error": "Failed to reset password"}), 500


@users_bp.route('/validate-reset-token/<token>', methods=['GET'])
def validate_reset_token(token):
    """Validate a password reset token without using it"""
    current_app.logger.debug(f" Validating reset token: {token[:10]}...")
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
                "expires_at": reset_token.expires_at.isoformat()
            }), 200
        else:
            return jsonify({"valid": False, "error": error_message}), 400
        
    except Exception as e:
        current_app.logger.error(f" Error validating reset token: {e}")
        return jsonify({"valid": False, "error": "Failed to validate token"}), 500


@users_bp.route('/<int:user_id>/resend-setup-email', methods=['POST'])
@jwt_required()
def resend_setup_email(user_id):
    """Resend password setup email for a user (admin only)"""
    current_app.logger.debug(f" Resending setup email for user {user_id}")
    try:
        caller, err = _require_admin()
        if err:
            return err

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
            current_app.logger.info(f" Setup email resent to {user.email}")
            return jsonify({"message": f"Password setup email sent to {user.email}"}), 200
        else:
            # Surface non-secret last_error for diagnostics
            last_err = getattr(email_service, 'last_error', None)
            current_app.logger.warning(f" Failed to resend setup email to {user.email}; last_error={last_err}")
            detail = last_err or "Email delivery failed. Check SMTP credentials and provider settings."
            return jsonify({"error": "Failed to send setup email", "detail": detail}), 502
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f" Error resending setup email: {e}")
        return jsonify({"error": str(e)}), 500
