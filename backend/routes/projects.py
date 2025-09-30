"""
Project management routes for StructuredDocs
Handles projects, stakeholders, milestones, and project-based reviews
"""

from datetime import datetime, date
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import joinedload
from sqlalchemy import desc
from ..models import db, Project, Stakeholder, ProjectStakeholder, Collection, Topic, User

projects_bp = Blueprint('projects', __name__, url_prefix='/api/projects')

@projects_bp.route('/<int:project_id>/archive', methods=['POST'])
@jwt_required()
def archive_project(project_id):
    """Toggle a project's archived state (admin only). Body: {"archived": true|false}"""
    try:
        data = request.get_json(silent=True) or {}
        if 'archived' not in data:
            return jsonify({'error': 'Missing archived field'}), 400
        desired = bool(data.get('archived'))

        user_id = get_jwt_identity()
        try:
            user_pk = int(user_id)
        except Exception:
            user_pk = None
        user = User.query.get(user_pk) if user_pk else None
        if not user:
            return jsonify({'error': 'User not found or session expired'}), 401
        is_admin = False
        try:
            if getattr(user, 'is_admin', False):
                is_admin = True
            elif getattr(user, 'role', '').lower() in ('admin', 'superadmin'):
                is_admin = True
        except Exception:
            pass
        if not is_admin:
            return jsonify({'error': 'Admin role required'}), 403

        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404

        prev = bool(getattr(project, 'archived', False))
        project.archived = desired
        db.session.commit()
        # Structured log (using print to stay consistent with existing logging approach)
        try:
            print(f"[PROJECT_ARCHIVE] user_id={user_pk} project_id={project.id} previous_archived={prev} new_archived={project.archived} timestamp={datetime.utcnow().isoformat()}Z")
        except Exception:
            pass
        return jsonify({'project': project.to_dict(), 'previous_archived': prev}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    """Update a project's basic info"""
    try:
        data = request.get_json()
        project = Project.query.get_or_404(project_id)
        if 'name' in data:
            project.name = data['name']
        if 'description' in data:
            project.description = data['description']
        if 'status' in data:
            project.status = data['status']
        if 'start_date' in data:
            project.start_date = data['start_date']
        if 'target_completion' in data:
            project.target_completion = data['target_completion']
        db.session.commit()
        return jsonify(project.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/', methods=['GET'])
def list_projects():
    """Get all projects with basic info"""
    import traceback
    try:
        projects = Project.query.order_by(desc(Project.updated_at)).all()
        return jsonify([project.to_dict() for project in projects])
    except Exception as e:
        print('Error in /api/projects:', e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@projects_bp.route('/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """Get detailed project information"""
    try:
        project = Project.query.options(
            joinedload(Project.stakeholders).joinedload(ProjectStakeholder.stakeholder),
            joinedload(Project.milestones),
            joinedload(Project.collections)
        ).get_or_404(project_id)
        return jsonify(project.to_dict(include_details=True))
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
        project = Project(
            name=data['name'],
            description=data.get('description'),
            status=data.get('status', 'planning'),
            start_date=datetime.fromisoformat(data['start_date']).date() if data.get('start_date') else None,
            target_completion=datetime.fromisoformat(data['target_completion']).date() if data.get('target_completion') else None
        )
        db.session.add(project)
        db.session.commit()
        return jsonify(project.to_dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@projects_bp.route('/<int:project_id>/stakeholders', methods=['GET'])
def get_project_stakeholders(project_id):
    """Get all stakeholders for a project"""
    from sqlalchemy.orm import joinedload
    try:
        # Get all project stakeholders with their stakeholder details
        project_stakeholders = ProjectStakeholder.query.filter_by(project_id=project_id).options(joinedload(ProjectStakeholder.stakeholder)).all()
        
        result = []
        for ps in project_stakeholders:
            result.append({
                "id": ps.stakeholder.id,
                "name": ps.stakeholder.name,
                "email": ps.stakeholder.email,
                "title": ps.stakeholder.title,
                "organization": ps.stakeholder.organization,
                "role": ps.role,
                "can_review": ps.can_review,
                "notes": ps.notes,
                "project_stakeholder_id": ps.id,
                "created_at": ps.created_at.isoformat() if ps.created_at else None
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@projects_bp.route('/<int:project_id>/stakeholders', methods=['POST'])
def add_project_stakeholder(project_id):
    """Add a stakeholder to a project"""
    try:
        data = request.get_json()
        
        # Verify project exists
        project = Project.query.get_or_404(project_id)
        
        # Support adding by stakeholder_id (existing) or by name/email/role (new)
        if data.get('stakeholder_id'):
            # Add existing stakeholder to project
            stakeholder_id = data['stakeholder_id']
            stakeholder = Stakeholder.query.get_or_404(stakeholder_id)
            
            # Check if stakeholder is already associated with this project
            existing_association = ProjectStakeholder.query.filter_by(
                project_id=project_id, 
                stakeholder_id=stakeholder_id
            ).first()
            
            if existing_association:
                return jsonify({"error": "Stakeholder is already associated with this project"}), 400
            
            # Create new project-stakeholder association
            project_stakeholder = ProjectStakeholder(
                project_id=project_id,
                stakeholder_id=stakeholder_id,
                role=data.get('role', 'stakeholder'),
                can_review=data.get('can_review', True),
                notes=data.get('notes')
            )
            
            db.session.add(project_stakeholder)
            db.session.commit()
            
            return jsonify({
                "id": project_stakeholder.id,
                "project_id": project_id,
                "stakeholder_id": stakeholder_id,
                "name": stakeholder.name,
                "email": stakeholder.email,
                "role": project_stakeholder.role,
                "can_review": project_stakeholder.can_review,
                "notes": project_stakeholder.notes,
                "created_at": project_stakeholder.created_at.isoformat(),
                "existing": True
            }), 201
        else:
            # Create new stakeholder and add to project
            required_fields = ['name', 'email', 'role']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({"error": f"{field} is required"}), 400
            
            # Check if stakeholder with this email already exists
            existing_stakeholder = Stakeholder.query.filter_by(email=data['email']).first()
            if existing_stakeholder:
                # Use existing stakeholder
                stakeholder = existing_stakeholder
            else:
                # Create new stakeholder
                stakeholder = Stakeholder(
                    name=data['name'],
                    email=data['email'],
                    title=data.get('title'),
                    organization=data.get('organization'),
                    role=data.get('role', 'stakeholder')
                )
                db.session.add(stakeholder)
                db.session.flush()  # Get the ID
            
            # Create project-stakeholder association
            project_stakeholder = ProjectStakeholder(
                project_id=project_id,
                stakeholder_id=stakeholder.id,
                role=data.get('role', 'stakeholder'),
                can_review=data.get('can_review', True),
                notes=data.get('notes')
            )
            
            db.session.add(project_stakeholder)
            db.session.commit()
            
            return jsonify({
                "id": project_stakeholder.id,
                "project_id": project_id,
                "stakeholder_id": stakeholder.id,
                "name": stakeholder.name,
                "email": stakeholder.email,
                "role": project_stakeholder.role,
                "can_review": project_stakeholder.can_review,
                "notes": project_stakeholder.notes,
                "created_at": project_stakeholder.created_at.isoformat(),
                "existing": False
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
