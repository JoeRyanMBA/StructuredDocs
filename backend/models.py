# backend/models.py

from datetime import datetime
from sqlalchemy import Enum, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy import Table, Column, Integer
from backend.extensions import db
from typing import TYPE_CHECKING

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=True)
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

    password_reset_tokens = relationship("PasswordResetToken", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "active": self.active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    if TYPE_CHECKING:
        def __init__(self, id: int | None = None, name: str = ..., email: str = ..., password_hash: str | None = None, role: str = 'author', active: bool = True, created_at: datetime | None = None): ...

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
    description = db.Column(db.Text, nullable=True)  # Add description field
    form_number = db.Column(db.String(100), nullable=False, unique=True)  # Collection ID (Form Number)
    parent_id = db.Column(db.Integer, db.ForeignKey('collections.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    position  = db.Column(db.Integer, nullable=False, default=0)
    archived  = db.Column(db.Boolean, nullable=False, default=False, server_default='0')  # Soft archive flag
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

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
            'form_number': self.form_number,
            'description': self.description,
            'position': self.position,
            'parentId': self.parent_id,
            'projectId': self.project_id,
            'archived': self.archived,
            'topics_count': len(self.topics),  # Add topic count
            'created_at': self.created_at.isoformat() if hasattr(self, 'created_at') and self.created_at else None,
            'updated_at': self.updated_at.isoformat() if hasattr(self, 'updated_at') and self.updated_at else None,
            'projectName': self.project.name if self.project else None
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

    if TYPE_CHECKING:
        def __init__(self, id: int | None = None, name: str = ..., description: str | None = None, form_number: str = ..., parent_id: int | None = None, project_id: int | None = None, position: int = 0, created_at: datetime | None = None, updated_at: datetime | None = None): ...

class Topic(db.Model):
    __tablename__ = 'topics'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=True)
    frontmatter = db.Column(db.Text, nullable=True)  # YAML frontmatter

    # Draft → Pending Review → [Revisions Requested] → Approved → Published → Archived
    status = db.Column(
        Enum('draft', 'pending_review', 'revisions_requested', 'approved', 'published', 'rejected', 'archived', name='topic_status'),
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

    if TYPE_CHECKING:
        def __init__(self, id: int | None = None, title: str = ..., content: str | None = None, frontmatter: str | None = None, status: str = 'draft', created_at: datetime | None = None, updated_at: datetime | None = None): ...

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

    if TYPE_CHECKING:
        def __init__(self, id: int | None = None, filename: str = ..., source_type: str = ..., status: str = 'staging', review_step: str = 'pending', created_at: datetime | None = None, reviewed_at: datetime | None = None, reviewer: str | None = None): ...

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

    if TYPE_CHECKING:
        def __init__(self, id: int | None = None, document_id: int = ..., heading_order: int = ..., title: str = ..., content: str = ..., committed_topic: int | None = None): ...

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
            "topics_count": len(self.nodes),  # Count of publication nodes (topics)
        }
        if include_nodes:
            base["nodes"] = [n.to_dict() for n in self.nodes]
        return base

    if TYPE_CHECKING:
        # Hint constructor parameters for static analysis (SQLAlchemy supplies these dynamically at runtime)
        def __init__(self, id: int | None = None, title: str = ..., description: str | None = None, created_at: datetime | None = None): ...

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

    # Snapshotted substituted text
    title_snapshot = db.Column(db.String(200), nullable=True)
    content_snapshot = db.Column(db.Text, nullable=True)

    if TYPE_CHECKING:
        def __init__(self, id: int | None = None, publication_id: int = ..., topic_id: int = ..., parent_id: int | None = None, position: int = ..., title_snapshot: str | None = None, content_snapshot: str | None = None): ...

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

    if TYPE_CHECKING:
        def __init__(self, id: int | None = None, document_id: int = ..., filename: str = ..., original_name: str = ..., public_url: str = ..., backend_path: str = ..., frontend_path: str = ..., width: int | None = None, height: int | None = None, format: str | None = None, file_size: int | None = None, mime_type: str | None = None, created_at: datetime | None = None): ...


class ImportLink(db.Model):
    """Track links extracted from imported documents"""
    __tablename__ = 'import_links'

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(
        db.Integer,
        ForeignKey('import_documents.id', ondelete='CASCADE'),
        nullable=False
    )
    title = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(512), nullable=False)
    description = db.Column(db.Text, nullable=True)
    link_type = db.Column(
        Enum('form', 'document', 'website', 'policy', 'procedure', 'regulation', 'other', name='link_type_enum'),
        nullable=False,
        default='website'
    )
    is_internal = db.Column(db.Boolean, nullable=False, default=False)
    context = db.Column(db.Text, nullable=True)  # Surrounding text where the link was found
    position_in_document = db.Column(db.Integer, nullable=True)  # Order of appearance in document
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    document = relationship('ImportDocument', backref='links')

    def to_dict(self):
        return {
            'id': self.id,
            'document_id': self.document_id,
            'title': self.title,
            'url': self.url,
            'description': self.description,
            'link_type': self.link_type,
            'is_internal': self.is_internal,
            'context': self.context,
            'position_in_document': self.position_in_document,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'source': 'import',
            'reference_code': f"IMP-{self.document_id}-{self.id}",  # Auto-generated reference
            'is_active': True,  # Imported links are considered active by default
        }

    if TYPE_CHECKING:
        def __init__(self, id: int | None = None, document_id: int = ..., title: str = ..., url: str = ..., description: str | None = None, link_type: str = ..., is_internal: bool = ..., context: str | None = None, position_in_document: int | None = None, created_at: datetime | None = None): ...


class Stakeholder(db.Model):
    """Reusable stakeholder model that can be associated with multiple projects"""
    __tablename__ = 'stakeholders'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    title = db.Column(db.String(200), nullable=True)
    organization = db.Column(db.String(200), nullable=True)
    division = db.Column(db.String(200), nullable=True)
    department = db.Column(db.String(200), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    expertise_areas = db.Column(db.Text, nullable=True)  # JSON string of expertise areas
    bio = db.Column(db.Text, nullable=True)
    role = db.Column(
        Enum('author', 'reviewer', 'subject_matter_expert', 'stakeholder', 'admin', name='stakeholder_role'),
        nullable=False,
        default='stakeholder',
        server_default='stakeholder'
    )
    can_review = db.Column(db.Boolean, nullable=False, default=True, server_default='1')
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
            "division": self.division,
            "department": self.department,
            "phone": self.phone,
            "expertise_areas": self.expertise_areas,
            "bio": self.bio,
            "role": self.role,
            "can_review": self.can_review,
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
    archived = db.Column(db.Boolean, nullable=False, default=False, server_default='0')

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
            "archived": self.archived,
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
        Enum('project_manager', 'subject_matter_expert', 'reviewer', 'stakeholder', 'sponsor', name='project_stakeholder_role'),
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
        import json
        try:
            tags = json.loads(self.tags) if self.tags else []
        except Exception:
            tags = []
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
            "tags": tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            # Include related object names for display
            "project_name": self.project.name if self.project else None,
            "collection_name": self.collection.name if self.collection else None,
            "topic_name": self.topic.title if self.topic else None  # Topic uses 'title' not 'name'
        }


class Tag(db.Model):
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(
        db.DateTime,
        server_default=func.now(),
        nullable=False
    )
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


###############################################
# Variable / Token Substitution Models
###############################################

class Variable(db.Model):
    """User-defined variable tokens (e.g., {{Organization}}) that resolve to a selected value at publish time."""
    __tablename__ = 'variables'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)  # Display name
    slug = db.Column(db.String(120), nullable=False, unique=True)  # Token slug used inside {{slug}}
    description = db.Column(db.Text, nullable=True)
    scope = db.Column(
        Enum('global', 'collection', name='variable_scope_enum'),
        nullable=False,
        default='global',
        server_default='global'
    )
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship: values
    values = relationship('VariableValue', back_populates='variable', cascade='all, delete-orphan')

    def to_dict(self, include_values=False, selection_map=None):
        data = {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'scope': self.scope,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_values:
            data['values'] = [v.to_dict() for v in self.values]
            # Attach current selection (if provided mapping of variable_id -> value_id)
            if selection_map is not None:
                data['selected_value_id'] = selection_map.get(self.id)
        return data


class VariableValue(db.Model):
    __tablename__ = 'variable_values'

    id = db.Column(db.Integer, primary_key=True)
    variable_id = db.Column(db.Integer, db.ForeignKey('variables.id', ondelete='CASCADE'), nullable=False)
    value = db.Column(db.String(500), nullable=False)
    is_default = db.Column(db.Boolean, nullable=False, default=False, server_default='0')
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)

    variable = relationship('Variable', back_populates='values')

    __table_args__ = (
        db.UniqueConstraint('variable_id', 'value', name='uq_variable_value'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'variable_id': self.variable_id,
            'value': self.value,
            'is_default': self.is_default,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class CollectionVariableSelection(db.Model):
    """Stores which value a collection has selected for a variable."""
    __tablename__ = 'collection_variable_selections'

    id = db.Column(db.Integer, primary_key=True)
    collection_id = db.Column(db.Integer, db.ForeignKey('collections.id', ondelete='CASCADE'), nullable=False)
    variable_id = db.Column(db.Integer, db.ForeignKey('variables.id', ondelete='CASCADE'), nullable=False)
    variable_value_id = db.Column(db.Integer, db.ForeignKey('variable_values.id', ondelete='SET NULL'), nullable=True)
    locked = db.Column(db.Boolean, nullable=False, default=False, server_default='0')  # future: prevent override at publish time
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)

    variable = relationship('Variable')
    value = relationship('VariableValue')

    __table_args__ = (
        db.UniqueConstraint('collection_id', 'variable_id', name='uq_collection_variable'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'collection_id': self.collection_id,
            'variable_id': self.variable_id,
            'variable_value_id': self.variable_value_id,
            'locked': self.locked,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


def build_variable_mapping_for_collection(collection_id):
    """Helper to build slug -> replacement string mapping for a collection.

    Resolution order:
      1. Explicit collection selection if exists.
      2. Variable default value (is_default=True) if present.
      3. Empty string (or '{{slug}}' left intact) if no value available.
    Returns (mapping, unresolved_slugs)
    """
    # Lazy imports to avoid circular
    from .models import Variable, VariableValue, CollectionVariableSelection  # type: ignore
    variables = Variable.query.all()
    selections = CollectionVariableSelection.query.filter_by(collection_id=collection_id).all()
    selection_map = {s.variable_id: s.variable_value_id for s in selections}
    # Load chosen values
    value_lookup = {}
    if selection_map:
        chosen_values = VariableValue.query.filter(VariableValue.id.in_(selection_map.values())).all()
        value_lookup = {v.id: v for v in chosen_values}

    mapping = {}
    unresolved = []
    for var in variables:
        chosen_value_id = selection_map.get(var.id)
        replacement = None
        if chosen_value_id:
            vv = value_lookup.get(chosen_value_id)
            if vv:
                replacement = vv.value
        if replacement is None:
            # Try default
            default_val = next((v for v in var.values if v.is_default), None)
            replacement = default_val.value if default_val else None
        if replacement is None:
            unresolved.append(var.slug)
            # Leave token unresolved; could choose '' instead
            continue
        mapping[var.slug] = replacement
    return mapping, unresolved


def substitute_variables_in_text(text: str, mapping: dict[str, str]) -> str:
    """Replace occurrences of {{slug}} in text with provided mapping values.
    Only exact double-brace tokens are replaced. Unknown tokens left intact."""
    if not text or not mapping:
        return text
    import re
    pattern = re.compile(r'\{\{([A-Za-z0-9_\-]+)\}\}')

    from typing import Match

    def repl(match: 'Match[str]') -> str:  # type: ignore[type-arg]
        slug = match.group(1)
        replacement = mapping.get(slug)
        if replacement is None:
            return match.group(0)
        return replacement

    return pattern.sub(repl, text)


class Review(db.Model):
    """Review model for tracking topic reviews and feedback"""
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # What's being reviewed
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False)
    
    # Who requested the review (author)
    requested_by = db.Column(db.Integer, db.ForeignKey('stakeholders.id'), nullable=False)
    
    # Who should do the review
    reviewer_id = db.Column(db.Integer, db.ForeignKey('stakeholders.id'), nullable=False)
    
    # Review status
    status = db.Column(
        Enum('pending', 'in_progress', 'completed', 'declined', name='review_status'),
        nullable=False,
        default='pending',
        server_default='pending'
    )
    
    # Review priority
    priority = db.Column(
        Enum('low', 'medium', 'high', 'urgent', name='review_priority'),
        nullable=False,
        default='medium',
        server_default='medium'
    )
    
    # Timing
    requested_at = db.Column(
        db.DateTime,
        server_default=func.now(),
        nullable=False
    )
    due_date = db.Column(db.DateTime, nullable=True)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    follow_up_sent_at = db.Column(db.DateTime, nullable=True)  # Track when follow-up reminder was sent
    
    # Feedback
    feedback = db.Column(db.Text, nullable=True)
    recommendation = db.Column(
        Enum('approve', 'approve_with_changes', 'reject', 'needs_more_info', name='review_recommendation'),
        nullable=True
    )
    
    # Additional context
    review_notes = db.Column(db.Text, nullable=True)  # Private notes from reviewer
    author_message = db.Column(db.Text, nullable=True)  # Message from author when requesting
    edited_content = db.Column(db.Text, nullable=True)  # Edited content from WYSIWYG editor
    
    # Sequential review tracking
    sequence_id = db.Column(db.Integer, db.ForeignKey('review_sequences.id'), nullable=True)
    sequence_position = db.Column(db.Integer, nullable=True)  # Position in the sequence (0-based)
    
    # Relationships
    topic = relationship('Topic', backref='reviews')
    requester = relationship('Stakeholder', foreign_keys=[requested_by], backref='requested_reviews')
    reviewer = relationship('Stakeholder', foreign_keys=[reviewer_id], backref='assigned_reviews')
    sequence = relationship('ReviewSequence', back_populates='reviews')
    
    def to_dict(self):
        return {
            "id": self.id,
            "topic_id": self.topic_id,
            "topic_title": self.topic.title if self.topic else None,
            "topic_status": self.topic.status if self.topic else None,
            "requested_by": self.requested_by,
            "requester_name": self.requester.name if self.requester else None,
            "reviewer_id": self.reviewer_id,
            "reviewer_name": self.reviewer.name if self.reviewer else None,
            "status": self.status,
            "priority": self.priority,
            "requested_at": self.requested_at.isoformat() if self.requested_at else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "follow_up_sent_at": self.follow_up_sent_at.isoformat() if self.follow_up_sent_at else None,
            "feedback": self.feedback,
            "recommendation": self.recommendation,
            "review_notes": self.review_notes,
            "author_message": self.author_message,
            "edited_content": self.edited_content,
            "sequence_id": self.sequence_id,
            "sequence_position": self.sequence_position
        }

    if TYPE_CHECKING:
        def __init__(self, id: int | None = None, topic_id: int = ..., requested_by: int = ..., reviewer_id: int = ..., status: str = 'pending', priority: str = 'medium', requested_at: datetime | None = None, due_date: datetime | None = None, started_at: datetime | None = None, completed_at: datetime | None = None, follow_up_sent_at: datetime | None = None, feedback: str | None = None, recommendation: str | None = None, review_notes: str | None = None, author_message: str | None = None, edited_content: str | None = None, sequence_id: int | None = None, sequence_position: int | None = None): ...


class PasswordResetToken(db.Model):
    """Model for password reset tokens"""
    __tablename__ = 'password_reset_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(64), nullable=False, unique=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token_type = db.Column(
        Enum('reset', 'setup', name='token_type'),
        nullable=False,
        default='reset'
    )
    expires_at = db.Column(db.DateTime, nullable=False)
    used_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_by_admin = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="password_reset_tokens")
    
    def is_valid(self):
        """Check if token is still valid for use"""
        if not self.is_active:
            return False, "Token has been deactivated"
        
        if datetime.now() > self.expires_at:
            return False, "Token has expired"
            
        return True, "Token is valid"

    if TYPE_CHECKING:
        def __init__(self, id: int | None = None, token: str = ..., user_id: int = ..., token_type: str = 'reset', expires_at: datetime = ..., used_at: datetime | None = None, is_active: bool = True, created_by_admin: bool = False, created_at: datetime | None = None): ...


