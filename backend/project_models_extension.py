# Project Management Models Extension for StructuredDocs

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum, ForeignKey, func, Table, Column, Integer
from sqlalchemy.orm import relationship

# Additional models to add to models.py

class Project(db.Model):
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
    reviews = relationship('TopicReview', back_populates='project')

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
                "collections_count": len(self.collections),
                "active_reviews_count": len([r for r in self.reviews if r.status == 'pending'])
            })
        
        return data


class ProjectStakeholder(db.Model):
    __tablename__ = 'project_stakeholders'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(
        db.Integer,
        db.ForeignKey('projects.id', ondelete='CASCADE'),
        nullable=False
    )
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    role = db.Column(
        Enum('project_manager', 'subject_matter_expert', 'reviewer', 'stakeholder', name='stakeholder_role'),
        nullable=False,
        default='reviewer',
        server_default='reviewer'
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

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "can_review": self.can_review,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class ProjectMilestone(db.Model):
    __tablename__ = 'project_milestones'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(
        db.Integer,
        db.ForeignKey('projects.id', ondelete='CASCADE'),
        nullable=False
    )
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.Date, nullable=True)
    status = db.Column(
        Enum('pending', 'in_progress', 'completed', 'delayed', name='milestone_status'),
        nullable=False,
        default='pending',
        server_default='pending'
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
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "status": self.status,
            "completion_date": self.completion_date.isoformat() if self.completion_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class TopicReview(db.Model):
    __tablename__ = 'topic_reviews'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(
        db.Integer,
        db.ForeignKey('projects.id', ondelete='CASCADE'),
        nullable=False
    )
    topic_id = db.Column(
        db.Integer,
        db.ForeignKey('topics.id', ondelete='CASCADE'),
        nullable=False
    )
    assigned_stakeholder_id = db.Column(
        db.Integer,
        db.ForeignKey('project_stakeholders.id'),
        nullable=False
    )
    status = db.Column(
        Enum('pending', 'in_review', 'approved', 'rejected', 'revision_requested', name='review_status'),
        nullable=False,
        default='pending',
        server_default='pending'
    )
    due_date = db.Column(db.Date, nullable=True)
    submitted_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    submitter_notes = db.Column(db.Text, nullable=True)
    reviewer_comments = db.Column(db.Text, nullable=True)
    
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
    project = relationship('Project', back_populates='reviews')
    topic = relationship('Topic')
    assigned_stakeholder = relationship('ProjectStakeholder')

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "topic_id": self.topic_id,
            "topic": self.topic.to_dict() if self.topic else None,
            "assigned_stakeholder_id": self.assigned_stakeholder_id,
            "assigned_stakeholder": self.assigned_stakeholder.to_dict() if self.assigned_stakeholder else None,
            "status": self.status,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "submitter_notes": self.submitter_notes,
            "reviewer_comments": self.reviewer_comments,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


# Updates to existing models:

# Add to Collection model:
# project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
# project = relationship('Project', back_populates='collections')

# Add to Topic model:
# current_review_id = db.Column(db.Integer, db.ForeignKey('topic_reviews.id'), nullable=True)
# current_review = relationship('TopicReview', foreign_keys=[current_review_id])
