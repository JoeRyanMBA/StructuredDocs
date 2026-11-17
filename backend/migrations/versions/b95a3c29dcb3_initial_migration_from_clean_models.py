"""Initial migration from clean models

Revision ID: b95a3c29dcb3
Revises: 
Create Date: 2025-08-12 19:46:16.842869

"""
from alembic import op
import sqlalchemy as sa


# A pre-Alembic database may already contain the complete baseline schema.
_BASELINE_COLUMNS = {
    'import_documents': {
        'id', 'filename', 'source_type', 'status', 'review_step', 'created_at',
        'reviewed_at', 'reviewer',
    },
    'links': {
        'id', 'title', 'url', 'description', 'reference_code', 'link_type',
        'is_internal', 'is_active', 'created_at', 'updated_at', 'created_by',
    },
    'notifications': {'id', 'user_id', 'title', 'message', 'link', 'type', 'date', 'read'},
    'projects': {
        'id', 'name', 'description', 'status', 'start_date', 'target_completion',
        'created_at', 'updated_at',
    },
    'publications': {'id', 'title', 'description', 'created_at'},
    'stakeholders': {
        'id', 'name', 'email', 'title', 'organization', 'department', 'phone',
        'expertise_areas', 'bio', 'active', 'created_at', 'updated_at',
    },
    'topics': {'id', 'title', 'content', 'frontmatter', 'status', 'created_at', 'updated_at'},
    'users': {'id', 'name', 'email', 'password_hash', 'role', 'active', 'created_at'},
    'collections': {
        'id', 'name', 'description', 'form_number', 'parent_id', 'project_id',
        'position', 'created_at', 'updated_at',
    },
    'import_images': {
        'id', 'document_id', 'filename', 'original_name', 'public_url', 'backend_path',
        'frontend_path', 'width', 'height', 'format', 'file_size', 'mime_type',
        'created_at',
    },
    'import_items': {'id', 'document_id', 'heading_order', 'title', 'content', 'committed_topic'},
    'project_milestones': {
        'id', 'project_id', 'name', 'description', 'date', 'status',
        'completion_date', 'created_at',
    },
    'project_stakeholders': {
        'id', 'project_id', 'stakeholder_id', 'role', 'can_review', 'notes',
        'created_at',
    },
    'publication_nodes': {'id', 'publication_id', 'topic_id', 'parent_id', 'position'},
    'topic_links': {'id', 'topic_id', 'link_id', 'context', 'position', 'created_at'},
    'collection_topic_tree': {'collection_id', 'topic_id', 'parent_topic_id', 'position'},
    'tasks': {
        'id', 'title', 'description', 'status', 'priority', 'due_date', 'completed_at',
        'project_id', 'collection_id', 'topic_id', 'assigned_to', 'created_by', 'tags',
        'created_at', 'updated_at',
    },
}
_BASELINE_PRIMARY_KEYS = {
    **{table: {'id'} for table in _BASELINE_COLUMNS},
    'collection_topic_tree': set(),
}
_BASELINE_UNIQUE_CONSTRAINTS = {
    'links': {('reference_code',)},
    'stakeholders': {('email',)},
    'users': {('email',)},
    'collections': {('form_number',)},
    'project_stakeholders': {('project_id', 'stakeholder_id')},
    'topic_links': {('topic_id', 'link_id')},
}
_BASELINE_FOREIGN_KEYS = {
    'collections': {
        (('parent_id',), 'collections', ('id',)),
        (('project_id',), 'projects', ('id',)),
    },
    'import_images': {(('document_id',), 'import_documents', ('id',))},
    'import_items': {
        (('committed_topic',), 'topics', ('id',)),
        (('document_id',), 'import_documents', ('id',)),
    },
    'project_milestones': {(('project_id',), 'projects', ('id',))},
    'project_stakeholders': {
        (('project_id',), 'projects', ('id',)),
        (('stakeholder_id',), 'stakeholders', ('id',)),
    },
    'publication_nodes': {
        (('parent_id',), 'publication_nodes', ('id',)),
        (('publication_id',), 'publications', ('id',)),
        (('topic_id',), 'topics', ('id',)),
    },
    'topic_links': {
        (('link_id',), 'links', ('id',)),
        (('topic_id',), 'topics', ('id',)),
    },
    'collection_topic_tree': {
        (('collection_id',), 'collections', ('id',)),
        (('parent_topic_id',), 'topics', ('id',)),
        (('topic_id',), 'topics', ('id',)),
    },
    'tasks': {
        (('collection_id',), 'collections', ('id',)),
        (('project_id',), 'projects', ('id',)),
        (('topic_id',), 'topics', ('id',)),
    },
}
_BASELINE_ENUMS = {
    'source_type_enum': {'word', 'markdown'},
    'import_status_enum': {'staging', 'approved', 'rejected'},
    'import_review_step': {'pending', 'sme_approved', 'final_approved'},
    'link_type_enum': {
        'form', 'document', 'website', 'policy', 'procedure', 'regulation', 'other',
    },
    'project_status': {'planning', 'active', 'review', 'completed', 'on_hold'},
    'topic_status': {
        'draft', 'pending_review', 'published', 'rejected', 'archived',
    },
    'user_role': {'author', 'reviewer', 'admin'},
    'milestone_status': {'planned', 'in-progress', 'completed', 'overdue'},
    'stakeholder_role': {'project_manager', 'subject_matter_expert', 'reviewer', 'stakeholder', 'sponsor'},
    'task_status': {'todo', 'in_progress', 'review', 'completed', 'cancelled'},
    'task_priority': {'low', 'medium', 'high', 'urgent'},
}
_BASELINE_ENUM_COLUMNS = {
    'import_documents': {
        'source_type': 'source_type_enum',
        'status': 'import_status_enum',
        'review_step': 'import_review_step',
    },
    'links': {'link_type': 'link_type_enum'},
    'projects': {'status': 'project_status'},
    'topics': {'status': 'topic_status'},
    'users': {'role': 'user_role'},
    'project_milestones': {'status': 'milestone_status'},
    'project_stakeholders': {'role': 'stakeholder_role'},
    'tasks': {'status': 'task_status', 'priority': 'task_priority'},
}


