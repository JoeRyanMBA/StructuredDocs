"""
Milestone management routes for StructuredDocs
Handles CRUD operations for project milestones
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import desc
from datetime import datetime, date
import json

# Import models
from ..models import db, ProjectMilestone, Project

milestones_bp = Blueprint('milestones', __name__, url_prefix='/api/milestones')

@milestones_bp.route('/', methods=['GET'])
@milestones_bp.route('', methods=['GET'])
@jwt_required()
def list_milestones():
    """Get all milestones with project information"""
    try:
        milestones = ProjectMilestone.query.join(Project).order_by(ProjectMilestone.date.asc()).all()
        result = []
        for milestone in milestones:
            milestone_dict = milestone.to_dict()
            milestone_dict['project_name'] = milestone.project.name if milestone.project else None
            result.append(milestone_dict)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@milestones_bp.route('/', methods=['POST'])
@milestones_bp.route('', methods=['POST'])
@jwt_required()
def create_milestone():
    """Create a new milestone"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({"error": "Milestone name is required"}), 400
        if not data.get('project_id'):
            return jsonify({"error": "Project ID is required"}), 400
            
        # Verify project exists
        project = Project.query.get(data['project_id'])
        if not project:
            return jsonify({"error": "Project not found"}), 404
            
        # Parse date if provided
        milestone_date = None
        if data.get('date'):
            try:
                milestone_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
                
        milestone = ProjectMilestone(
            project_id=data['project_id'],
            name=data['name'],
            description=data.get('description'),
            date=milestone_date,
            status=data.get('status', 'planned')
        )
        
        db.session.add(milestone)
        db.session.commit()
        
        return jsonify(milestone.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@milestones_bp.route('/<int:milestone_id>', methods=['PUT'])
@jwt_required()
def update_milestone(milestone_id):
    """Update a milestone"""
    try:
        milestone = ProjectMilestone.query.get_or_404(milestone_id)
        data = request.get_json()
        
        # Update fields
        if 'name' in data:
            if not data['name'].strip():
                return jsonify({"error": "Milestone name cannot be empty"}), 400
            milestone.name = data['name'].strip()
            
        if 'description' in data:
            milestone.description = data['description']
            
        if 'date' in data:
            if data['date']:
                try:
                    milestone.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
            else:
                milestone.date = None
                
        if 'status' in data:
            milestone.status = data['status']
            
        if 'project_id' in data:
            # Verify new project exists
            project = Project.query.get(data['project_id'])
            if not project:
                return jsonify({"error": "Project not found"}), 404
            milestone.project_id = data['project_id']
            
        # Set completion date if status is completed
        if data.get('status') == 'completed' and milestone.completion_date is None:
            milestone.completion_date = date.today()
        elif data.get('status') != 'completed':
            milestone.completion_date = None
        
        db.session.commit()
        
        return jsonify(milestone.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@milestones_bp.route('/<int:milestone_id>', methods=['DELETE'])
@jwt_required()
def delete_milestone(milestone_id):
    """Delete a milestone"""
    try:
        milestone = ProjectMilestone.query.get_or_404(milestone_id)
        
        db.session.delete(milestone)
        db.session.commit()
        
        return jsonify({"message": "Milestone deleted successfully"})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@milestones_bp.route('/projects', methods=['GET'])
@jwt_required()
def list_projects():
    """Get list of projects for milestone association"""
    try:
        # Get projects that are not completed or on hold
        projects = Project.query.filter(
            Project.status.in_(['planning', 'active', 'review'])
        ).order_by(Project.name).all()
        return jsonify([{"id": p.id, "name": p.name} for p in projects])
    except Exception as e:
        return jsonify({"error": str(e)}), 500