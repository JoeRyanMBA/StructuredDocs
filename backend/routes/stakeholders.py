"""
Stakeholder management routes for StructuredDocs
Handles CRUD operations for stakeholders
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy.orm import joinedload
from sqlalchemy import desc
import json
from ..models import db, Stakeholder, Project, ProjectStakeholder

stakeholders_bp = Blueprint('stakeholders', __name__, url_prefix='/api/stakeholders')

def parse_expertise_areas(expertise_data):
    """Helper function to parse expertise areas from various input formats"""
    if isinstance(expertise_data, str):
        # If it's a string, assume it's newline-separated areas
        return [area.strip() for area in expertise_data.split('\n') if area.strip()]
    elif isinstance(expertise_data, list):
        return expertise_data
    else:
        return []

@stakeholders_bp.route('/', methods=['GET'])
@jwt_required()
def list_stakeholders():
    """Get all stakeholders"""
    try:
        stakeholders = Stakeholder.query.order_by(Stakeholder.name).all()
        return jsonify([s.to_dict() for s in stakeholders])
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@stakeholders_bp.route('/', methods=['POST'])
@jwt_required()
def create_stakeholder():
    """Create a new stakeholder"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Check if stakeholder already exists
        existing = Stakeholder.query.filter_by(email=data['email']).first()
        if existing:
            return jsonify({"error": "Stakeholder with this email already exists"}), 409

        # Create new stakeholder
        stakeholder = Stakeholder(
            name=data['name'],
            email=data['email'],
            title=data.get('title'),
            organization=data.get('organization'),
            division=data.get('division'),
            department=data.get('department'),
            phone=data.get('phone'),
            expertise_areas=json.dumps(data.get('expertise_areas', [])),
            bio=data.get('bio'),
            active=data.get('active', True)
        )
        db.session.add(stakeholder)
        db.session.commit()
        return jsonify(stakeholder.to_dict()), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@stakeholders_bp.route('/<int:stakeholder_id>', methods=['GET'])
@jwt_required()
def get_stakeholder(stakeholder_id):
    """Get a specific stakeholder"""
    try:
        # stakeholder = Stakeholder.query.get_or_404(stakeholder_id)
        # return jsonify(stakeholder.to_dict())
        
        # Placeholder response
        return jsonify({
            "id": stakeholder_id,
            "name": "Dr. Sarah Johnson",
            "email": "sarah.johnson@census.gov",
            "title": "Senior Project Manager",
            "organization": "U.S. Census Bureau",
            "department": "Data Collection Operations",
            "phone": "(301) 555-0101",
            "expertise_areas": ["Project Management", "Data Collection", "Survey Design"],
            "bio": "15+ years experience managing large-scale census and survey operations.",
            "active": True,
            "created_at": "2025-01-15T10:00:00",
            "updated_at": "2025-07-25T14:30:00"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@stakeholders_bp.route('/<int:stakeholder_id>', methods=['PUT'])
@jwt_required()
def update_stakeholder(stakeholder_id):
    """Update a stakeholder"""
    try:
        stakeholder = Stakeholder.query.get_or_404(stakeholder_id)
        data = request.get_json()
        
        # Validate required fields if they're provided
        if 'email' in data:
            existing = Stakeholder.query.filter(
                Stakeholder.email == data['email'],
                Stakeholder.id != stakeholder_id
            ).first()
            if existing:
                return jsonify({"error": "Another stakeholder with this email already exists"}), 409
        
        # Update fields
        stakeholder.name = data.get('name', stakeholder.name)
        stakeholder.email = data.get('email', stakeholder.email)
        stakeholder.title = data.get('title', stakeholder.title)
        stakeholder.organization = data.get('organization', stakeholder.organization)
        stakeholder.division = data.get('division', stakeholder.division)
        stakeholder.department = data.get('department', stakeholder.department)
        stakeholder.phone = data.get('phone', stakeholder.phone)
        stakeholder.bio = data.get('bio', stakeholder.bio)
        stakeholder.active = data.get('active', stakeholder.active)
        
        if 'expertise_areas' in data:
            parsed_expertise = parse_expertise_areas(data['expertise_areas'])
            if parsed_expertise is not None:
                stakeholder.expertise_areas = json.dumps(parsed_expertise)
        
        db.session.commit()
        return jsonify(stakeholder.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@stakeholders_bp.route('/<int:stakeholder_id>', methods=['DELETE'])
@jwt_required()
def delete_stakeholder(stakeholder_id):
    """Deactivate a stakeholder (soft delete)"""
    try:
        stakeholder = Stakeholder.query.get_or_404(stakeholder_id)
        stakeholder.active = False
        db.session.commit()
        return jsonify({"message": "Stakeholder deactivated successfully"})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@stakeholders_bp.route('/search', methods=['GET'])
@jwt_required()
def search_stakeholders():
    """Search stakeholders by various criteria"""
    try:
        search_term = request.args.get('q', '').strip()
        expertise = request.args.get('expertise', '').strip()
        organization = request.args.get('organization', '').strip()
        
        # query = Stakeholder.query.filter(Stakeholder.active == True)
        
        # if search_term:
        #     query = query.filter(
        #         db.or_(
        #             Stakeholder.name.ilike(f'%{search_term}%'),
        #             Stakeholder.email.ilike(f'%{search_term}%'),
        #             Stakeholder.title.ilike(f'%{search_term}%')
        #         )
        #     )
        
        # if expertise:
        #     query = query.filter(Stakeholder.expertise_areas.ilike(f'%{expertise}%'))
        
        # if organization:
        #     query = query.filter(Stakeholder.organization.ilike(f'%{organization}%'))
        
        # stakeholders = query.order_by(Stakeholder.name).limit(20).all()
        # return jsonify([s.to_dict() for s in stakeholders])
        
        # Placeholder response
        return jsonify([
            {
                "id": 1,
                "name": "Dr. Sarah Johnson",
                "email": "sarah.johnson@census.gov",
                "title": "Senior Project Manager",
                "organization": "U.S. Census Bureau"
            },
            {
                "id": 2,
                "name": "Prof. Michael Chen",
                "email": "michael.chen@statistics.gov",
                "title": "Chief Statistician",
                "organization": "Bureau of Labor Statistics"
            }
        ])
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
