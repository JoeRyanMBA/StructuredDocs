"""
Project management routes for StructuredDocs
Handles projects, stakeholders, milestones, and project-based reviews
"""

from datetime import datetime, date
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import joinedload
from sqlalchemy import desc

# Will import these from updated models.py once integrated
# from models import db, Project, ProjectStakeholder, ProjectMilestone, TopicReview, Topic

projects_bp = Blueprint('projects', __name__, url_prefix='/api/projects')

@projects_bp.route('/', methods=['GET'])
def list_projects():
    """Get all projects with basic info"""
    try:
        # projects = Project.query.order_by(desc(Project.updated_at)).all()
        # return jsonify([project.to_dict() for project in projects])
        
        # Placeholder response for now
        return jsonify([
            {
                "id": 1,
                "name": "Census 2030 Survey Methodology",
                "description": "Development of survey methodology for 2030 Census",
                "status": "active",
                "start_date": "2025-01-15",
                "target_completion": "2025-12-31",
                "stakeholders_count": 8,
                "collections_count": 3,
                "active_reviews_count": 2
            },
            {
                "id": 2,
                "name": "Labor Statistics Modernization",
                "description": "Updating labor force survey methodologies",
                "status": "planning",
                "start_date": "2025-03-01",
                "target_completion": "2026-06-30",
                "stakeholders_count": 5,
                "collections_count": 2,
                "active_reviews_count": 0
            }
        ])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@projects_bp.route('/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """Get detailed project information"""
    try:
        # project = Project.query.options(
        #     joinedload(Project.stakeholders),
        #     joinedload(Project.milestones),
        #     joinedload(Project.reviews)
        # ).get_or_404(project_id)
        # return jsonify(project.to_dict(include_details=True))
        
        # Placeholder response
        if project_id == 1:
            return jsonify({
                "id": 1,
                "name": "Census 2030 Survey Methodology",
                "description": "Development of comprehensive survey methodology for the 2030 Census, including sampling techniques, data collection protocols, and quality assurance procedures.",
                "status": "active",
                "start_date": "2025-01-15",
                "target_completion": "2025-12-31",
                "created_at": "2025-01-15T09:00:00",
                "updated_at": "2025-07-25T14:30:00",
                "stakeholders": [
                    {
                        "id": 1,
                        "name": "Dr. Sarah Johnson",
                        "email": "sarah.johnson@census.gov",
                        "role": "project_manager",
                        "can_review": True,
                        "notes": "Lead project manager, final approval authority"
                    },
                    {
                        "id": 2,
                        "name": "Prof. Michael Chen",
                        "email": "michael.chen@statistics.gov",
                        "role": "subject_matter_expert",
                        "can_review": True,
                        "notes": "Sampling methodology expert"
                    },
                    {
                        "id": 3,
                        "name": "Dr. Amanda Rodriguez",
                        "email": "amanda.rodriguez@census.gov",
                        "role": "reviewer",
                        "can_review": True,
                        "notes": "Quality assurance specialist"
                    }
                ],
                "milestones": [
                    {
                        "id": 1,
                        "title": "Sampling Framework Design",
                        "description": "Complete design of sampling framework and methodology",
                        "due_date": "2025-08-15",
                        "status": "in_progress"
                    },
                    {
                        "id": 2,
                        "title": "Data Collection Protocols",
                        "description": "Finalize data collection protocols and training materials",
                        "due_date": "2025-10-01",
                        "status": "pending"
                    },
                    {
                        "id": 3,
                        "title": "Final Documentation",
                        "description": "Complete all methodology documentation",
                        "due_date": "2025-12-15",
                        "status": "pending"
                    }
                ],
                "collections_count": 3,
                "active_reviews_count": 2
            })
        else:
            return jsonify({"error": "Project not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@projects_bp.route('/', methods=['POST'])
def create_project():
    """Create a new project"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({"error": "Project name is required"}), 400
        
        # project = Project(
        #     name=data['name'],
        #     description=data.get('description'),
        #     status=data.get('status', 'planning'),
        #     start_date=datetime.fromisoformat(data['start_date']).date() if data.get('start_date') else None,
        #     target_completion=datetime.fromisoformat(data['target_completion']).date() if data.get('target_completion') else None
        # )
        # 
        # db.session.add(project)
        # db.session.commit()
        # 
        # return jsonify(project.to_dict()), 201
        
        # Placeholder response
        return jsonify({
            "id": 999,
            "name": data['name'],
            "description": data.get('description'),
            "status": data.get('status', 'planning'),
            "start_date": data.get('start_date'),
            "target_completion": data.get('target_completion'),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@projects_bp.route('/<int:project_id>/stakeholders', methods=['GET'])
def get_project_stakeholders(project_id):
    """Get all stakeholders for a project"""
    try:
        # stakeholders = ProjectStakeholder.query.filter_by(project_id=project_id).all()
        # return jsonify([stakeholder.to_dict() for stakeholder in stakeholders])
        
        # Placeholder - return stakeholders who can review
        if project_id == 1:
            return jsonify([
                {
                    "id": 1,
                    "name": "Dr. Sarah Johnson",
                    "email": "sarah.johnson@census.gov",
                    "role": "project_manager",
                    "can_review": True
                },
                {
                    "id": 2,
                    "name": "Prof. Michael Chen", 
                    "email": "michael.chen@statistics.gov",
                    "role": "subject_matter_expert",
                    "can_review": True
                },
                {
                    "id": 3,
                    "name": "Dr. Amanda Rodriguez",
                    "email": "amanda.rodriguez@census.gov", 
                    "role": "reviewer",
                    "can_review": True
                },
                {
                    "id": 4,
                    "name": "Jennifer Kim",
                    "email": "jennifer.kim@census.gov",
                    "role": "stakeholder",
                    "can_review": False
                }
            ])
        else:
            return jsonify([])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@projects_bp.route('/<int:project_id>/stakeholders', methods=['POST'])
def add_project_stakeholder(project_id):
    """Add a stakeholder to a project"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"{field} is required"}), 400
        
        # stakeholder = ProjectStakeholder(
        #     project_id=project_id,
        #     name=data['name'],
        #     email=data['email'],
        #     role=data['role'],
        #     can_review=data.get('can_review', True),
        #     notes=data.get('notes')
        # )
        # 
        # db.session.add(stakeholder)
        # db.session.commit()
        # 
        # return jsonify(stakeholder.to_dict()), 201
        
        # Placeholder response
        return jsonify({
            "id": 999,
            "project_id": project_id,
            "name": data['name'],
            "email": data['email'],
            "role": data['role'],
            "can_review": data.get('can_review', True),
            "notes": data.get('notes'),
            "created_at": datetime.utcnow().isoformat()
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@projects_bp.route('/<int:project_id>/reviews', methods=['GET'])
def get_project_reviews(project_id):
    """Get all reviews for a project"""
    try:
        # reviews = TopicReview.query.filter_by(project_id=project_id)\
        #     .options(joinedload(TopicReview.topic), joinedload(TopicReview.assigned_stakeholder))\
        #     .order_by(desc(TopicReview.submitted_at)).all()
        # return jsonify([review.to_dict() for review in reviews])
        
        # Placeholder response
        if project_id == 1:
            return jsonify([
                {
                    "id": 1,
                    "topic": {
                        "id": 1,
                        "title": "Random Sampling Methodology for Large Scale Surveys"
                    },
                    "assigned_stakeholder": {
                        "id": 2,
                        "name": "Prof. Michael Chen",
                        "role": "subject_matter_expert"
                    },
                    "status": "pending",
                    "due_date": "2025-08-01",
                    "submitted_at": "2025-07-25T10:00:00",
                    "submitter_notes": "Please review the sampling methodology section for technical accuracy."
                },
                {
                    "id": 2,
                    "topic": {
                        "id": 3,
                        "title": "Statistical Disclosure Control in Census Publications"
                    },
                    "assigned_stakeholder": {
                        "id": 3,
                        "name": "Dr. Amanda Rodriguez",
                        "role": "reviewer"
                    },
                    "status": "in_review",
                    "due_date": "2025-07-30",
                    "submitted_at": "2025-07-22T14:30:00",
                    "submitter_notes": "Need review of privacy protection methods."
                }
            ])
        else:
            return jsonify([])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@projects_bp.route('/<int:project_id>/reviews', methods=['POST'])
def submit_topic_for_project_review(project_id):
    """Submit a topic for review within a project context"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['topic_id', 'assigned_stakeholder_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"{field} is required"}), 400
        
        # review = TopicReview(
        #     project_id=project_id,
        #     topic_id=data['topic_id'],
        #     assigned_stakeholder_id=data['assigned_stakeholder_id'],
        #     due_date=datetime.fromisoformat(data['due_date']).date() if data.get('due_date') else None,
        #     submitter_notes=data.get('submitter_notes')
        # )
        # 
        # db.session.add(review)
        # db.session.commit()
        # 
        # return jsonify(review.to_dict()), 201
        
        # Placeholder response
        return jsonify({
            "id": 999,
            "project_id": project_id,
            "topic_id": data['topic_id'],
            "assigned_stakeholder_id": data['assigned_stakeholder_id'],
            "status": "pending",
            "due_date": data.get('due_date'),
            "submitted_at": datetime.utcnow().isoformat(),
            "submitter_notes": data.get('submitter_notes')
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