class ReviewToken(db.Model):
    """Secure tokens for external reviewer access without authentication"""
    __tablename__ = 'review_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(64), nullable=False, unique=True, index=True)
    review_id = db.Column(db.Integer, ForeignKey('reviews.id'), nullable=False)
    reviewer_email = db.Column(db.String(120), nullable=False)
    
    # Token lifecycle
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    accessed_at = db.Column(db.DateTime, nullable=True)
    used_at = db.Column(db.DateTime, nullable=True)
    
    # Security
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    access_count = db.Column(db.Integer, default=0, nullable=False)
    max_access_count = db.Column(db.Integer, default=10, nullable=False)
    
    # Relationships
    review = relationship("Review", backref="tokens")
    
    def to_dict(self):
        return {
            "id": self.id,
            "token": self.token,
            "review_id": self.review_id,
            "reviewer_email": self.reviewer_email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "accessed_at": self.accessed_at.isoformat() if self.accessed_at else None,
            "used_at": self.used_at.isoformat() if self.used_at else None,
            "is_active": self.is_active,
            "access_count": self.access_count,
            "max_access_count": self.max_access_count
        }
    
    def is_valid(self):
        """Check if token is still valid for use"""
        if not self.is_active:
            return False, "Token has been deactivated"
        
        if datetime.now() > self.expires_at:
            return False, "Token has expired"
            
        if self.access_count >= self.max_access_count:
            return False, "Token access limit exceeded"
            
        return True, "Token is valid"

    if TYPE_CHECKING:
        def __init__(self, id: int | None = None, token: str = ..., review_id: int = ..., reviewer_email: str = ..., created_at: datetime | None = None, expires_at: datetime | None = None, accessed_at: datetime | None = None, used_at: datetime | None = None, is_active: bool = True, access_count: int = 0, max_access_count: int = 10): ...


