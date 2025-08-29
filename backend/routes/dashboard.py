from flask import Blueprint, jsonify
from sqlalchemy import func
from datetime import datetime, timedelta

from ..models import db, Topic, Collection, Project, Task, Review, User, Tag, ProjectMilestone as Milestone, ReviewFeedback as Feedback, Notification

bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

@bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Gathers and returns a comprehensive set of statistics for the admin dashboard.
    """
    try:
        # Key Metrics
        total_projects = db.session.query(func.count(Project.id)).scalar()
        total_collections = db.session.query(func.count(Collection.id)).scalar()
        total_topics = db.session.query(func.count(Topic.id)).scalar()
        total_users = db.session.query(func.count(User.id)).scalar()

        # User Stats
        active_users = db.session.query(func.count(User.id)).filter(User.active == True).scalar()
        inactive_users = total_users - active_users
        
        # Content Stats
        draft_topics = db.session.query(func.count(Topic.id)).filter(Topic.status == 'draft').scalar()
        published_topics = db.session.query(func.count(Topic.id)).filter(Topic.status == 'published').scalar()
        
        # Review Stats
        pending_reviews = db.session.query(func.count(Review.id)).filter(Review.status == 'pending').scalar()
        completed_reviews = db.session.query(func.count(Review.id)).filter(Review.status == 'completed').scalar()

        # Task Stats
        total_tasks = db.session.query(func.count(Task.id)).scalar()
        completed_tasks = db.session.query(func.count(Task.id)).filter(Task.status == 'completed').scalar()

        # Database Metrics
        total_tags = db.session.query(func.count(Tag.id)).scalar()
        total_milestones = db.session.query(func.count(Milestone.id)).scalar()
        total_feedback = db.session.query(func.count(Feedback.id)).scalar()
        
        # System Overview
        unread_notifications = db.session.query(func.count(Notification.id)).filter(Notification.read == False).scalar()
        
        # Recent Activity (e.g., last 7 days)
        one_week_ago = datetime.utcnow() - timedelta(days=7)
        new_users_weekly = db.session.query(func.count(User.id)).filter(User.created_at >= one_week_ago).scalar()
        new_topics_weekly = db.session.query(func.count(Topic.id)).filter(Topic.created_at >= one_week_ago).scalar()

        stats = {
            'keyMetrics': {
                'totalProjects': total_projects,
                'totalCollections': total_collections,
                'totalTopics': total_topics,
                'totalUsers': total_users,
            },
            'userStats': {
                'totalUsers': total_users,
                'activeUsers': active_users,
                'inactiveUsers': inactive_users,
                'newUsersWeekly': new_users_weekly,
            },
            'contentStats': {
                'totalTopics': total_topics,
                'draftTopics': draft_topics,
                'publishedTopics': published_topics,
                'newTopicsWeekly': new_topics_weekly,
            },
            'reviewAndTaskStats': {
                'pendingReviews': pending_reviews,
                'completedReviews': completed_reviews,
                'totalTasks': total_tasks,
                'completedTasks': completed_tasks,
            },
            'databaseMetrics': {
                'projects': total_projects,
                'collections': total_collections,
                'topics': total_topics,
                'users': total_users,
                'reviews': pending_reviews + completed_reviews,
                'tasks': total_tasks,
                'tags': total_tags,
                'milestones': total_milestones,
                'feedback': total_feedback,
                'notifications': unread_notifications + db.session.query(func.count(Notification.id)).filter(Notification.read == True).scalar(),
            },
            'systemOverview': {
                'databaseSize': 'N/A', # Placeholder, requires specific DB query
                'unreadNotifications': unread_notifications,
                'logCount': 0, # Placeholder, requires log file analysis
            }
        }
        
        return jsonify(stats)

    except Exception as e:
        # Log the error for debugging
        print(f"Error in get_stats: {e}")
        return jsonify({'error': 'An error occurred while fetching dashboard statistics.'}), 500


@bp.route('/pending-actions', methods=['GET'])
def get_pending_actions():
    # Dummy data, replace with real queries as needed
    return jsonify([
        {'id': 1, 'type': 'review', 'description': 'Review project X', 'link': '/projects/1/review'},
        {'id': 2, 'type': 'approval', 'description': 'Approve collection Y', 'link': '/collections/2/approve'}
    ])