def _baseline_schema_is_present(bind):
    inspector = sa.inspect(bind)
    if not set(_BASELINE_COLUMNS).issubset(inspector.get_table_names()):
        return False

    for table, expected_columns in _BASELINE_COLUMNS.items():
        existing_columns = {column['name'] for column in inspector.get_columns(table)}
        if not expected_columns.issubset(existing_columns):
            return False
        primary_key = set(inspector.get_pk_constraint(table).get('constrained_columns') or [])
        if primary_key != _BASELINE_PRIMARY_KEYS[table]:
            return False
        existing_unique = {
            tuple(constraint['column_names'])
            for constraint in inspector.get_unique_constraints(table)
        }
        if not _BASELINE_UNIQUE_CONSTRAINTS.get(table, set()).issubset(existing_unique):
            return False
        existing_foreign_keys = {
            (
                tuple(constraint['constrained_columns']),
                constraint['referred_table'],
                tuple(constraint['referred_columns']),
            )
            for constraint in inspector.get_foreign_keys(table)
        }
        if not _BASELINE_FOREIGN_KEYS.get(table, set()).issubset(existing_foreign_keys):
            return False

    if bind.dialect.name == 'postgresql':
        enums = {enum['name']: set(enum['labels']) for enum in inspector.get_enums()}
        if any(
            not labels.issubset(enums.get(name, set()))
            for name, labels in _BASELINE_ENUMS.items()
        ):
            return False
        for table, columns in _BASELINE_ENUM_COLUMNS.items():
            types = {column['name']: column['type'] for column in inspector.get_columns(table)}
            if any(
                getattr(types.get(column), 'name', None) != enum
                for column, enum in columns.items()
            ):
                return False

    return True


