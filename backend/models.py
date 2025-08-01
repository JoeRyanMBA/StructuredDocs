# backend/models.py

from datetime import datetime
from sqlalchemy import Enum, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy import Table, Column, Integer
from . import db

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
    position  = db.Column(db.Integer, nullable=False, default=0)

    # Nested children collections
    children = relationship(
        'Collection',
        backref=db.backref('parent', remote_side=[id]),
        cascade='all, delete-orphan'
    )

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
            'parentId': self.parent_id
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

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

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