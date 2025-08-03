# backend/models.py

from datetime import datetime
from sqlalchemy import Enum, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy import Table, Column, Integer
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    role = db.Column(
        Enum('author', 'reviewer', 'admin', name='user_role'),
        nullable=False,
        default='author',
        server_default='author'
    )
    active = db.Column(db.Boolean, nullable=False, default=True, server_default='1')
    created_at = db.Column(
        db.DateTime,
        server_default=func.now(),
        nullable=False
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "active": self.active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

# Pivot table: tracks topic ordering within a collection
collection_topic_tree = Table(
    'collection_topic_tree',
    db.Model.metadata,
    Column('collection_id', Integer, ForeignKey('collections.id', ondelete='CASCADE')),
    Column('topic_id', Integer, ForeignKey('topics.id', ondelete='CASCADE')),
    Column('parent_topic_id', Integer, ForeignKey('topics.id', ondelete='CASCADE'), nullable=True),
    Column('position', Integer, nullable=False, default=0)
)

class Collection(db.Model):
    __tablename__ = 'collections'

    id        = db.Column(db.Integer, primary_key=True)
    name      = db.Column(db.String(200), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('collections.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    position  = db.Column(db.Integer, nullable=False, default=0)

    # Nested children collections
    children = relationship(
        'Collection',
        backref=db.backref('parent', remote_side=[id]),
        cascade='all, delete-orphan'
    )

    # Project relationship
    project = relationship('Project', back_populates='collections')

    # Topics in this collection
    topics = relationship(
        'Topic',
        secondary=collection_topic_tree,
        backref='collections',
        order_by=collection_topic_tree.c.position,
        foreign_keys=[collection_topic_tree.c.collection_id, collection_topic_tree.c.topic_id]  # <-- add this line
    )

    # Hierarchical topics in this collection
    hierarchical_topics = relationship(
        'Topic',
        secondary=collection_topic_tree,
        primaryjoin=id == collection_topic_tree.c.collection_id,
        secondaryjoin=lambda: Topic.id == collection_topic_tree.c.topic_id,
        order_by=collection_topic_tree.c.position,
        viewonly=True,
        foreign_keys=[collection_topic_tree.c.collection_id, collection_topic_tree.c.topic_id]  # <-- add this line
    )

    def to_dict(self, include_children=True, include_topics=True):
        data = {
            'id': self.id,
            'name': self.name,
            'position': self.position,
            'parentId': self.parent_id,
            'projectId': self.project_id
        }
        if include_topics:
            # Use hierarchical topic structure instead of flat list
            data['topics'] = self.to_tree()
        if include_children:
            data['children'] = [
                c.to_dict(include_children, include_topics)
                for c in sorted(self.children, key=lambda x: x.position)
            ]
        return data

    def to_tree(self):
        # Build a tree of topics for this collection
        from collections import defaultdict
        rows = db.session.execute(
            collection_topic_tree.select().where(
                collection_topic_tree.c.collection_id == self.id
            ).order_by(collection_topic_tree.c.position)
        ).fetchall()
        topics = {t.id: t for t in self.topics}
        tree = defaultdict(list)
        for row in rows:
            topic = topics.get(row.topic_id)
            if topic:
                tree[row.parent_topic_id].append({
                    'id': topic.id,
                    'title': topic.title,
                    'children': []
                })
        # Recursively build children
        def build(parent_id):
            nodes = tree[parent_id]
            for node in nodes:
                node['children'] = build(node['id'])
            return nodes
        return build(None)

class Topic(db.Model):
    __tablename__ = 'topics'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=True)
    frontmatter = db.Column(db.Text, nullable=True)  # YAML frontmatter

    # Draft → Published → Archived
    status = db.Column(
        Enum('draft', 'pending_review', 'published', 'rejected', 'archived', name='topic_status'),
        nullable=False,
        default='draft',
        server_default='draft'
    )

    created_at = db.Column(
        db.DateTime,
        server_default=func.now(),
        nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationship to reusable links
    topic_links = relationship('TopicLink', back_populates='topic', cascade='all, delete-orphan')

    def to_dict(self, include_links=False):
        base = {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "frontmatter": self.frontmatter,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        if include_links:
            base["links"] = [tl.to_dict() for tl in self.topic_links]
            base["links_count"] = len(self.topic_links)
        return base

class ImportDocument(db.Model):
    __tablename__ = 'import_documents'

    SOURCE_TYPES = ('word', 'markdown')
    STATUSES     = ('staging', 'approved', 'rejected')
    REVIEW_STEPS = ('pending', 'sme_approved', 'final_approved')

    id          = db.Column(db.Integer, primary_key=True)
    filename    = db.Column(db.String(256), nullable=False)
    source_type = db.Column(
        Enum(*SOURCE_TYPES, name='source_type_enum'),
        nullable=False
    )
    status      = db.Column(
        Enum(*STATUSES, name='import_status_enum'),
        nullable=False,
        default='staging',
        server_default='staging'
    )
    review_step = db.Column(
        Enum(*REVIEW_STEPS, name='import_review_step'),
        nullable=False,
        default='pending',
        server_default='pending'
    )
    created_at  = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    reviewer    = db.Column(db.String(64), nullable=True)

    # One-to-many → each document has multiple heading items
    items = relationship(
        'ImportItem',
        back_populates='document',
        cascade='all, delete-orphan'
    )

    def to_dict(self, include_items=False):
        base = {
            "id": self.id,
            "filename": self.filename,
            "type": self.source_type,
            "status": self.status,
            "review_step": self.review_step,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "reviewed_at": self.reviewed_at and self.reviewed_at.isoformat(),
            "reviewer": self.reviewer,
            "topics_count": len(self.items)  # Add count of import items
        }
        if include_items:
            base["items"] = [item.to_dict() for item in self.items]
        return base

class ImportItem(db.Model):
    __tablename__ = 'import_items'

    id              = db.Column(db.Integer, primary_key=True)
    document_id     = db.Column(
        db.Integer,
        ForeignKey('import_documents.id', ondelete='CASCADE'),
        nullable=False
    )
    heading_order   = db.Column(db.Integer, nullable=False)
    title           = db.Column(db.String(200), nullable=False)
    content         = db.Column(db.Text, nullable=False)
    committed_topic = db.Column(
        db.Integer,
        ForeignKey('topics.id'),
        nullable=True
    )

    # Relationships back to parent document and committed Topic
    document = relationship('ImportDocument', back_populates='items')
    topic    = relationship('Topic', foreign_keys=[committed_topic])

    def to_dict(self):
        return {
            "id": self.id,
            "heading_order": self.heading_order,
            "title": self.title,
            "content": self.content,
            "committed_topic": self.committed_topic
        }

class Publication(db.Model):
    __tablename__ = 'publications'

    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at  = db.Column(
        db.DateTime,
        server_default=func.now(),
        nullable=False
    )

    # Top-level nodes for this publication
    nodes = relationship(
        'PublicationNode',
        back_populates='publication',
        cascade='all, delete-orphan'
    )
    def to_dict(self, include_nodes=False):
        base = {
            "id":          self.id,
            "title":       self.title,
            "description": self.description,
            "created_at":  self.created_at.isoformat(),
        }
        if include_nodes:
            base["nodes"] = [n.to_dict() for n in self.nodes]
        return base

class PublicationNode(db.Model):
    __tablename__ = 'publication_nodes'

    id              = db.Column(db.Integer, primary_key=True)
    publication_id  = db.Column(
        db.Integer,
        ForeignKey('publications.id', ondelete='CASCADE'),
        nullable=False
    )
    topic_id        = db.Column(
        db.Integer,
        ForeignKey('topics.id'),
        nullable=False
    )
    parent_id       = db.Column(
        db.Integer,
        ForeignKey('publication_nodes.id'),
        nullable=True
    )
    position        = db.Column(db.Integer, nullable=False, default=0)

    # Relationships
    publication = relationship('Publication', back_populates='nodes')
    topic       = relationship('Topic')
    children    = relationship(
        'PublicationNode',
        back_populates='parent',
        cascade='all, delete-orphan'
    )
    parent      = relationship(
        'PublicationNode',
        remote_side=[id],
        back_populates='children'
    )

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)  # Null for global notifications
    title = db.Column(db.String(128), nullable=False)
    message = db.Column(db.String(256), nullable=False)
    link = db.Column(db.String(256), nullable=True)
    type = db.Column(db.String(32), nullable=False, default='global')
    date = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'link': self.link,
            'type': self.type,
            'date': self.date.isoformat() if self.date else None,
            'read': self.read
        }

class Link(db.Model):
    """Reusable link objects that can be referenced across multiple topics"""
    __tablename__ = 'links'

    LINK_TYPES = ('form', 'document', 'website', 'policy', 'procedure', 'regulation', 'other')

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(512), nullable=False)
    description = db.Column(db.Text, nullable=True)
    reference_code = db.Column(db.String(100), nullable=True, unique=True)  # e.g., "AB-123"
    link_type = db.Column(
        Enum(*LINK_TYPES, name='link_type_enum'),
        nullable=False,
        default='other'
    )
    is_internal = db.Column(db.Boolean, nullable=False, default=False)  # Internal vs external link
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = db.Column(db.String(100), nullable=True)  # User who created the link

    # Relationship to track which topics use this link
    topic_links = relationship('TopicLink', back_populates='link', cascade='all, delete-orphan')

    def to_dict(self, include_usage=False):
        base = {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'description': self.description,
            'reference_code': self.reference_code,
            'link_type': self.link_type,
            'is_internal': self.is_internal,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by
        }
        if include_usage:
            base['usage_count'] = len(self.topic_links)
            base['used_in_topics'] = [tl.topic.title for tl in self.topic_links if tl.topic]
        return base

class TopicLink(db.Model):
    """Junction table linking topics to reusable links"""
    __tablename__ = 'topic_links'

    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(
        db.Integer,
        ForeignKey('topics.id', ondelete='CASCADE'),
        nullable=False
    )
    link_id = db.Column(
        db.Integer,
        ForeignKey('links.id', ondelete='CASCADE'),
        nullable=False
    )
    context = db.Column(db.String(200), nullable=True)  # Context where link appears in topic
    position = db.Column(db.Integer, nullable=False, default=0)  # Order within topic
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    topic = relationship('Topic', back_populates='topic_links')
    link = relationship('Link', back_populates='topic_links')

    # Unique constraint to prevent duplicate links in same topic
    __table_args__ = (db.UniqueConstraint('topic_id', 'link_id', name='unique_topic_link'),)

    def to_dict(self):
        return {
            'id': self.id,
            'topic_id': self.topic_id,
            'link_id': self.link_id,
            'context': self.context,
            'position': self.position,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'link': self.link.to_dict() if self.link else None
        }

class ImportImage(db.Model):
    """Track images extracted from imported documents"""
    __tablename__ = 'import_images'

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(
        db.Integer,
        ForeignKey('import_documents.id', ondelete='CASCADE'),
        nullable=False
    )
    filename = db.Column(db.String(256), nullable=False)
    original_name = db.Column(db.String(256), nullable=False)
    public_url = db.Column(db.String(512), nullable=False)
    backend_path = db.Column(db.String(512), nullable=False)
    frontend_path = db.Column(db.String(512), nullable=False)
    width = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Integer, nullable=True)
    format = db.Column(db.String(32), nullable=True)
    file_size = db.Column(db.Integer, nullable=True)
    mime_type = db.Column(db.String(64), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    document = relationship('ImportDocument', backref='images')

    def to_dict(self):
        return {
            'id': self.id,
            'document_id': self.document_id,
            'filename': self.filename,
            'original_name': self.original_name,
            'public_url': self.public_url,
            'width': self.width,
            'height': self.height,
            'format': self.format,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Stakeholder(db.Model):
    """Reusable stakeholder model that can be associated with multiple projects"""
    __tablename__ = 'stakeholders'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    title = db.Column(db.String(200), nullable=True)
    organization = db.Column(db.String(200), nullable=True)
    department = db.Column(db.String(200), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    expertise_areas = db.Column(db.Text, nullable=True)  # JSON string of expertise areas
    bio = db.Column(db.Text, nullable=True)
    active = db.Column(db.Boolean, nullable=False, default=True, server_default='1')
    created_at = db.Column(
        db.DateTime,
        server_default=func.now(),
        nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "title": self.title,
            "organization": self.organization,
            "department": self.department,
            "phone": self.phone,
            "expertise_areas": self.expertise_areas,
            "bio": self.bio,
            "active": self.active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class Project(db.Model):
    """Project management model"""
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(
        Enum('planning', 'active', 'review', 'completed', 'on_hold', name='project_status'),
        nullable=False,
        default='planning',
        server_default='planning'
    )
    start_date = db.Column(db.Date, nullable=True)
    target_completion = db.Column(db.Date, nullable=True)
    created_at = db.Column(
        db.DateTime,
        server_default=func.now(),
        nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships
    stakeholders = relationship('ProjectStakeholder', back_populates='project', cascade='all, delete-orphan')
    milestones = relationship('ProjectMilestone', back_populates='project', cascade='all, delete-orphan')
    collections = relationship('Collection', back_populates='project')

    def to_dict(self, include_details=False):
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "target_completion": self.target_completion.isoformat() if self.target_completion else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_details:
            data.update({
                "stakeholders": [s.to_dict() for s in self.stakeholders],
                "milestones": [m.to_dict() for m in sorted(self.milestones, key=lambda x: x.due_date or datetime.max.date())],
                "collections": [c.to_dict(include_children=False, include_topics=False) for c in self.collections],
                "publishedDocuments": []  # Placeholder for frontend compatibility
            })
        
        return data


class ProjectStakeholder(db.Model):
    """Association between projects and stakeholders with project-specific roles"""
    __tablename__ = 'project_stakeholders'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(
        db.Integer,
        db.ForeignKey('projects.id', ondelete='CASCADE'),
        nullable=False
    )
    stakeholder_id = db.Column(
        db.Integer,
        db.ForeignKey('stakeholders.id', ondelete='CASCADE'),
        nullable=False
    )
    role = db.Column(
        Enum('project_manager', 'subject_matter_expert', 'reviewer', 'stakeholder', 'sponsor', name='stakeholder_role'),
        nullable=False,
        default='stakeholder',
        server_default='stakeholder'
    )
    can_review = db.Column(db.Boolean, nullable=False, default=True, server_default='1')
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime,
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    project = relationship('Project', back_populates='stakeholders')
    stakeholder = relationship('Stakeholder')

    # Unique constraint to prevent duplicate stakeholder assignments to same project
    __table_args__ = (db.UniqueConstraint('project_id', 'stakeholder_id', name='unique_project_stakeholder'),)

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "stakeholder_id": self.stakeholder_id,
            "name": self.stakeholder.name if self.stakeholder else None,
            "email": self.stakeholder.email if self.stakeholder else None,
            "title": self.stakeholder.title if self.stakeholder else None,
            "role": self.role,
            "can_review": self.can_review,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "stakeholder": self.stakeholder.to_dict() if self.stakeholder else None
        }


class ProjectMilestone(db.Model):
    """Project milestones and deadlines"""
    __tablename__ = 'project_milestones'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(
        db.Integer,
        db.ForeignKey('projects.id', ondelete='CASCADE'),
        nullable=False
    )
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.Date, nullable=True)
    status = db.Column(
        Enum('planned', 'in-progress', 'completed', 'overdue', name='milestone_status'),
        nullable=False,
        default='planned',
        server_default='planned'
    )
    completion_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(
        db.DateTime,
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    project = relationship('Project', back_populates='milestones')

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "name": self.name,
            "description": self.description,
            "date": self.date.isoformat() if self.date else None,
            "status": self.status,
            "completion_date": self.completion_date.isoformat() if self.completion_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Task(db.Model):
    """Task management model for projects, collections, and topics"""
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(
        Enum('todo', 'in_progress', 'review', 'completed', 'cancelled', name='task_status'),
        nullable=False,
        default='todo',
        server_default='todo'
    )
    priority = db.Column(
        Enum('low', 'medium', 'high', 'urgent', name='task_priority'),
        nullable=False,
        default='medium',
        server_default='medium'
    )
    due_date = db.Column(db.Date, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Association fields - a task can be associated with one of these
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    collection_id = db.Column(db.Integer, db.ForeignKey('collections.id'), nullable=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=True)
    
    # Assignment
    assigned_to = db.Column(db.String(100), nullable=True)  # Could be stakeholder name or email
    created_by = db.Column(db.String(100), nullable=True)
    
    # Tags for categorization
    tags = db.Column(db.Text, nullable=True)  # JSON string of tags
    
    created_at = db.Column(
        db.DateTime,
        server_default=func.now(),
        nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships
    project = relationship('Project', backref='tasks')
    collection = relationship('Collection', backref='tasks')
    topic = relationship('Topic', backref='tasks')

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "project_id": self.project_id,
            "collection_id": self.collection_id,
            "topic_id": self.topic_id,
            "assigned_to": self.assigned_to,
            "created_by": self.created_by,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            # Include related object names for display
            "project_name": self.project.name if self.project else None,
            "collection_name": self.collection.name if self.collection else None,
            "topic_name": self.topic.title if self.topic else None  # Topic uses 'title' not 'name'
        }