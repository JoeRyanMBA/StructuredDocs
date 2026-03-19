from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from sqlalchemy import func
from datetime import datetime, timedelta

from ..models import db, Topic, Collection, Project, Task, Review, User, Tag, ProjectMilestone as Milestone, ReviewFeedback as Feedback, Notification, ImportDocument, Stakeholder

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
        fifteen_min_ago = datetime.utcnow() - timedelta(minutes=15)
        online_now = (
            db.session.query(func.count(User.id)).filter(User.last_seen >= fifteen_min_ago).scalar()
            if hasattr(User, 'last_seen') else 0
        )
        
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
                'onlineNow': online_now,
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
    """Return real pending actions for the authenticated user."""
    actions = []

    # Resolve current user via optional JWT
    current_user = None
    current_stakeholder = None
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        if user_id:
            current_user = User.query.get(user_id)
            if current_user:
                current_stakeholder = Stakeholder.query.filter_by(email=current_user.email).first()
    except Exception:
        pass

    counter = 1  # synthetic id for each action item

    # --- Reviews assigned to me (as reviewer) ---
    if current_stakeholder:
        assigned_reviews = (
            Review.query
            .filter(
                Review.reviewer_id == current_stakeholder.id,
                Review.status.in_(['pending', 'in_progress'])
            )
            .order_by(Review.due_date.asc().nullslast(), Review.requested_at.asc())
            .limit(10)
            .all()
        )
        for r in assigned_reviews:
            topic_title = r.topic.title if r.topic else f'Topic #{r.topic_id}'
            due_str = f' · Due {r.due_date.strftime("%b %d")}' if r.due_date else ''
            actions.append({
                'id': f'review-{counter}',
                'type': 'review',
                'title': f'Review: {topic_title}',
                'description': f'Requested by {r.requester.name}{due_str} · Priority: {r.priority}',
                'created_at': r.requested_at.isoformat() if r.requested_at else None,
                'link': f'/reviews',
            })
            counter += 1

    # --- Feedback awaiting my response (as author) ---
    if current_stakeholder:
        feedback_reviews = (
            db.session.query(Review)
            .join(Feedback, Feedback.review_id == Review.id)
            .filter(
                Review.requested_by == current_stakeholder.id,
                Feedback.status == 'pending'
            )
            .distinct()
            .limit(10)
            .all()
        )
        for r in feedback_reviews:
            topic_title = r.topic.title if r.topic else f'Topic #{r.topic_id}'
            pending_count = sum(1 for f in r.feedback_items if f.status == 'pending')
            actions.append({
                'id': f'feedback-{counter}',
                'type': 'feedback',
                'title': f'Respond to feedback: {topic_title}',
                'description': f'{pending_count} unresolved item{"s" if pending_count != 1 else ""} from {r.reviewer.name}',
                'created_at': r.requested_at.isoformat() if r.requested_at else None,
                'link': f'/reviews',
            })
            counter += 1

    # --- Staged imports awaiting commit ---
    staged_imports = (
        ImportDocument.query
        .filter_by(status='staging')
        .order_by(ImportDocument.created_at.desc())
        .limit(5)
        .all()
    )
    for doc in staged_imports:
        actions.append({
            'id': f'import-{counter}',
            'type': 'import',
            'title': f'Import pending: {doc.filename}',
            'description': f'{len(doc.items)} topic{"s" if len(doc.items) != 1 else ""} staged · Step: {doc.review_step}',
            'created_at': doc.created_at.isoformat() if doc.created_at else None,
            'link': f'/import/staging/{doc.id}',
        })
        counter += 1

    return jsonify(actions)
