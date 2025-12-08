"""
Project management routes for StructuredDocs
Handles projects, stakeholders, milestones, and project-based reviews
"""

from datetime import datetime, date
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import joinedload
from sqlalchemy import desc
from ..models import db, Project, Stakeholder, ProjectStakeholder, Collection, Topic, User

projects_bp = Blueprint('projects', __name__, url_prefix='/api/projects')

@projects_bp.route('/roles', methods=['GET'])
def get_allowed_project_roles():
    """Return allowed roles for Stakeholder and ProjectStakeholder enums.
    Useful for frontend to populate role dropdowns accurately.
    """
    try:
        stakeholder_roles = []
        project_roles = []
        try:
            stakeholder_roles = list(Stakeholder.__table__.c.role.type.enums)
        except Exception:
            stakeholder_roles = ['author', 'reviewer', 'subject_matter_expert', 'stakeholder', 'admin']
        try:
            project_roles = list(ProjectStakeholder.__table__.c.role.type.enums)
        except Exception:
            project_roles = ['project_manager', 'subject_matter_expert', 'reviewer', 'stakeholder', 'sponsor']
        return jsonify({
            'stakeholder_roles': stakeholder_roles,
            'project_roles': project_roles
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
    """Add a stakeholder to a project with validation to avoid 500s."""
    from sqlalchemy.exc import IntegrityError

    try:
        data = request.get_json() or {}
        current_app.logger.info(f"POST /api/projects/{project_id}/stakeholders - Data: {data}")

        # Verify project exists
        project = Project.query.get_or_404(project_id)
        current_app.logger.info(f"Project {project_id} found: {project.name}")

        # Allowed roles — derive directly from SQLAlchemy Enum definitions to avoid DB mismatches
        try:
            stakeholder_role_enums = set(Stakeholder.__table__.c.role.type.enums)
        except Exception:
            stakeholder_role_enums = {'author', 'reviewer', 'subject_matter_expert', 'stakeholder', 'admin'}
        try:
            project_role_enums = set(ProjectStakeholder.__table__.c.role.type.enums)
        except Exception:
            project_role_enums = {'project_manager', 'subject_matter_expert', 'reviewer', 'stakeholder', 'sponsor'}

        # When creating a new stakeholder, accept project roles as well (for Stakeholder.role mapping)
        allowed_creation_roles = stakeholder_role_enums | project_role_enums

        def validate_email(email: str) -> bool:
            try:
                return isinstance(email, str) and '@' in email and '.' in email.split('@')[-1]
            except Exception:
                return False

        # Helper to normalize incoming role labels (e.g., "Project Manager" -> "project_manager")
        def normalize_role(val: str | None) -> str:
            if not isinstance(val, str):
                return 'stakeholder'
            s = val.strip().lower()
            s = s.replace('-', '_').replace(' ', '_')
            return s or 'stakeholder'

        # Support adding by stakeholder_id (existing) or by name/email/role (new)
        if data.get('stakeholder_id'):
            stakeholder_id = data['stakeholder_id']
            current_app.logger.info(f"Adding existing stakeholder {stakeholder_id} to project {project_id}")
            stakeholder = Stakeholder.query.get_or_404(stakeholder_id)

            # Validate project role
            proj_role = normalize_role(data.get('role', 'stakeholder'))
            current_app.logger.info(f"Requested role: {proj_role}, allowed: {sorted(list(project_role_enums))}")
            if proj_role not in project_role_enums:
                current_app.logger.warning(f"Invalid project role: {proj_role}; coercing to 'stakeholder'")
                # Coerce to safe default instead of failing hard
                proj_role = 'stakeholder'

            # Check if stakeholder is already associated with this project
            existing_association = ProjectStakeholder.query.filter_by(
                project_id=project_id,
                stakeholder_id=stakeholder_id
            ).first()
            if existing_association:
                return jsonify({"error": "Stakeholder is already associated with this project"}), 400

            try:
                current_app.logger.info(f"Creating ProjectStakeholder: project={project_id}, stakeholder={stakeholder_id}, role={proj_role}")
                # Extra validation - ensure role is valid for ProjectStakeholder model
                if proj_role not in project_role_enums:
                    current_app.logger.warning(f"Invalid role value for ProjectStakeholder after coercion: {proj_role}; forcing 'stakeholder'")
                    proj_role = 'stakeholder'
                
                project_stakeholder = ProjectStakeholder(
                    project_id=project_id,
                    stakeholder_id=stakeholder_id,
                    role=proj_role,
                    can_review=bool(data.get('can_review', True)),
                    notes=data.get('notes')
                )
                db.session.add(project_stakeholder)
                current_app.logger.info(f"Committing ProjectStakeholder to database...")
                db.session.commit()
                current_app.logger.info(f"ProjectStakeholder created successfully: id={project_stakeholder.id}")
            except IntegrityError as ie:
                db.session.rollback()
                current_app.logger.error(f"IntegrityError: {ie}", exc_info=True)
                return jsonify({"error": "Duplicate association or constraint violation", "details": str(ie)}), 400
            except Exception as project_err:
                db.session.rollback()
                current_app.logger.error(f"Error creating project stakeholder: {project_err}", exc_info=True)
                raise

            # Build response safely
            try:
                response_data = {
                    "id": project_stakeholder.id,
                    "project_id": project_id,
                    "stakeholder_id": stakeholder_id,
                    "name": stakeholder.name,
                    "email": stakeholder.email,
                    "role": project_stakeholder.role,
                    "can_review": project_stakeholder.can_review,
                    "notes": project_stakeholder.notes,
                    "existing": True
                }
                # Only add created_at if it exists
                if hasattr(project_stakeholder, 'created_at') and project_stakeholder.created_at:
                    response_data["created_at"] = project_stakeholder.created_at.isoformat()
                return jsonify(response_data), 201
            except Exception as resp_err:
                current_app.logger.error(f"Error building response: {resp_err}", exc_info=True)
                # Return minimal response if we can't build the full one
                try:
                    return jsonify({
                        "id": project_stakeholder.id,
                        "project_id": project_id,
                        "stakeholder_id": stakeholder_id,
                        "role": proj_role,
                        "existing": True
                    }), 201
                except Exception as minimal_err:
                    current_app.logger.error(f"Error building minimal response: {minimal_err}", exc_info=True)
                    raise
        else:
            # Create new stakeholder and add to project
            required_fields = ['name', 'email', 'role']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({"error": f"{field} is required"}), 400

            # Validate email and stakeholder role
            if not validate_email(data['email']):
                return jsonify({"error": "Invalid email format"}), 400

            stakeholder_role = normalize_role(data.get('role', 'stakeholder'))
            if stakeholder_role not in allowed_creation_roles:
                return jsonify({
                    "error": f"Invalid role: {stakeholder_role}",
                    "allowed": sorted(list(allowed_creation_roles))
                }), 400

            # Reuse existing stakeholder by email if present
            stakeholder = Stakeholder.query.filter_by(email=data['email']).first()
            if not stakeholder:
                # Map project role to stakeholder role if needed
                # Default to 'stakeholder' for the Stakeholder.role field
                # The actual project-specific role is stored in ProjectStakeholder.role
                sh_role = stakeholder_role if stakeholder_role in stakeholder_role_enums else 'stakeholder'
                
                try:
                    stakeholder = Stakeholder(
                        name=data['name'],
                        email=data['email'],
                        title=data.get('title'),
                        organization=data.get('organization'),
                        role=sh_role,
                        can_review=bool(data.get('can_review', True)),
                        active=True  # Explicitly set active status
                    )
                except TypeError as te:
                    # Handle case where columns might not exist on older database
                    current_app.logger.warning(f"TypeError creating Stakeholder with all fields: {te}")
                    stakeholder = Stakeholder(
                        name=data['name'],
                        email=data['email'],
                        title=data.get('title'),
                        organization=data.get('organization')
                    )
                
                db.session.add(stakeholder)
                try:
                    db.session.flush()  # Assign ID
                except Exception as flush_err:
                    db.session.rollback()
                    current_app.logger.error(f"Error flushing stakeholder: {flush_err}", exc_info=True)
                    raise

            # Validate project role (can differ from stakeholder role set)
            proj_role = normalize_role(data.get('role', 'stakeholder'))
            if proj_role not in project_role_enums:
                current_app.logger.warning(f"Invalid project role for association: {proj_role}; coercing to 'stakeholder'")
                proj_role = 'stakeholder'

            try:
                current_app.logger.info(f"Creating ProjectStakeholder for new stakeholder: project={project_id}, stakeholder={stakeholder.id}, role={proj_role}")
                # Extra validation - ensure role is valid for ProjectStakeholder model
                if proj_role not in project_role_enums:
                    current_app.logger.warning(f"Invalid role value for ProjectStakeholder after coercion: {proj_role}; forcing 'stakeholder'")
                    proj_role = 'stakeholder'
                
                project_stakeholder = ProjectStakeholder(
                    project_id=project_id,
                    stakeholder_id=stakeholder.id,
                    role=proj_role,
                    can_review=bool(data.get('can_review', True)),
                    notes=data.get('notes')
                )
                db.session.add(project_stakeholder)
                db.session.commit()
                current_app.logger.info(f"ProjectStakeholder created successfully: id={project_stakeholder.id}")
            except IntegrityError as ie:
                db.session.rollback()
                current_app.logger.error(f"IntegrityError: {ie}", exc_info=True)
                return jsonify({"error": "Duplicate association or constraint violation", "details": str(ie)}), 400
            except Exception as project_err:
                db.session.rollback()
                current_app.logger.error(f"Error creating project stakeholder: {project_err}", exc_info=True)
                raise

            # Build response safely
            try:
                response_data = {
                    "id": project_stakeholder.id,
                    "project_id": project_id,
                    "stakeholder_id": stakeholder.id,
                    "name": stakeholder.name,
                    "email": stakeholder.email,
                    "role": project_stakeholder.role,
                    "can_review": project_stakeholder.can_review,
                    "notes": project_stakeholder.notes,
                    "existing": False
                }
                # Only add created_at if it exists
                if hasattr(project_stakeholder, 'created_at') and project_stakeholder.created_at:
                    response_data["created_at"] = project_stakeholder.created_at.isoformat()
                return jsonify(response_data), 201
            except Exception as resp_err:
                current_app.logger.error(f"Error building response: {resp_err}", exc_info=True)
                # Return minimal response if we can't build the full one
                try:
                    return jsonify({
                        "id": project_stakeholder.id,
                        "project_id": project_id,
                        "stakeholder_id": stakeholder.id,
                        "role": proj_role,
                        "existing": False
                    }), 201
                except Exception as minimal_err:
                    current_app.logger.error(f"Error building minimal response: {minimal_err}", exc_info=True)
                    raise
    except Exception as e:
        db.session.rollback()
        error_type = type(e).__name__
        error_msg = str(e)
        current_app.logger.error(
            f"Error adding stakeholder to project {project_id}: {error_type}: {error_msg}", 
            exc_info=True
        )
        return jsonify({
            "error": error_msg, 
            "type": error_type,
            "details": "Check server logs for more information"
        }), 500

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