class ReviewFeedback(db.Model):
    """Structured feedback and change suggestions from reviewers"""
    __tablename__ = 'review_feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(db.Integer, ForeignKey('reviews.id'), nullable=False)
    
    # Feedback categorization
    feedback_type = db.Column(
        Enum('general_comment', 'text_edit', 'text_addition', 'text_deletion', 
             'structural_change', 'technical_correction', 'style_suggestion', 
             name='feedback_type'),
        nullable=False,
        default='general_comment'
    )
    
    # Content targeting
    section_title = db.Column(db.String(200), nullable=True)
    page_number = db.Column(db.Integer, nullable=True)
    paragraph_number = db.Column(db.Integer, nullable=True)
    line_reference = db.Column(db.String(100), nullable=True)
    
    # Feedback content
    original_text = db.Column(db.Text, nullable=True)
    suggested_text = db.Column(db.Text, nullable=True)
    comment = db.Column(db.Text, nullable=False)
    rationale = db.Column(db.Text, nullable=True)
    
    # Priority and impact
    priority = db.Column(
        Enum('low', 'medium', 'high', 'critical', name='feedback_priority'),
        nullable=False,
        default='medium'
    )
    impact = db.Column(
        Enum('minor', 'moderate', 'major', name='feedback_impact'),
        nullable=False,
        default='moderate'
    )
    
    # Author response
    author_response = db.Column(db.Text, nullable=True)
    status = db.Column(
        Enum('pending', 'accepted', 'rejected', 'modified', name='feedback_status'),
        nullable=False,
        default='pending'
    )
    
    # Timing
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    responded_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    review = relationship("Review", backref="feedback_items")
    
    def to_dict(self):
        return {
            "id": self.id,
            "review_id": self.review_id,
            "feedback_type": self.feedback_type,
            "section_title": self.section_title,
            "page_number": self.page_number,
            "paragraph_number": self.paragraph_number,
            "line_reference": self.line_reference,
            "original_text": self.original_text,
            "suggested_text": self.suggested_text,
            "comment": self.comment,
            "rationale": self.rationale,
            "priority": self.priority,
            "impact": self.impact,
            "author_response": self.author_response,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "responded_at": self.responded_at.isoformat() if self.responded_at else None
        }