# revision identifiers, used by Alembic.
revision = 'b95a3c29dcb3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    existing_tables = set(sa.inspect(bind).get_table_names())
    baseline_tables = set(_BASELINE_COLUMNS)
    if existing_tables & baseline_tables:
        if _baseline_schema_is_present(bind):
            return
        raise RuntimeError(
            'The initial migration found a partial pre-existing schema. '
            'Reconcile the database schema before applying this revision.'
        )

    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('import_documents',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('filename', sa.String(length=256), nullable=False),
    sa.Column('source_type', sa.Enum('word', 'markdown', name='source_type_enum'), nullable=False),
    sa.Column('status', sa.Enum('staging', 'approved', 'rejected', name='import_status_enum'), server_default='staging', nullable=False),
    sa.Column('review_step', sa.Enum('pending', 'sme_approved', 'final_approved', name='import_review_step'), server_default='pending', nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('reviewed_at', sa.DateTime(), nullable=True),
    sa.Column('reviewer', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('links',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('url', sa.String(length=512), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('reference_code', sa.String(length=100), nullable=True),
    sa.Column('link_type', sa.Enum('form', 'document', 'website', 'policy', 'procedure', 'regulation', 'other', name='link_type_enum'), nullable=False),
    sa.Column('is_internal', sa.Boolean(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('created_by', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('reference_code')
    )
    op.create_table('notifications',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('title', sa.String(length=128), nullable=False),
    sa.Column('message', sa.String(length=256), nullable=False),
    sa.Column('link', sa.String(length=256), nullable=True),
    sa.Column('type', sa.String(length=32), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.Column('read', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('projects',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('status', sa.Enum('planning', 'active', 'review', 'completed', 'on_hold', name='project_status'), server_default='planning', nullable=False),
    sa.Column('start_date', sa.Date(), nullable=True),
    sa.Column('target_completion', sa.Date(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('publications',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('stakeholders',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=True),
    sa.Column('organization', sa.String(length=200), nullable=True),
    sa.Column('department', sa.String(length=200), nullable=True),
    sa.Column('phone', sa.String(length=20), nullable=True),
    sa.Column('expertise_areas', sa.Text(), nullable=True),
    sa.Column('bio', sa.Text(), nullable=True),
    sa.Column('active', sa.Boolean(), server_default='1', nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('topics',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('frontmatter', sa.Text(), nullable=True),
    sa.Column('status', sa.Enum('draft', 'pending_review', 'published', 'rejected', 'archived', name='topic_status'), server_default='draft', nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=True),
    sa.Column('role', sa.Enum('author', 'reviewer', 'admin', name='user_role'), server_default='author', nullable=False),
    sa.Column('active', sa.Boolean(), server_default='1', nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('collections',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('form_number', sa.String(length=100), nullable=False),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('project_id', sa.Integer(), nullable=True),
    sa.Column('position', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['parent_id'], ['collections.id'], ),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('form_number')
    )
    op.create_table('import_images',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('document_id', sa.Integer(), nullable=False),
    sa.Column('filename', sa.String(length=256), nullable=False),
    sa.Column('original_name', sa.String(length=256), nullable=False),
    sa.Column('public_url', sa.String(length=512), nullable=False),
    sa.Column('backend_path', sa.String(length=512), nullable=False),
    sa.Column('frontend_path', sa.String(length=512), nullable=False),
    sa.Column('width', sa.Integer(), nullable=True),
    sa.Column('height', sa.Integer(), nullable=True),
    sa.Column('format', sa.String(length=32), nullable=True),
    sa.Column('file_size', sa.Integer(), nullable=True),
    sa.Column('mime_type', sa.String(length=64), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['document_id'], ['import_documents.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('import_items',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('document_id', sa.Integer(), nullable=False),
    sa.Column('heading_order', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('committed_topic', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['committed_topic'], ['topics.id'], ),
    sa.ForeignKeyConstraint(['document_id'], ['import_documents.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('project_milestones',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('date', sa.Date(), nullable=True),
    sa.Column('status', sa.Enum('planned', 'in-progress', 'completed', 'overdue', name='milestone_status'), server_default='planned', nullable=False),
    sa.Column('completion_date', sa.Date(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('project_stakeholders',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('stakeholder_id', sa.Integer(), nullable=False),
    sa.Column('role', sa.Enum('project_manager', 'subject_matter_expert', 'reviewer', 'stakeholder', 'sponsor', name='stakeholder_role'), server_default='stakeholder', nullable=False),
    sa.Column('can_review', sa.Boolean(), server_default='1', nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['stakeholder_id'], ['stakeholders.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('project_id', 'stakeholder_id', name='unique_project_stakeholder')
    )
    op.create_table('publication_nodes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('publication_id', sa.Integer(), nullable=False),
    sa.Column('topic_id', sa.Integer(), nullable=False),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('position', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['parent_id'], ['publication_nodes.id'], ),
    sa.ForeignKeyConstraint(['publication_id'], ['publications.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('topic_links',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('topic_id', sa.Integer(), nullable=False),
    sa.Column('link_id', sa.Integer(), nullable=False),
    sa.Column('context', sa.String(length=200), nullable=True),
    sa.Column('position', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['link_id'], ['links.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('topic_id', 'link_id', name='unique_topic_link')
    )
    op.create_table('collection_topic_tree',
    sa.Column('collection_id', sa.Integer(), nullable=True),
    sa.Column('topic_id', sa.Integer(), nullable=True),
    sa.Column('parent_topic_id', sa.Integer(), nullable=True),
    sa.Column('position', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['collection_id'], ['collections.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['parent_topic_id'], ['topics.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], ondelete='CASCADE')
    )
    op.create_table('tasks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('status', sa.Enum('todo', 'in_progress', 'review', 'completed', 'cancelled', name='task_status'), server_default='todo', nullable=False),
    sa.Column('priority', sa.Enum('low', 'medium', 'high', 'urgent', name='task_priority'), server_default='medium', nullable=False),
    sa.Column('due_date', sa.Date(), nullable=True),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.Column('project_id', sa.Integer(), nullable=True),
    sa.Column('collection_id', sa.Integer(), nullable=True),
    sa.Column('topic_id', sa.Integer(), nullable=True),
    sa.Column('assigned_to', sa.String(length=100), nullable=True),
    sa.Column('created_by', sa.String(length=100), nullable=True),
    sa.Column('tags', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['collection_id'], ['collections.id'], ),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tasks')
    op.drop_table('collection_topic_tree')
    op.drop_table('topic_links')
    op.drop_table('publication_nodes')
    op.drop_table('project_stakeholders')
    op.drop_table('project_milestones')
    op.drop_table('import_items')
    op.drop_table('import_images')
    op.drop_table('collections')
    op.drop_table('users')
    op.drop_table('topics')
    op.drop_table('stakeholders')
    op.drop_table('publications')
    op.drop_table('projects')
    op.drop_table('notifications')
    op.drop_table('links')
    op.drop_table('import_documents')
    # ### end Alembic commands ###
