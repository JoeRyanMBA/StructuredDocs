# backend/models.py

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum, ForeignKey, func
from sqlalchemy.orm import relationship

db = SQLAlchemy()


class Topic(db.Model):
    __tablename__ = 'topics'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=True)

    # Draft → Published → Archived
    status = db.Column(
        Enum('draft', 'published', 'archived', name='topic_status'),
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
            "reviewer": self.reviewer
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