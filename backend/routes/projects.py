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
from ..utils.audit import log_audit

projects_bp = Blueprint('projects', __name__, url_prefix='/api/projects')

@projects_bp.route('/roles', methods=['GET'])
@jwt_required()
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
            current_app.logger.debug(f"[PROJECT_ARCHIVE] user_id={user_pk} project_id={project.id} previous_archived={prev} new_archived={project.archived} timestamp={datetime.utcnow().isoformat()}Z")
        except Exception:
            pass
        return jsonify({'project': project.to_dict(), 'previous_archived': prev}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/<int:project_id>', methods=['PUT'])
@jwt_required()
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
        log_audit('update', 'project', project_id, details={'name': project.name})
        return jsonify(project.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/', methods=['GET'])
@jwt_required()
def list_projects():
    """Get all projects with basic info"""
    import traceback
    try:
        projects = Project.query.order_by(desc(Project.updated_at)).all()
        return jsonify([project.to_dict() for project in projects])
    except Exception as e:
        current_app.logger.debug('Error in /api/projects:', e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@projects_bp.route('/<int:project_id>', methods=['GET'])
@jwt_required()
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
@jwt_required()
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
        log_audit('create', 'project', project.id, details={'name': project.name})
        return jsonify(project.to_dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@projects_bp.route('/<int:project_id>/stakeholders', methods=['GET'])
@jwt_required()
def get_project_stakeholders(project_id):
    """Get all stakeholders for a project"""
    from sqlalchemy.orm import joinedload
    try:
        current_app.logger.info(f"GET /api/projects/{project_id}/stakeholders - Fetching project stakeholders")
        
        # Verify project exists
        project = Project.query.get(project_id)
        if not project:
            current_app.logger.warning(f"Project {project_id} not found")
            return jsonify({"error": "Project not found"}), 404
        
        # Get all project stakeholders with their stakeholder details
        project_stakeholders = ProjectStakeholder.query.filter_by(project_id=project_id).options(joinedload(ProjectStakeholder.stakeholder)).all()
        current_app.logger.info(f"Found {len(project_stakeholders)} stakeholders for project {project_id}")
        
        result = []
        for ps in project_stakeholders:
            try:
                # Handle case where stakeholder relationship is null
                if not ps.stakeholder:
                    current_app.logger.warning(f"ProjectStakeholder {ps.id} has null stakeholder relationship")
                    continue
                
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
            except Exception as item_err:
                current_app.logger.error(f"Error serializing project stakeholder {ps.id}: {item_err}", exc_info=True)
                # Skip this item but continue with others
                continue
        
        current_app.logger.info(f"Returning {len(result)} serialized stakeholders")
        return jsonify(result)
    except Exception as e:
        current_app.logger.error(f"Error fetching project stakeholders: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@projects_bp.route('/<int:project_id>/stakeholders', methods=['POST'])
@jwt_required()
def add_project_stakeholder(project_id):
    """Add a stakeholder to a project with validation to avoid 500s."""
    from sqlalchemy.exc import IntegrityError

    try:
        # Parse JSON payload with extra error handling
        try:
            data = request.get_json(force=True, silent=False)
        except Exception as json_err:
            current_app.logger.error(f"JSON parse error: {json_err}", exc_info=True)
            # Try to get raw body
            try:
                raw_body = request.get_data(as_text=True)
                current_app.logger.error(f"Raw request body: {raw_body[:500]}")
            except Exception:
                pass
            return jsonify({"error": f"Invalid JSON payload: {str(json_err)}"}), 400
        
        if data is None:
            data = {}
        current_app.logger.info(f"POST /api/projects/{project_id}/stakeholders - Data: {data}")

        # Verify project exists
        try:
            project = Project.query.get(project_id)
            if not project:
                current_app.logger.warning(f"Project {project_id} not found")
                return jsonify({"error": f"Project {project_id} not found"}), 404
        except Exception as proj_err:
            current_app.logger.error(f"Error querying project {project_id}: {proj_err}", exc_info=True)
            return jsonify({"error": f"Error finding project: {str(proj_err)}"}), 500
        current_app.logger.info(f"Project {project_id} found: {project.name}")

        # Allowed roles — derive directly from SQLAlchemy Enum definitions
        try:
            stakeholder_role_enums = set(Stakeholder.__table__.c.role.type.enums)
        except Exception:
            stakeholder_role_enums = {'author', 'reviewer', 'subject_matter_expert', 'stakeholder', 'admin'}

        # ProjectStakeholder roles (what we want to support / now in project_stakeholder_role enum)
        desired_project_roles = {'project_manager', 'subject_matter_expert', 'reviewer', 'stakeholder', 'sponsor'}

        # Mapping: keep valid project roles; coerce legacy author/admin into supported roles
        project_role_to_db_role = {
            'author': 'project_manager',   # legacy value → project_manager
            'admin': 'sponsor',            # legacy value → sponsor
            'project_manager': 'project_manager',
            'sponsor': 'sponsor',
            'subject_matter_expert': 'subject_matter_expert',
            'reviewer': 'reviewer',
            'stakeholder': 'stakeholder'
        }

        try:
            project_role_enums = set(ProjectStakeholder.__table__.c.role.type.enums)
        except Exception:
            project_role_enums = desired_project_roles

        # When creating a new stakeholder, accept project roles as well (for Stakeholder.role mapping)
        allowed_creation_roles = stakeholder_role_enums | project_role_enums

        def validate_email(email: str) -> bool:
            try:
                return isinstance(email, str) and '@' in email and '.' in email.split('@')[-1]
            except Exception:
                return False

        # Helper to normalize incoming role labels (e.g., "Project Manager" -> "project_manager")
        def normalize_role(val: str | None, allowed_enums: set[str] | None = None) -> str:
            if not isinstance(val, str):
                return 'stakeholder'
            
            original = val
            s = val.strip().lower()
            # Replace common separators with underscores
            s = s.replace('-', '_').replace(' ', '_').replace('__', '_')
            
            # If the normalized value is in allowed enums, use it
            if allowed_enums and s in allowed_enums:
                current_app.logger.info(f"Role '{original}' normalized to '{s}' (allowed)")
                return s
            
            # Try explicit mappings for common UI labels
            role_aliases = {
                'project_manager': ['pm', 'project manager', 'project-manager', 'projectmanager'],
                'subject_matter_expert': ['sme', 'subject matter expert', 'subject-matter-expert', 'subjectmatterexpert'],
                'sponsor': ['project sponsor', 'project-sponsor', 'projectsponsor'],
                'reviewer': ['code reviewer', 'code-reviewer', 'peer reviewer'],
                'stakeholder': ['stake holder', 'stake-holder']
            }
            
            for canonical, aliases in role_aliases.items():
                normalized_aliases = [a.lower().replace('-', '_').replace(' ', '_') for a in aliases]
                if s in normalized_aliases:
                    if not allowed_enums or canonical in allowed_enums:
                        current_app.logger.info(f"Role '{original}' mapped to canonical '{canonical}'")
                        return canonical
            
            # Last resort: use the normalized form even if not in enums (may cause DB error but logged)
            current_app.logger.warning(f"Role '{original}' normalized to '{s}' but not in allowed enums: {allowed_enums}")
            return s or 'stakeholder'
        
        # Helper to map project roles to database-safe values (handles enum collision)
        def map_role_to_db_value(proj_role: str) -> str:
            """Map desired project role to actual database-allowed value"""
            return project_role_to_db_role.get(proj_role, proj_role)

        # Support adding by stakeholder_id (existing) or by name/email/role (new)
        if data.get('stakeholder_id'):
            stakeholder_id = data['stakeholder_id']
            current_app.logger.info(f"Adding existing stakeholder {stakeholder_id} to project {project_id}")
            stakeholder = Stakeholder.query.get_or_404(stakeholder_id)

            # Validate project role
            proj_role = normalize_role(data.get('role', 'stakeholder'), project_role_enums)
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
                
                # Map project role to database-safe value (due to enum collision in production)
                db_role = project_role_to_db_role.get(proj_role, proj_role)
                current_app.logger.info(f"Mapped role {proj_role} -> {db_role} for database")
                
                project_stakeholder = ProjectStakeholder(
                    project_id=project_id,
                    stakeholder_id=stakeholder_id,
                    role=db_role,
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
                return jsonify({"error": "Failed to create project stakeholder", "details": str(project_err)}), 500

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
                    return jsonify({"error": "Failed to build response"}), 500
        else:
            # Create new stakeholder and add to project
            required_fields = ['name', 'email', 'role']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({"error": f"{field} is required"}), 400

            # Validate email and stakeholder role
            if not validate_email(data['email']):
                return jsonify({"error": "Invalid email format"}), 400

            stakeholder_role = normalize_role(data.get('role', 'stakeholder'), allowed_creation_roles)
            if stakeholder_role not in allowed_creation_roles:
                return jsonify({
                    "error": f"Invalid role: {stakeholder_role}",
                    "allowed": sorted(list(allowed_creation_roles))
                }), 400

            # Reuse existing stakeholder by email if present
            try:
                stakeholder = Stakeholder.query.filter_by(email=data['email']).first()
            except Exception as query_err:
                current_app.logger.error(f"Error querying stakeholder by email: {query_err}", exc_info=True)
                return jsonify({"error": f"Failed to query stakeholder: {str(query_err)}"}), 500
            
            if not stakeholder:
                # Map project role to stakeholder role if needed
                # Default to 'stakeholder' for the Stakeholder.role field
                # The actual project-specific role is stored in ProjectStakeholder.role
                sh_role = stakeholder_role if stakeholder_role in stakeholder_role_enums else 'stakeholder'
                
                current_app.logger.info(f"Creating new Stakeholder: name={data['name']}, email={data['email']}, sh_role={sh_role}")
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
                    try:
                        stakeholder = Stakeholder(
                            name=data['name'],
                            email=data['email'],
                            title=data.get('title'),
                            organization=data.get('organization')
                        )
                    except Exception as alt_err:
                        current_app.logger.error(f"Error creating Stakeholder with minimal fields: {alt_err}", exc_info=True)
                        return jsonify({"error": f"Failed to create stakeholder: {str(alt_err)}"}), 400
                
                current_app.logger.info(f"Adding Stakeholder to session...")
                db.session.add(stakeholder)
                try:
                    current_app.logger.info(f"Flushing stakeholder to get ID...")
                    db.session.flush()  # Assign ID without committing
                    current_app.logger.info(f"Stakeholder assigned id={stakeholder.id}")
                except Exception as flush_err:
                    db.session.rollback()
                    current_app.logger.error(f"Error flushing stakeholder: {flush_err}", exc_info=True)
                    return jsonify({"error": f"Failed to save stakeholder: {str(flush_err)}"}), 400
            else:
                current_app.logger.info(f"Found existing Stakeholder with email {data['email']}: id={stakeholder.id}")

            # Validate project role (can differ from stakeholder role set)
            proj_role = normalize_role(data.get('role', 'stakeholder'), project_role_enums)
            if proj_role not in project_role_enums:
                current_app.logger.warning(f"Invalid project role for association: {proj_role}; coercing to 'stakeholder'")
                proj_role = 'stakeholder'

            try:
                current_app.logger.info(f"Creating ProjectStakeholder for new stakeholder: project={project_id}, stakeholder={stakeholder.id}, role={proj_role}")
                # Extra validation - ensure role is valid for ProjectStakeholder model
                if proj_role not in project_role_enums:
                    current_app.logger.warning(f"Invalid role value for ProjectStakeholder after coercion: {proj_role}; forcing 'stakeholder'")
                    proj_role = 'stakeholder'
                
                # Map project role to database-safe value (due to enum collision in production)
                db_role = project_role_to_db_role.get(proj_role, proj_role)
                current_app.logger.info(f"Mapped role {proj_role} -> {db_role} for database")
                
                project_stakeholder = ProjectStakeholder(
                    project_id=project_id,
                    stakeholder_id=stakeholder.id,
                    role=db_role,
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
                return jsonify({"error": "Failed to create project stakeholder", "details": str(project_err)}), 500

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
                    return jsonify({"error": "Failed to build response"}), 500
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
@jwt_required()
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
@jwt_required()
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
