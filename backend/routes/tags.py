"""
Tag management routes for StructuredDocs
Handles CRUD operations for tags
"""

from flask import Blueprint, request, jsonify
from sqlalchemy import desc
import json

# Import models
from ..models import db, Tag, Task

tags_bp = Blueprint('tags', __name__, url_prefix='/api/tags')

# Support both '/api/tags' and '/api/tags/' to avoid redirects through proxies
@tags_bp.route('', methods=['GET'])
@tags_bp.route('/', methods=['GET'])
def list_tags():
    """Get all tags with full details"""
    try:
        tags = Tag.query.order_by(Tag.name).all()
        return jsonify([tag.to_dict() for tag in tags])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Support both '/api/tags' and '/api/tags/' for POST
@tags_bp.route('', methods=['POST'])
@tags_bp.route('/', methods=['POST'])
def create_tag():
    """Create a new tag"""
    try:
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({"error": "Tag name is required"}), 400
            
        name = data['name'].strip()
        if not name:
            return jsonify({"error": "Tag name cannot be empty"}), 400
            
        # Check if tag already exists
        existing_tag = Tag.query.filter_by(name=name).first()
        if existing_tag:
            return jsonify({"error": "Tag already exists"}), 400
        
        # Avoid kwargs for SQLAlchemy model init to keep type checkers happy
        tag = Tag()
        tag.name = name
        db.session.add(tag)
        db.session.commit()
        
        return jsonify(tag.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@tags_bp.route('/<int:tag_id>', methods=['PUT'])
def update_tag(tag_id):
    """Update a tag"""
    try:
        tag = Tag.query.get_or_404(tag_id)
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({"error": "Tag name is required"}), 400
            
        name = data['name'].strip()
        if not name:
            return jsonify({"error": "Tag name cannot be empty"}), 400
            
        # Check if another tag with this name exists
        existing_tag = Tag.query.filter(Tag.name == name, Tag.id != tag_id).first()
        if existing_tag:
            return jsonify({"error": "Tag with this name already exists"}), 400
            
        old_name = tag.name
        tag.name = name
        
        # Update tag name in all tasks that use this tag
        if old_name != name:
            tasks_to_update = Task.query.all()
            for task in tasks_to_update:
                try:
                    task_tags = json.loads(task.tags or '[]')
                    if old_name in task_tags:
                        # Replace old tag name with new name
                        task_tags = [name if t == old_name else t for t in task_tags]
                        task.tags = json.dumps(task_tags)
                except:
                    continue
        
        db.session.commit()
        
        return jsonify(tag.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@tags_bp.route('/<int:tag_id>', methods=['DELETE'])
def delete_tag(tag_id):
    """Delete a tag.

    Optional query params:
      force=1 | true  -> Remove the tag from all tasks (including completed/cancelled) then delete.
      active_only=1   -> (default) Only block deletion if tag is used by active tasks (todo, in_progress, review).
    """
    try:
        tag = Tag.query.get_or_404(tag_id)

        force = request.args.get('force', '').lower() in ('1', 'true', 'yes')
        active_only = request.args.get('active_only', '1') not in ('0', 'false', 'no')

        # Gather tasks referencing this tag
        tasks_query = Task.query
        tasks_with_tag = []
        for task in tasks_query:  # (Small datasets acceptable; if large consider LIKE filter)
            try:
                task_tags = json.loads(task.tags or '[]')
                if isinstance(task_tags, list) and tag.name in task_tags:
                    tasks_with_tag.append(task)
            except Exception:
                continue

        if tasks_with_tag:
            # Optionally filter to only active tasks
            if active_only:
                active_statuses = {'todo', 'in_progress', 'review'}
                active_usage = [t for t in tasks_with_tag if t.status in active_statuses]
            else:
                active_usage = tasks_with_tag

            if active_usage and not force:
                sample_titles = ', '.join([t.title for t in active_usage[:3]])
                return jsonify({
                    "error": (
                        f"Cannot delete tag; referenced by {len(active_usage)} active task(s): {sample_titles}"
                        + ("..." if len(active_usage) > 3 else "")
                        + ". Add ?force=1 to remove it from all tasks and delete, or ?active_only=0 to consider completed tasks."
                    )
                }), 400

            if force:
                removed_from = 0
                for task in tasks_with_tag:
                    try:
                        tag_list = json.loads(task.tags or '[]')
                        if tag.name in tag_list:
                            tag_list = [t for t in tag_list if t != tag.name]
                            task.tags = json.dumps(tag_list)
                            removed_from += 1
                    except Exception:
                        continue
                # Commit intermediate task updates before deleting tag
                db.session.flush()

        db.session.delete(tag)
        db.session.commit()
        return jsonify({"message": "Tag deleted successfully", "force": force, "removed_task_refs": len(tasks_with_tag) if force else 0})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@tags_bp.route('/usage', methods=['GET'])
def tag_usage():
    """Get tag usage statistics"""
    try:
        tags = Tag.query.all()
        usage_stats = []
        
        for tag in tags:
            task_count = 0
            tasks = Task.query.all()
            for task in tasks:
                try:
                    task_tags = json.loads(task.tags or '[]')
                    if tag.name in task_tags:
                        task_count += 1
                except:
                    continue
                    
            usage_stats.append({
                "id": tag.id,
                "name": tag.name,
                "task_count": task_count,
                "created_at": tag.created_at.isoformat() if tag.created_at else None
            })
            
        # Sort by usage count (descending) then by name
        usage_stats.sort(key=lambda x: (-x['task_count'], x['name']))
        
        return jsonify(usage_stats)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
