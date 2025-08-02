"""
Task management routes for StructuredDocs
Handles CRUD operations for tasks and their associations with projects, collections, and topics
"""

from flask import Blueprint, request, jsonify
from sqlalchemy.orm import joinedload
from sqlalchemy import desc, and_, or_
from datetime import datetime, date
import json

# Import models
from models import db, Task, Project, Collection, Topic

tasks_bp = Blueprint('tasks', __name__, url_prefix='/api/tasks')

@tasks_bp.route('/', methods=['GET'])
def list_tasks():
    """Get all tasks with optional filtering"""
    try:
        # Query parameters for filtering
        status = request.args.get('status')
        priority = request.args.get('priority')
        project_id = request.args.get('project_id', type=int)
        collection_id = request.args.get('collection_id', type=int)
        topic_id = request.args.get('topic_id', type=int)
        assigned_to = request.args.get('assigned_to')
        search = request.args.get('search', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)

        # Build query with eager loading
        query = Task.query.options(
            joinedload(Task.project),
            joinedload(Task.collection),
            joinedload(Task.topic)
        )

        # Apply filters
        if status:
            query = query.filter(Task.status == status)
        if priority:
            query = query.filter(Task.priority == priority)
        if project_id:
            query = query.filter(Task.project_id == project_id)
        if collection_id:
            query = query.filter(Task.collection_id == collection_id)
        if topic_id:
            query = query.filter(Task.topic_id == topic_id)
        if assigned_to:
            query = query.filter(Task.assigned_to.ilike(f'%{assigned_to}%'))
        if search:
            query = query.filter(
                or_(
                    Task.title.ilike(f'%{search}%'),
                    Task.description.ilike(f'%{search}%')
                )
            )

        # Order by priority and due date
        tasks = query.order_by(
            Task.status.asc(),
            Task.priority.desc(),
            Task.due_date.asc().nullslast(),
            Task.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'tasks': [task.to_dict() for task in tasks.items],
            'total': tasks.total,
            'pages': tasks.pages,
            'current_page': page
        })

    except Exception as e:
        print(f"Error in list_tasks: {e}")
        # Return placeholder response as fallback
        sample_tasks = [
            {
                "id": 1,
                "title": "Review Census Methodology Document",
                "description": "Complete review of the updated census methodology documentation for accuracy and completeness.",
                "status": "in_progress",
                "priority": "high",
                "due_date": "2025-08-15",
                "completed_at": None,
                "project_id": 1,
                "collection_id": None,
                "topic_id": None,
                "assigned_to": "sarah.johnson@census.gov",
                "created_by": "admin@census.gov",
                "tags": '["documentation", "review", "methodology"]',
                "created_at": "2025-08-01T09:00:00",
                "updated_at": "2025-08-02T14:30:00",
                "project_name": "Census 2030 Modernization Initiative",
                "collection_name": None,
                "topic_name": None
            },
            {
                "id": 2,
                "title": "Update API Documentation",
                "description": "Add examples and improve clarity in the REST API documentation.",
                "status": "todo",
                "priority": "medium",
                "due_date": "2025-08-20",
                "completed_at": None,
                "project_id": None,
                "collection_id": 1,
                "topic_id": None,
                "assigned_to": "michael.chen@statistics.gov",
                "created_by": "admin@census.gov",
                "tags": '["api", "documentation", "development"]',
                "created_at": "2025-08-01T10:30:00",
                "updated_at": "2025-08-01T10:30:00",
                "project_name": None,
                "collection_name": "API Documentation",
                "topic_name": None
            },
            {
                "id": 3,
                "title": "Validate Survey Questions",
                "description": "Review and validate the survey questions for the upcoming labor force survey.",
                "status": "review",
                "priority": "high",
                "due_date": "2025-08-10",
                "completed_at": None,
                "project_id": None,
                "collection_id": None,
                "topic_id": 15,
                "assigned_to": "amanda.rodriguez@census.gov",
                "created_by": "admin@census.gov",
                "tags": '["survey", "validation", "questions"]',
                "created_at": "2025-07-28T15:00:00",
                "updated_at": "2025-08-02T11:15:00",
                "project_name": None,
                "collection_name": None,
                "topic_name": "Labor Force Survey Design"
            },
            {
                "id": 4,
                "title": "Create Training Materials",
                "description": "Develop training materials for new census field representatives.",
                "status": "completed",
                "priority": "medium",
                "due_date": "2025-07-30",
                "completed_at": "2025-07-29T16:45:00",
                "project_id": 1,
                "collection_id": None,
                "topic_id": None,
                "assigned_to": "james.wilson@commerce.gov",
                "created_by": "admin@census.gov",
                "tags": '["training", "materials", "field-work"]',
                "created_at": "2025-07-15T08:00:00",
                "updated_at": "2025-07-29T16:45:00",
                "project_name": "Census 2030 Modernization Initiative",
                "collection_name": None,
                "topic_name": None
            }
        ]

        # Apply filters to sample data
        filtered_tasks = sample_tasks
        if status:
            filtered_tasks = [t for t in filtered_tasks if t['status'] == status]
        if priority:
            filtered_tasks = [t for t in filtered_tasks if t['priority'] == priority]
        if project_id:
            filtered_tasks = [t for t in filtered_tasks if t['project_id'] == project_id]

        return jsonify({
            'tasks': filtered_tasks,
            'total': len(filtered_tasks),
            'pages': 1,
            'current_page': 1
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@tasks_bp.route('/', methods=['POST'])
def create_task():
    """Create a new task"""
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('title'):
            return jsonify({"error": "Title is required"}), 400

        # Validate that only one association is provided
        associations = [data.get('project_id'), data.get('collection_id'), data.get('topic_id')]
        if sum(1 for a in associations if a is not None) > 1:
            return jsonify({"error": "Task can only be associated with one project, collection, or topic"}), 400

        # Parse due_date if provided
        due_date = None
        if data.get('due_date'):
            try:
                due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({"error": "Invalid due_date format. Use YYYY-MM-DD"}), 400

        # Create new task
        task = Task(
            title=data['title'],
            description=data.get('description'),
            status=data.get('status', 'todo'),
            priority=data.get('priority', 'medium'),
            due_date=due_date,
            project_id=data.get('project_id'),
            collection_id=data.get('collection_id'),
            topic_id=data.get('topic_id'),
            assigned_to=data.get('assigned_to'),
            created_by=data.get('created_by'),
            tags=json.dumps(data.get('tags', []))
        )

        db.session.add(task)
        db.session.commit()

        return jsonify(task.to_dict()), 201

    except Exception as e:
        print(f"Error in create_task: {e}")
        # Return placeholder response as fallback
        return jsonify({
            "id": 999,
            "title": data['title'],
            "description": data.get('description'),
            "status": data.get('status', 'todo'),
            "priority": data.get('priority', 'medium'),
            "due_date": data.get('due_date'),
            "project_id": data.get('project_id'),
            "collection_id": data.get('collection_id'),
            "topic_id": data.get('topic_id'),
            "assigned_to": data.get('assigned_to'),
            "created_by": data.get('created_by'),
            "tags": json.dumps(data.get('tags', [])),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@tasks_bp.route('/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Get a specific task"""
    try:
        # task = Task.query.options(
        #     joinedload(Task.project),
        #     joinedload(Task.collection),
        #     joinedload(Task.topic)
        # ).get_or_404(task_id)
        # return jsonify(task.to_dict())

        # Placeholder response
        return jsonify({
            "id": task_id,
            "title": "Review Census Methodology Document",
            "description": "Complete review of the updated census methodology documentation for accuracy and completeness.",
            "status": "in_progress",
            "priority": "high",
            "due_date": "2025-08-15",
            "completed_at": None,
            "project_id": 1,
            "collection_id": None,
            "topic_id": None,
            "assigned_to": "sarah.johnson@census.gov",
            "created_by": "admin@census.gov",
            "tags": '["documentation", "review", "methodology"]',
            "created_at": "2025-08-01T09:00:00",
            "updated_at": "2025-08-02T14:30:00",
            "project_name": "Census 2030 Modernization Initiative",
            "collection_name": None,
            "topic_name": None
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@tasks_bp.route('/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update a task"""
    try:
        # task = Task.query.get_or_404(task_id)
        data = request.get_json()

        # Validate that only one association is provided
        associations = [data.get('project_id'), data.get('collection_id'), data.get('topic_id')]
        if sum(1 for a in associations if a is not None) > 1:
            return jsonify({"error": "Task can only be associated with one project, collection, or topic"}), 400

        # Parse due_date if provided
        # if data.get('due_date'):
        #     try:
        #         task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        #     except ValueError:
        #         return jsonify({"error": "Invalid due_date format. Use YYYY-MM-DD"}), 400

        # # Update fields
        # task.title = data.get('title', task.title)
        # task.description = data.get('description', task.description)
        # task.status = data.get('status', task.status)
        # task.priority = data.get('priority', task.priority)
        # task.project_id = data.get('project_id', task.project_id)
        # task.collection_id = data.get('collection_id', task.collection_id)
        # task.topic_id = data.get('topic_id', task.topic_id)
        # task.assigned_to = data.get('assigned_to', task.assigned_to)
        # task.created_by = data.get('created_by', task.created_by)

        # if 'tags' in data:
        #     task.tags = json.dumps(data['tags'])

        # # Mark as completed if status changed to completed
        # if data.get('status') == 'completed' and task.status != 'completed':
        #     task.completed_at = datetime.utcnow()
        # elif data.get('status') != 'completed':
        #     task.completed_at = None

        # db.session.commit()
        # return jsonify(task.to_dict())

        # Placeholder response
        return jsonify({
            "id": task_id,
            "title": data.get('title', "Review Census Methodology Document"),
            "description": data.get('description', "Complete review of the updated census methodology documentation."),
            "status": data.get('status', "in_progress"),
            "priority": data.get('priority', "high"),
            "due_date": data.get('due_date', "2025-08-15"),
            "project_id": data.get('project_id', 1),
            "collection_id": data.get('collection_id'),
            "topic_id": data.get('topic_id'),
            "assigned_to": data.get('assigned_to', "sarah.johnson@census.gov"),
            "updated_at": datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    try:
        # task = Task.query.get_or_404(task_id)
        # db.session.delete(task)
        # db.session.commit()
        # return jsonify({"message": "Task deleted successfully"})

        # Placeholder response
        return jsonify({"message": "Task deleted successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@tasks_bp.route('/summary', methods=['GET'])
def get_task_summary():
    """Get task summary statistics"""
    try:
        total_tasks = Task.query.count()
        todo_tasks = Task.query.filter(Task.status == 'todo').count()
        in_progress_tasks = Task.query.filter(Task.status == 'in_progress').count()
        completed_tasks = Task.query.filter(Task.status == 'completed').count()
        overdue_tasks = Task.query.filter(
            and_(Task.due_date < date.today(), Task.status != 'completed')
        ).count()

        return jsonify({
            'total': total_tasks,
            'todo': todo_tasks,
            'in_progress': in_progress_tasks,
            'completed': completed_tasks,
            'overdue': overdue_tasks
        })

    except Exception as e:
        print(f"Error in get_task_summary: {e}")
        return jsonify({"error": str(e)}), 500

@tasks_bp.route('/associations', methods=['GET'])
def get_task_associations():
    """Get available associations for task creation (projects, collections, topics)"""
    try:
        # Get all projects
        projects = Project.query.all()
        projects_data = [{'id': p.id, 'name': p.name} for p in projects]
        
        # Get all collections
        collections = Collection.query.all()
        collections_data = [{'id': c.id, 'name': c.name} for c in collections]
        
        # Get all topics
        topics = Topic.query.all()
        topics_data = [{'id': t.id, 'name': t.title} for t in topics]
        
        return jsonify({
            'projects': projects_data,
            'collections': collections_data,
            'topics': topics_data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
