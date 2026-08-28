---
description: "Use when adding database validation, error handling in route handlers, or working with rollback/commit patterns in StructuredDocs backend. Covers model validation, transaction safety, and consistent error responses."
name: "StructuredDocs Backend Validation & Error Handling"
applyTo: "backend/models.py,backend/routes/**/*.py"
---
# Backend Validation & Error Handling Patterns

StructuredDocs backend uses SQLAlchemy with careful validation and transaction management to maintain data consistency.

## Model Validation

Validation should happen in the model layer, not just the route:

```python
# backend/models.py
from sqlalchemy import Column, String, Integer, Boolean, DateTime
from datetime import datetime

class Topic(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    collection_id = Column(Integer, ForeignKey('collection.id'), nullable=False)
    position = Column(Integer, default=0, server_default='0')
    archived = Column(Boolean, default=False, server_default='false')
    created_at = Column(DateTime, default=datetime.utcnow, server_default=func.now())
    
    def __init__(self, name, collection_id, position=0):
        # Validation in constructor
        if not name or len(name) < 1:
            raise ValueError("Topic name cannot be empty")
        if not isinstance(position, int) or position < 0:
            raise ValueError("Position must be a non-negative integer")
        
        self.name = name
        self.collection_id = collection_id
        self.position = position
    
    def to_dict(self):
        """Serialize to JSON."""
        return {
            'id': self.id,
            'name': self.name,
            'collection_id': self.collection_id,
            'position': self.position,
            'archived': self.archived,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
```

## Route Handler Pattern

```python
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError

@bp.post('/topics')
@jwt_required()
def create_topic():
    """Create a new topic with validation."""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    try:
        # Validate input
        if not data or 'name' not in data:
            return {'error': 'Topic name is required'}, 400
        
        # Validate foreign key exists
        collection = Collection.query.get(data.get('collection_id'))
        if not collection:
            return {'error': 'Collection not found'}, 404
        
        # Check permissions (user can edit collection)
        if collection.project.owner_id != user_id:
            return {'error': 'Unauthorized'}, 403
        
        # Create model (constructor validates)
        topic = Topic(
            name=data['name'],
            collection_id=data['collection_id'],
            position=data.get('position', 0),
        )
        
        # Add and commit
        db.session.add(topic)
        db.session.commit()
        
        return topic.to_dict(), 201
        
    except ValueError as e:
        # Model validation error
        db.session.rollback()
        return {'error': str(e)}, 400
    except IntegrityError as e:
        # Database constraint violation (e.g., duplicate unique field)
        db.session.rollback()
        current_app.logger.exception(f"Database integrity error: {e}")
        return {'error': 'Data validation failed'}, 409
    except Exception as e:
        # Unexpected error
        db.session.rollback()
        current_app.logger.exception(f"Create topic failed: {e}")
        return {'error': 'Internal server error'}, 500
```

## Common Error Response Patterns

```python
# Validation error (4xx)
return {'error': 'Invalid input', 'details': {...}}, 400

# Not found (4xx)
return {'error': f'Topic {id} not found'}, 404

# Unauthorized (4xx)
return {'error': 'Unauthorized'}, 403

# Conflict (4xx) — e.g., unique constraint violation
return {'error': 'Resource already exists'}, 409

# Server error (5xx) — always log these
current_app.logger.exception("Unhandled error")
return {'error': 'Internal server error'}, 500
```

## Transaction & Rollback Patterns

### Automatic Rollback on Error
```python
try:
    topic.name = new_name
    db.session.commit()
except Exception as e:
    db.session.rollback()
    raise
```

### Nested Transactions / Savepoints
```python
try:
    db.session.add(topic1)
    db.session.flush()  # Check constraints without committing
    
    # If this fails, only topic2 is rolled back
    savepoint = db.session.begin_nested()
    try:
        db.session.add(topic2)
        db.session.commit()
    except Exception:
        savepoint.rollback()
        raise
    
    db.session.commit()
except Exception:
    db.session.rollback()
```

## Update Handler Pattern

```python
@bp.put('/topics/<int:topic_id>')
@jwt_required()
def update_topic(topic_id):
    """Update a topic with validation."""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    try:
        topic = Topic.query.get(topic_id)
        if not topic:
            return {'error': 'Topic not found'}, 404
        
        # Check permissions
        if topic.collection.project.owner_id != user_id:
            return {'error': 'Unauthorized'}, 403
        
        # Update only allowed fields
        if 'name' in data:
            if not data['name']:
                return {'error': 'Topic name cannot be empty'}, 400
            topic.name = data['name']
        
        if 'position' in data:
            if not isinstance(data['position'], int) or data['position'] < 0:
                return {'error': 'Position must be non-negative'}, 400
            topic.position = data['position']
        
        db.session.commit()
        return topic.to_dict(), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception(f"Update topic failed: {e}")
        return {'error': 'Internal server error'}, 500
```

