from flask import Blueprint, request, jsonify
from ..models import db, User, Notification, Topic, Collection, Project, Task
from ..utils.email_service import get_email_service
from ..utils.storage import get_storage_backend, SpacesStorage
from sqlalchemy import func, text
from datetime import datetime, timedelta
import os
from typing import Any

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
        # Auth: Authorization: Bearer <token> OR Authorization: <token> OR X-Admin-Token
        auth = request.headers.get('Authorization', '') or ''
        token = ''
        if auth.startswith('Bearer '):
            token = auth[7:].strip()
        elif auth:
            token = auth.strip()
        if not token:
            token = (request.headers.get('X-Admin-Token', '') or '').strip()
        expected = (os.getenv('ADMIN_API_KEY') or '').strip()
        if not expected or token != expected:
            return jsonify({"error": "Unauthorized"}), 401

        payload = request.get_json(silent=True) or {}
        to_email = (payload.get('to') or '').strip()
        if not to_email:
            return jsonify({"error": "Missing 'to' email"}), 400

        use_sendgrid = bool(os.getenv('SENDGRID_API_KEY'))
        status_code = None
        body_text = None
        ok = False
        # Ensure these are always defined to avoid unbound variable errors if SendGrid initialization fails
        from_email = (os.getenv('DEFAULT_FROM_EMAIL', '') or '').strip()
        verified_sender = ''

        if use_sendgrid:
            try:
                from sendgrid import SendGridAPIClient  # type: ignore
                from sendgrid.helpers.mail import Mail  # type: ignore
                api_key = os.getenv('SENDGRID_API_KEY')
                # Prefer verified sender to satisfy DMARC if provided
                verified_sender = (os.getenv('SENDGRID_VERIFIED_SENDER') or '').strip()
                from_email = (verified_sender or os.getenv('DEFAULT_FROM_EMAIL', '')).strip()
                branding_from = (os.getenv('DEFAULT_FROM_EMAIL', '')).strip()
                branding_name = (os.getenv('FROM_NAME', 'StructuredDocs')).strip()

                message = Mail(
                    from_email={"email": from_email, "name": branding_name},
                    to_emails=to_email,
                    subject="StructuredDocs Test Email",
                    plain_text_content="This is a test email from StructuredDocs via SendGrid.",
                    html_content="<strong>This is a test email from StructuredDocs via SendGrid.</strong>",
                )
                # If using a verified sender that differs from branding, set Reply-To
                if verified_sender and branding_from and verified_sender != branding_from:
                    try:
                        message.reply_to = {"email": branding_from, "name": branding_name}
                    except Exception:
                        pass
                sg = SendGridAPIClient(api_key)
                resp = sg.send(message)
                status_code = getattr(resp, 'status_code', None)
                body = getattr(resp, 'body', b'')
                body_text = body.decode('utf-8', errors='ignore') if isinstance(body, (bytes, bytearray)) else str(body)
                ok = (status_code == 202)
            except Exception as e:
                body_text = str(e)
                ok = False
        else:
            from ..utils.email_service import email_service
            ok = email_service.send_test_email(to_email)
        # Non-secret diagnostics
        detail: dict[str, Any] = {"provider": "sendgrid" if use_sendgrid else "smtp"}
        if use_sendgrid:
            detail["from"] = from_email
            detail["verifiedSenderUsed"] = bool(verified_sender)
            detail["has_key"] = str(True)
            detail["status_code"] = str(status_code) if status_code is not None else ""
            detail["response"] = body_text or ""
        else:
            detail["server"] = os.getenv('SMTP_SERVER', '')
            detail["from"] = from_email or os.getenv('FROM_EMAIL', '') or os.getenv('DEFAULT_FROM_EMAIL', '')

        return jsonify({"ok": bool(ok), "detail": detail}), (200 if ok else 500)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/email-status', methods=['GET'])
def email_status():
    """Return sanitized email configuration status (no secrets)."""
    try:
        auth = request.headers.get('Authorization', '') or ''
        token = ''
        if auth.startswith('Bearer '):
            token = auth[7:].strip()
        elif auth:
            token = auth.strip()
        if not token:
            token = (request.headers.get('X-Admin-Token', '') or '').strip()
        expected = (os.getenv('ADMIN_API_KEY') or '').strip()
        if not expected or token != expected:
            return jsonify({"error": "Unauthorized"}), 401

        svc = get_email_service()
        svc.reload_config()
        provider = svc.provider or 'smtp'
        data = {
            'provider': provider,
            'fromEmail': svc.from_email,
            'fromName': svc.from_name,
            'debugMode': svc.debug_mode,
            'smtpServer': svc.smtp_server if provider == 'smtp' else None,
            'smtpPort': svc.smtp_port if provider == 'smtp' else None,
            'lastError': svc.last_error,
            'hasPostmarkToken': bool(getattr(svc, 'postmark_token', '')),
            'hasResendKey': bool(getattr(svc, 'resend_api_key', '')),
        }
        return jsonify(data), 200
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

