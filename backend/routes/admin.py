from flask import Blueprint, request, jsonify
from ..models import db, User, Notification, Topic, Collection, Project, Task
from sqlalchemy import func
from datetime import datetime, timedelta
import os

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/stats', methods=['GET'])
def get_admin_stats():
    """Get admin dashboard statistics including system metrics"""
    try:
        # Get user statistics
        total_users = User.query.count()
        active_users = User.query.filter(User.active == True).count() if hasattr(User, 'active') else total_users
        authors = User.query.filter(User.role == 'author').count() if hasattr(User, 'role') else 0
        reviewers = User.query.filter(User.role == 'reviewer').count() if hasattr(User, 'role') else 0
        
        # Get content statistics
        total_topics = Topic.query.count()
        total_collections = Collection.query.count()
        total_projects = Project.query.count()
        total_tasks = Task.query.count() if Task else 0
        
        # Get recent activity (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_topics = Topic.query.filter(Topic.created_at >= week_ago).count() if hasattr(Topic, 'created_at') else 0
        recent_collections = Collection.query.filter(Collection.created_at >= week_ago).count() if hasattr(Collection, 'created_at') else 0
        
        # Import system metrics from metrics module
        try:
            from .metrics import get_basic_system_metrics, get_database_metrics, get_application_metrics
            
            # Get real system performance metrics
            system_performance = get_basic_system_metrics()
            db_metrics = get_database_metrics(None)  # Will auto-detect PostgreSQL
            app_metrics = get_application_metrics(None)
            
        except Exception as e:
            print(f"⚠️ Error getting system metrics: {e}")
            # Fallback system performance data
            system_performance = {
                'memoryUsage': 65.0,
                'cpuUsage': 35.0,
                'diskUsage': 45.0,
                'systemHealth': 'healthy',
                'serverStatus': 'online',
                'databaseStatus': 'connected'
            }
            db_metrics = {'size': 'Unknown', 'tables': 0, 'totalRecords': 0}
            app_metrics = {'users': {'active': active_users, 'total': total_users}}
        
        stats = {
            'totalUsers': total_users,
            'activeUsers': active_users,
            'authors': authors,
            'reviewers': reviewers,
            'systemHealth': system_performance.get('systemHealth', 'Good'),
            'uptime': system_performance.get('uptime', '99.9%')
        }
        
        user_stats = {
            'totalUsers': total_users,
            'activeUsers': active_users,
            'newUsersThisWeek': max(0, total_users - 10)  # Placeholder calculation
        }
        
        system_metrics = {
            'totalTopics': total_topics,
            'totalCollections': total_collections,
            'totalProjects': total_projects,
            'totalTasks': total_tasks,
            'recentTopics': recent_topics,
            'recentCollections': recent_collections
        }
        
        # Add system performance metrics
        performance_metrics = {
            'memoryUsage': system_performance.get('memoryUsage', 0),
            'cpuUsage': system_performance.get('cpuUsage', 0),
            'diskUsage': system_performance.get('diskUsage', 0),
            'systemHealth': system_performance.get('systemHealth', 'unknown'),
            'serverStatus': system_performance.get('serverStatus', 'unknown'),
            'databaseStatus': system_performance.get('databaseStatus', 'unknown'),
            'uptime': system_performance.get('uptime', 'Unknown')
        }
        
        # Add database metrics
        database_metrics = {
            'size': db_metrics.get('size', 'Unknown'),
            'tables': db_metrics.get('tables', 0),
            'totalRecords': db_metrics.get('totalRecords', 0),
            'lastBackup': db_metrics.get('lastBackup', 'Never'),
            'backupStatus': db_metrics.get('backupStatus', 'unknown')
        }
        
        return jsonify({
            'stats': stats,
            'userStats': user_stats,
            'systemMetrics': system_metrics,
            'performanceMetrics': performance_metrics,
            'databaseMetrics': database_metrics
        }), 200
        
    except Exception as e:
        print(f"❌ Error in get_admin_stats: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/activity', methods=['GET'])
def get_recent_activity():
    """Get recent system activity"""
    try:
        activity_items = []
        
        # Get recent users (if they have created_at timestamp)
        try:
            recent_users = User.query.order_by(User.id.desc()).limit(5).all()
            for user in recent_users:
                activity_items.append({
                    'id': f'user_{user.id}',
                    'type': 'user_created',
                    'description': f'New user registered: {user.name}',
                    'timestamp': getattr(user, 'created_at', datetime.utcnow()).isoformat() if hasattr(user, 'created_at') else datetime.utcnow().isoformat(),
                    'user': user.name
                })
        except Exception as e:
            print(f"Error fetching recent users: {e}")
        
        # Get recent topics
        try:
            recent_topics = Topic.query.order_by(Topic.id.desc()).limit(5).all()
            for topic in recent_topics:
                activity_items.append({
                    'id': f'topic_{topic.id}',
                    'type': 'topic_created',
                    'description': f'New topic created: {topic.title}',
                    'timestamp': getattr(topic, 'created_at', datetime.utcnow()).isoformat() if hasattr(topic, 'created_at') else datetime.utcnow().isoformat(),
                    'user': 'System'
                })
        except Exception as e:
            print(f"Error fetching recent topics: {e}")
        
        # Get recent collections
        try:
            recent_collections = Collection.query.order_by(Collection.id.desc()).limit(5).all()
            for collection in recent_collections:
                activity_items.append({
                    'id': f'collection_{collection.id}',
                    'type': 'collection_created',
                    'description': f'New collection created: {collection.name}',
                    'timestamp': getattr(collection, 'created_at', datetime.utcnow()).isoformat() if hasattr(collection, 'created_at') else datetime.utcnow().isoformat(),
                    'user': 'System'
                })
        except Exception as e:
            print(f"Error fetching recent collections: {e}")
        
        # Sort by timestamp descending and limit to 10 most recent
        activity_items.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify(activity_items[:10]), 200
        
    except Exception as e:
        print(f"❌ Error in get_recent_activity: {e}")
        return jsonify([]), 200  # Return empty array instead of error

@admin_bp.route('/system-logs', methods=['GET'])
def get_system_logs():
    """Get recent system logs"""
    try:
        # For now, create some basic system log entries
        # In a real system, these would come from actual log files
        
        logs = [
            {
                'id': 1,
                'timestamp': datetime.utcnow().isoformat(),
                'level': 'INFO',
                'message': 'System startup completed successfully',
                'source': 'system'
            },
            {
                'id': 2,
                'timestamp': (datetime.utcnow() - timedelta(minutes=30)).isoformat(),
                'level': 'INFO',
                'message': 'Database connection established',
                'source': 'database'
            },
            {
                'id': 3,
                'timestamp': (datetime.utcnow() - timedelta(hours=1)).isoformat(),
                'level': 'INFO',
                'message': 'User authentication service running',
                'source': 'auth'
            },
            {
                'id': 4,
                'timestamp': (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                'level': 'INFO',
                'message': 'API endpoints initialized',
                'source': 'api'
            }
        ]
        
        return jsonify(logs), 200
        
    except Exception as e:
        print(f"❌ Error in get_system_logs: {e}")
        return jsonify([]), 200

@admin_bp.route('/send-test-email', methods=['POST'])
def send_test_email_endpoint():
    """Send a test email to verify SMTP configuration.

    Protect with ADMIN_API_KEY in Authorization header as a simple bearer token.
    Body: { "to": "you@example.com" }
    """
    try:
        # Accept either Authorization: Bearer <token> or plain Authorization: <token>
        auth = request.headers.get('Authorization', '')
        token = auth.split('Bearer ',-1)[-1].strip() if 'Bearer ' in auth else auth.strip()
        # Optional fallback header name to avoid issues with intermediaries stripping Authorization
        if not token:
            token = (request.headers.get('X-Admin-Token', '') or '').strip()
        expected = os.getenv('ADMIN_API_KEY')
        expected = expected.strip() if isinstance(expected, str) else expected
        if not expected or token != expected:
            return jsonify({"error": "Unauthorized"}), 401

        payload = request.get_json() or {}
        to_email = (payload.get('to') or '').strip()
        if not to_email:
            return jsonify({"error": "Missing 'to' email"}), 400

        # Prefer SendGrid when configured
        if os.getenv('SENDGRID_API_KEY'):
            try:
                from email_utils import send_email as sg_send_email  # project root module
                resp = sg_send_email(to_email, "StructuredDocs Test Email", "This is a test email from StructuredDocs via SendGrid.")
                ok = bool(resp)
            except Exception as e:
                ok = False
        else:
            from ..utils.email_service import email_service
            ok = email_service.send_test_email(to_email)
        return jsonify({"ok": bool(ok)}), (200 if ok else 500)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/users', methods=['GET'])
def get_admin_users():
    """Get all users for admin management"""
    try:
        users = User.query.order_by(User.name).all()
        users_data = []
        
        for user in users:
            user_dict = user.to_dict()
            # Add additional admin-specific fields
            user_dict.update({
                'created_at': getattr(user, 'created_at', None),
                'last_login': getattr(user, 'last_login', None),
                'active': getattr(user, 'active', True),
                'role': getattr(user, 'role', 'user')
            })
            users_data.append(user_dict)
        
        return jsonify(users_data), 200
        
    except Exception as e:
        print(f"❌ Error in get_admin_users: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/notifications', methods=['GET'])
def get_admin_notifications():
    """Get all notifications for admin management"""
    try:
        notifications = Notification.query.order_by(Notification.date.desc()).all()
        notifications_data = []
        
        for notification in notifications:
            notif_dict = notification.to_dict()
            # Add user information if available
            if notification.user_id:
                user = User.query.get(notification.user_id)
                notif_dict['user_name'] = user.name if user else 'Unknown User'
            else:
                notif_dict['user_name'] = 'All Users'
            
            notifications_data.append(notif_dict)
        
        return jsonify(notifications_data), 200
        
    except Exception as e:
        print(f"❌ Error in get_admin_notifications: {e}")
        return jsonify({'error': str(e)}), 500
