# backend/routes/__init__.py

# Import all route modules to make them available for blueprint registration
from . import admin
from . import collections
from . import dashboard
from . import feedback
from . import images
from . import import_handler
from . import links
from . import metrics
from . import milestones
from . import notifications
from . import projects
from . import publications
from . import review_tokens
from . import reviews
from . import sequences
from . import stakeholders
from . import tags
from . import tasks
from . import topics
from . import users

# Make them available for import
__all__ = [
    'admin',
    'collections',
    'dashboard',
    'feedback',
    'images',
    'import_handler',
    'links',
    'metrics',
    'milestones',
    'notifications',
    'projects',
    'publications',
    'review_tokens',
    'reviews',
    'sequences',
    'stakeholders',
    'tags',
    'tasks',
    'topics',
    'users'
]