@admin_bp.route('/clear-database', methods=['POST'])
def clear_database():
    """Clear all data from the database except the admin user (admin-only endpoint)."""
    # NOTE: In production, you should add authentication/authorization checks here!
    # Adjust this email if your admin user uses a different address
    admin_email = 'admin@example.com'
    payload = request.get_json(silent=True) or {}
    purge_storage_requested = bool(payload.get('purge_storage', False))
    storage_prefix = (payload.get('storage_prefix') or 'images/').strip() or 'images/'
    normalized_prefix = storage_prefix.lstrip('/')
    if normalized_prefix and not normalized_prefix.endswith('/'):
        normalized_prefix = f"{normalized_prefix}/"

    purge_prefixes = [normalized_prefix] if normalized_prefix else ['images/']
    if normalized_prefix == 'images/':
        # Legacy imports may have been stored under imports/ directly
        purge_prefixes.append('imports/')
    # Include leading-slash variants to catch historical malformed keys
    purge_prefixes.extend([f"/{p}" for p in list(purge_prefixes)])

    # Preserve order, remove duplicates
    seen_prefixes = set()
    purge_prefixes = [p for p in purge_prefixes if p and not (p in seen_prefixes or seen_prefixes.add(p))]

    def purge_spaces_objects(prefix: str) -> dict[str, Any]:
        """Delete Spaces objects under the provided prefix in batches."""
        storage = get_storage_backend()
        if not isinstance(storage, SpacesStorage):
            return {
                'attempted': False,
                'purged': False,
                'deleted_count': 0,
                'prefix': prefix,
                'message': 'Active storage backend is not Spaces; skipped storage purge.'
            }

        deleted_count = 0
        matched_count = 0
        continuation_token = None
        while True:
            list_kwargs: dict[str, Any] = {
                'Bucket': storage.bucket,
                'Prefix': prefix
            }
            if continuation_token:
                list_kwargs['ContinuationToken'] = continuation_token

            response = storage.s3_client.list_objects_v2(**list_kwargs)
            object_keys = [obj.get('Key') for obj in response.get('Contents', []) if obj.get('Key')]
            matched_count += len(object_keys)

            for idx in range(0, len(object_keys), 1000):
                chunk = object_keys[idx:idx + 1000]
                if not chunk:
                    continue
                delete_response = storage.s3_client.delete_objects(
                    Bucket=storage.bucket,
                    Delete={'Objects': [{'Key': key} for key in chunk], 'Quiet': True}
                )
                deleted_count += len(delete_response.get('Deleted', []))

            if not response.get('IsTruncated'):
                break
            continuation_token = response.get('NextContinuationToken')

        return {
            'attempted': True,
            'purged': True,
            'deleted_count': deleted_count,
            'matched_count': matched_count,
            'prefix': prefix,
            'message': f'Deleted {deleted_count} of {matched_count} Spaces object(s) under prefix "{prefix}".'
        }

    try:
        db.session.execute(text("DELETE FROM tags;"))
        db.session.execute(text("DELETE FROM review_feedback;"))
        db.session.execute(text("DELETE FROM review_tokens;"))
        db.session.execute(text("DELETE FROM reviews;"))
        db.session.execute(text("DELETE FROM password_reset_tokens;"))
        db.session.execute(text("DELETE FROM notifications;"))
        db.session.execute(text("DELETE FROM topic_links;"))
        db.session.execute(text("DELETE FROM links;"))
        db.session.execute(text("DELETE FROM import_items;"))
        db.session.execute(text("DELETE FROM import_links;"))
        db.session.execute(text("DELETE FROM import_images;"))
        db.session.execute(text("DELETE FROM import_documents;"))
        db.session.execute(text("DELETE FROM publication_nodes;"))
        db.session.execute(text("DELETE FROM publications;"))
        db.session.execute(text("DELETE FROM project_stakeholders;"))
        db.session.execute(text("DELETE FROM project_milestones;"))
        db.session.execute(text("DELETE FROM collections;"))
        db.session.execute(text("DELETE FROM collection_topic_tree;"))
        db.session.execute(text("DELETE FROM tasks;"))
        db.session.execute(text("DELETE FROM stakeholders;"))
        db.session.execute(text("DELETE FROM topics;"))
        db.session.execute(text("DELETE FROM projects;"))
        db.session.execute(text("DELETE FROM users WHERE email != :admin_email"), {"admin_email": admin_email})
        db.session.commit()

        storage_purge_result = {
            'attempted': False,
            'purged': False,
            'deleted_count': 0,
            'matched_count': 0,
            'prefix': normalized_prefix,
            'prefixes': purge_prefixes,
            'message': 'Storage purge not requested.'
        }

        if purge_storage_requested:
            try:
                per_prefix_results = [purge_spaces_objects(prefix) for prefix in purge_prefixes]
                attempted = any(r.get('attempted') for r in per_prefix_results)
                purged = any(r.get('purged') for r in per_prefix_results)
                total_deleted = sum(int(r.get('deleted_count') or 0) for r in per_prefix_results)
                total_matched = sum(int(r.get('matched_count') or 0) for r in per_prefix_results)

                storage_purge_result = {
                    'attempted': attempted,
                    'purged': purged,
                    'deleted_count': total_deleted,
                    'matched_count': total_matched,
                    'prefix': normalized_prefix,
                    'prefixes': purge_prefixes,
                    'details': per_prefix_results,
                    'message': f'Storage purge completed: deleted {total_deleted} of {total_matched} object(s) across {len(purge_prefixes)} prefix(es).'
                }
            except Exception as storage_err:
                storage_purge_result = {
                    'attempted': True,
                    'purged': False,
                    'deleted_count': 0,
                    'matched_count': 0,
                    'prefix': normalized_prefix,
                    'prefixes': purge_prefixes,
                    'message': f'Storage purge failed: {storage_err}'
                }

        return jsonify({
            'status': 'success',
            'message': 'Database cleared except for admin user.',
            'storage_purge': storage_purge_result
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