class ReviewSequence(db.Model):
    """Defines a multi-step review process for a topic."""
    __tablename__ = 'review_sequences'
    
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    status = db.Column(
        Enum('active', 'inactive', 'completed', name='sequence_status'),
        nullable=False,
        default='active'
    )
    
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    
    # Relationships
    topic = relationship('Topic', backref='review_sequences')
    steps = relationship('ReviewSequenceStep', back_populates='sequence', cascade='all, delete-orphan', order_by='ReviewSequenceStep.position')
    reviews = relationship('Review', back_populates='sequence')

    def to_dict(self, include_steps=False):
        data = {
            "id": self.id,
            "topic_id": self.topic_id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_steps:
            data['steps'] = [step.to_dict() for step in self.steps]
        return data

class ReviewSequenceStep(db.Model):
    """A single step within a review sequence."""
    __tablename__ = 'review_sequence_steps'
    
    id = db.Column(db.Integer, primary_key=True)
    sequence_id = db.Column(db.Integer, db.ForeignKey('review_sequences.id', ondelete='CASCADE'), nullable=False)
    position = db.Column(db.Integer, nullable=False)  # 0-based index
    
    # Who should perform this step
    reviewer_id = db.Column(db.Integer, db.ForeignKey('stakeholders.id'), nullable=True)
    reviewer_role = db.Column(db.String(100), nullable=True)  # e.g., 'SME', 'Legal'
    
    # Step details
    name = db.Column(db.String(200), nullable=False)
    instructions = db.Column(db.Text, nullable=True)
    
    # Relationships
    sequence = relationship('ReviewSequence', back_populates='steps')
    reviewer = relationship('Stakeholder')

    def to_dict(self):
        return {
            "id": self.id,
            "sequence_id": self.sequence_id,
            "position": self.position,
            "reviewer_id": self.reviewer_id,
            "reviewer_name": self.reviewer.name if self.reviewer else None,
            "reviewer_role": self.reviewer_role,
            "name": self.name,
            "instructions": self.instructions,
        }


class FeedbackReport(db.Model):
    """Model for storing user feedback and bug reports"""
    __tablename__ = 'feedback_reports'

    id = db.Column(db.Integer, primary_key=True)
    report_type = db.Column(
        db.String(20),
        nullable=False,
        default='other'
    )
    page = db.Column(db.String(256), nullable=True)
    component = db.Column(db.String(128), nullable=True)
    user_contact = db.Column(db.String(120), nullable=True)
    message = db.Column(db.Text, nullable=False)
    metadata_json = db.Column(db.Text, nullable=True)  # For storing extra JSON data
    status = db.Column(
        db.String(20),
        nullable=False,
        default='new'
    )
    created_at = db.Column(
        db.DateTime,
        server_default=func.now(),
        nullable=False
    )

    def to_dict(self):
        return {
            "id": self.id,
            "report_type": self.report_type,
            "page": self.page,
            "component": self.component,
            "user_contact": self.user_contact,
            "message": self.message,
            "metadata": self.metadata_json,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }