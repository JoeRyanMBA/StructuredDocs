"""add performance indexes to core tables

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2025-01-02 00:00:00.000000

"""
from alembic import op

revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    # Collections
    op.create_index('ix_collections_parent_id', 'collections', ['parent_id'])
    op.create_index('ix_collections_project_id', 'collections', ['project_id'])
    op.create_index('ix_collections_archived', 'collections', ['archived'])

    # Topics
    op.create_index('ix_topics_created_at', 'topics', ['created_at'])
    op.create_index('ix_topics_status', 'topics', ['status'])
    op.create_index('ix_topics_updated_at', 'topics', ['updated_at'])

    # Publications
    op.create_index('ix_publications_created_at', 'publications', ['created_at'])
    op.create_index('ix_publications_title', 'publications', ['title'])

    # Publication nodes
    op.create_index('ix_pub_nodes_publication_id', 'publication_nodes', ['publication_id'])
    op.create_index('ix_pub_nodes_parent_id', 'publication_nodes', ['parent_id'])

    # Reviews
    op.create_index('ix_reviews_topic_id', 'reviews', ['topic_id'])
    op.create_index('ix_reviews_status', 'reviews', ['status'])
    op.create_index('ix_reviews_reviewer_id', 'reviews', ['reviewer_id'])
    op.create_index('ix_reviews_requested_at', 'reviews', ['requested_at'])


def downgrade():
    op.drop_index('ix_reviews_requested_at', 'reviews')
    op.drop_index('ix_reviews_reviewer_id', 'reviews')
    op.drop_index('ix_reviews_status', 'reviews')
    op.drop_index('ix_reviews_topic_id', 'reviews')
    op.drop_index('ix_pub_nodes_parent_id', 'publication_nodes')
    op.drop_index('ix_pub_nodes_publication_id', 'publication_nodes')
    op.drop_index('ix_publications_title', 'publications')
    op.drop_index('ix_publications_created_at', 'publications')
    op.drop_index('ix_topics_updated_at', 'topics')
    op.drop_index('ix_topics_status', 'topics')
    op.drop_index('ix_topics_created_at', 'topics')
    op.drop_index('ix_collections_archived', 'collections')
    op.drop_index('ix_collections_project_id', 'collections')
    op.drop_index('ix_collections_parent_id', 'collections')
