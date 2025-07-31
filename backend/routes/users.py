from flask import Blueprint, request, jsonify
from backend.models import db, User
from sqlalchemy.exc import IntegrityError

users_bp = Blueprint('users', __name__, url_prefix='/api/users')

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
    """Create a new user"""
    print("🔄 Create user POST request received")
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({"error": "Name is required"}), 400
        if not data.get('email'):
            return jsonify({"error": "Email is required"}), 400
        
        # Create new user
        user = User(
            name=data['name'].strip(),
            email=data['email'].strip().lower(),
            role=data.get('role', 'author'),
            active=data.get('active', True)
        )
        
        db.session.add(user)
        db.session.commit()
        
        print(f"✅ Created user: {user.name} ({user.email})")
        return jsonify(user.to_dict()), 201
        
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