## Delete Handler Pattern

```python
@bp.delete('/topics/<int:topic_id>')
@jwt_required()
def delete_topic(topic_id):
    """Delete (or archive) a topic."""
    user_id = get_jwt_identity()
    
    try:
        topic = Topic.query.get(topic_id)
        if not topic:
            return {'error': 'Topic not found'}, 404
        
        # Check permissions
        if topic.collection.project.owner_id != user_id:
            return {'error': 'Unauthorized'}, 403
        
        # Soft delete (archival) or hard delete
        # Prefer archival (no data loss, reversible)
        topic.archived = True
        # Or: db.session.delete(topic)
        
        db.session.commit()
        return {'status': 'deleted'}, 204
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception(f"Delete topic failed: {e}")
        return {'error': 'Internal server error'}, 500
```

## Validation Checklist

When adding a new field or constraint:

- [ ] Field has `nullable=False` or `server_default` (no data loss for existing rows)
- [ ] Model constructor validates input
- [ ] Route handler checks permissions before writing
- [ ] Route handler validates foreign keys exist
- [ ] Route handler catches and rolls back on error
- [ ] Sensitive operations are logged (but not passwords)
- [ ] `to_dict()` is updated to include/exclude new fields
- [ ] Tests validate error cases (invalid input, not found, unauthorized)

## Archival vs. Hard Delete

StructuredDocs prefers archival (soft delete) over hard delete:

```python
# Archival (preferred)
topic.archived = True
db.session.commit()

# Can be restored later (reversible)
topic.archived = False
db.session.commit()

# Queries exclude archived by default
topics = Topic.query.filter(Topic.archived == False).all()

# Hard delete (use sparingly)
db.session.delete(topic)
db.session.commit()
```

## Handling Cascading Operations

When deleting a parent, handle children:

```python
@bp.delete('/collections/<int:collection_id>')
@jwt_required()
def delete_collection(collection_id):
    """Delete collection and archive child topics."""
    try:
        collection = Collection.query.get(collection_id)
        if not collection:
            return {'error': 'Collection not found'}, 404
        
        # Archive child topics instead of deleting
        for topic in collection.topics:
            topic.archived = True
        
        # Soft delete collection
        collection.archived = True
        db.session.commit()
        
        return {'status': 'deleted'}, 204
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception(f"Delete collection failed: {e}")
        return {'error': 'Internal server error'}, 500
```

## Server Default Values

Always include `server_default` for new columns:

```python
# Good: existing rows get default value
created_at = Column(DateTime, server_default=func.now())
archived = Column(Boolean, default=False, server_default='false')
position = Column(Integer, default=0, server_default='0')

# Bad: existing rows become NULL
new_field = Column(String(255), nullable=False)  # Will fail on existing rows!

# Fix: add server_default
new_field = Column(String(255), nullable=False, server_default='')
```

## Testing Patterns

```python
# test_topics.py
def test_create_topic_invalid_name(app, client, jwt_token):
    """Test that empty name is rejected."""
    response = client.post(
        '/api/topics',
        json={'name': '', 'collection_id': 1},
        headers={'Authorization': f'Bearer {jwt_token}'},
    )
    assert response.status_code == 400
    assert 'error' in response.json

def test_create_topic_collection_not_found(app, client, jwt_token):
    """Test that invalid collection_id is rejected."""
    response = client.post(
        '/api/topics',
        json={'name': 'Test', 'collection_id': 99999},
        headers={'Authorization': f'Bearer {jwt_token}'},
    )
    assert response.status_code == 404
```

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| "Unique constraint violation" | Duplicate value in unique field | Check data for existing entry, use `get_or_create` pattern |
| "Foreign key constraint failed" | Parent record doesn't exist | Validate foreign key exists before creating child |
| Existing rows become NULL | Missing `server_default` on new column | Add `server_default`, run migration again |
| Database locked/deadlock | Long transaction or concurrent writes | Keep transactions short, use proper isolation levels |
| `to_dict()` includes sensitive field | Password or token exposed in API | Update `to_dict()` to exclude sensitive fields |

## Files to Check

- `backend/models.py` — model validation, `to_dict()` patterns
- `backend/routes/*.py` — route handler error handling
- `conftest.py` — test fixtures with rollback/reset
- `backend/migrations/` — migration patterns with `server_default`

**Read:** [.github/instructions/backend.instructions.md](./backend.instructions.md) for route patterns  
**Read:** [.github/instructions/migrations.instructions.md](./migrations.instructions.md) for migration safety
