from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, verify_jwt_in_request
from ..models import db, User, Notification, Topic, Collection, Project, Task, AuditLog, SystemSetting
from ..utils.email_service import get_email_service
from ..utils.storage import get_storage_backend, SpacesStorage
from ..utils.settings import get_setting, set_setting, DEFAULTS
from sqlalchemy import func, text
from datetime import datetime, timedelta
import os
from typing import Any

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


def _extract_bearer_or_raw_token() -> str:
    auth = request.headers.get('Authorization', '') or ''
    if auth.startswith('Bearer '):
        return auth[7:].strip()
    return auth.strip()


def _require_admin_or_api_key():
    """Allow either the admin API key or an authenticated admin JWT."""
    expected = (os.getenv('ADMIN_API_KEY') or '').strip()
    supplied = _extract_bearer_or_raw_token() or (request.headers.get('X-Admin-Token', '') or '').strip()

    if expected and supplied == expected:
        return None

    try:
        verify_jwt_in_request()
    except Exception:
        return jsonify({"error": "Unauthorized"}), 401

    from ..routes.users import _require_admin
    _, err = _require_admin()
    return err

@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_admin_stats():
    """Get admin dashboard statistics including system metrics"""
    try:
        # Get user statistics
        total_users = User.query.count()
        active_users = User.query.filter(User.active == True).count() if hasattr(User, 'active') else total_users
        authors = User.query.filter(User.role == 'author').count() if hasattr(User, 'role') else 0
        reviewers = User.query.filter(User.role == 'reviewer').count() if hasattr(User, 'role') else 0

        # Users seen in the last 15 minutes
        fifteen_min_ago = datetime.utcnow() - timedelta(minutes=15)
        online_now = (
            User.query.filter(User.last_seen >= fifteen_min_ago).count()
            if hasattr(User, 'last_seen') else 0
        )
        
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
            current_app.logger.warning(f" Error getting system metrics: {e}")
            # Fallback to explicit unavailable metrics (no fabricated values)
            system_performance = {
                'memoryUsage': None,
                'cpuUsage': None,
                'diskUsage': None,
                'systemHealth': 'unavailable',
                'serverStatus': 'online',
                'databaseStatus': 'connected',
                'metricSource': 'unavailable',
                'metricError': str(e)
            }
            db_metrics = {'size': 'Unknown', 'tables': 0, 'totalRecords': 0}
            app_metrics = {'users': {'active': active_users, 'total': total_users}}
        
        stats = {
            'totalUsers': total_users,
            'activeUsers': active_users,
            'onlineNow': online_now,
            'authors': authors,
            'reviewers': reviewers,
            'systemHealth': system_performance.get('systemHealth', 'Good'),
            'uptime': system_performance.get('uptime', '99.9%')
        }

        user_stats = {
            'totalUsers': total_users,
            'activeUsers': active_users,
            'onlineNow': online_now,
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
            'uptime': system_performance.get('uptime', 'Unknown'),
            'metricSource': system_performance.get('metricSource', 'unknown'),
            'metricError': system_performance.get('metricError')
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
        current_app.logger.error(f" Error in get_admin_stats: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/activity', methods=['GET'])
@jwt_required()
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
            current_app.logger.debug(f"Error fetching recent users: {e}")
        
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
            current_app.logger.debug(f"Error fetching recent topics: {e}")
        
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
            current_app.logger.debug(f"Error fetching recent collections: {e}")
        
        # Sort by timestamp descending and limit to 10 most recent
        activity_items.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify(activity_items[:10]), 200
        
    except Exception as e:
        current_app.logger.error(f" Error in get_recent_activity: {e}")
        return jsonify([]), 200  # Return empty array instead of error

@admin_bp.route('/system-logs', methods=['GET'])
@jwt_required()
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
        current_app.logger.error(f" Error in get_system_logs: {e}")
        return jsonify([]), 200

@admin_bp.route('/send-test-email', methods=['POST'])
def send_test_email_endpoint():
    """Send a test email to verify SMTP configuration.

    Protect with ADMIN_API_KEY in Authorization/X-Admin-Token or an admin JWT.
    Body: { "to": "you@example.com" }
    """
    try:
        err = _require_admin_or_api_key()
        if err:
            return err

        payload = request.get_json(silent=True) or {}
        to_email = (payload.get('to') or '').strip()
        if not to_email:
            return jsonify({"error": "Missing 'to' email"}), 400

        svc = get_email_service()
        svc.reload_config()
        ok = svc.send_test_email(to_email)
        provider = svc.provider or 'smtp'
        detail: dict[str, Any] = {
            "provider": provider,
            "from": svc.from_email,
            "fromName": svc.from_name,
            "debugMode": svc.debug_mode,
            "lastError": svc.last_error,
            "verifiedSenderUsed": bool(getattr(svc, 'sendgrid_verified_sender', '')),
            "hasProviderApiKey": bool(
                getattr(svc, 'postmark_token', '') or
                getattr(svc, 'resend_api_key', '') or
                getattr(svc, 'sendgrid_api_key', '')
            ),
        }
        if provider == 'smtp':
            detail["server"] = svc.smtp_server
            detail["port"] = svc.smtp_port

        return jsonify({"ok": bool(ok), "detail": detail}), (200 if ok else 500)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/email-status', methods=['GET'])
def email_status():
    """Return sanitized email configuration status (no secrets)."""
    try:
        err = _require_admin_or_api_key()
        if err:
            return err

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
            'hasSendgridKey': bool(getattr(svc, 'sendgrid_api_key', '')),
            'sendgridVerifiedSender': getattr(svc, 'sendgrid_verified_sender', '') or None,
        }
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
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
        current_app.logger.error(f" Error in get_admin_users: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/notifications', methods=['GET'])
@jwt_required()
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
        current_app.logger.error(f" Error in get_admin_notifications: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/clear-database', methods=['POST'])
@jwt_required()
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
        # Delete in child-first order to satisfy foreign key constraints
        db.session.execute(text("DELETE FROM feedback_reports;"))
        db.session.execute(text("DELETE FROM review_feedback;"))
        db.session.execute(text("DELETE FROM review_tokens;"))
        db.session.execute(text("DELETE FROM review_sequence_steps;"))
        db.session.execute(text("DELETE FROM reviews;"))
        db.session.execute(text("DELETE FROM review_sequences;"))
        db.session.execute(text("DELETE FROM password_reset_tokens;"))
        db.session.execute(text("DELETE FROM notifications;"))
        db.session.execute(text("DELETE FROM tags;"))
        db.session.execute(text("DELETE FROM topic_links;"))
        db.session.execute(text("DELETE FROM collection_variable_selections;"))
        db.session.execute(text("DELETE FROM variable_values;"))
        db.session.execute(text("DELETE FROM variables;"))
        db.session.execute(text("DELETE FROM collection_topic_tree;"))
        db.session.execute(text("DELETE FROM import_items;"))
        db.session.execute(text("DELETE FROM import_links;"))
        db.session.execute(text("DELETE FROM import_images;"))
        db.session.execute(text("DELETE FROM import_documents;"))
        db.session.execute(text("DELETE FROM publication_nodes;"))
        db.session.execute(text("DELETE FROM publications;"))
        db.session.execute(text("DELETE FROM project_stakeholders;"))
        db.session.execute(text("DELETE FROM project_milestones;"))
        db.session.execute(text("DELETE FROM tasks;"))
        db.session.execute(text("DELETE FROM topics;"))
        db.session.execute(text("DELETE FROM collections;"))
        db.session.execute(text("DELETE FROM stakeholders;"))
        db.session.execute(text("DELETE FROM projects;"))
        db.session.execute(text("DELETE FROM links;"))
        db.session.execute(text("DELETE FROM snippets;"))
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


@admin_bp.route('/audit-logs', methods=['GET'])
@jwt_required()
def get_audit_logs():
    """Get recent audit log entries. Admin only.
    
    Query params:
      ?page=1&limit=50&resource_type=topic&action=delete&user_id=5
    """
    from ..routes.users import _require_admin
    caller, err = _require_admin()
    if err:
        return err

    page = max(1, request.args.get('page', 1, type=int))
    limit = min(200, max(1, request.args.get('limit', 50, type=int)))
    resource_type = request.args.get('resource_type')
    action = request.args.get('action')
    user_id = request.args.get('user_id', type=int)

    query = AuditLog.query.order_by(AuditLog.created_at.desc())
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)
    if action:
        query = query.filter(AuditLog.action == action)
    if user_id is not None:
        query = query.filter(AuditLog.user_id == user_id)

    total = query.count()
    entries = query.offset((page - 1) * limit).limit(limit).all()

    return jsonify({
        'items': [e.to_dict() for e in entries],
        'total': total,
        'page': page,
        'limit': limit,
        'pages': max(1, -(-total // limit)),
    }), 200


@admin_bp.route('/settings', methods=['GET'])
@jwt_required()
def get_settings():
    """Return all runtime-configurable system settings. Admin only."""
    from ..routes.users import _require_admin
    _, err = _require_admin()
    if err:
        return err

    rows = {row.key: row.to_dict() for row in SystemSetting.query.all()}
    # Include defaults for any keys not yet in DB
    result = []
    for key, (default_val, desc) in DEFAULTS.items():
        row = rows.get(key)
        result.append({
            'key': key,
            'value': row['value'] if row else default_val,
            'description': desc,
            'updated_at': row['updated_at'] if row else None,
        })
    return jsonify(result), 200


@admin_bp.route('/settings', methods=['PUT'])
@jwt_required()
def update_settings():
    """Update one or more runtime settings. Body: [{key, value}, ...]
    Admin only."""
    from ..routes.users import _require_admin
    _, err = _require_admin()
    if err:
        return err

    data = request.get_json() or []
    if not isinstance(data, list):
        data = [data]

    updated = []
    errors = []
    for item in data:
        key = item.get('key', '').strip()
        value = str(item.get('value', '')).strip()
        if not key or key not in DEFAULTS:
            errors.append(f"Unknown setting key: {key!r}")
            continue
        try:
            set_setting(key, value)
            # If upload size changed, apply immediately to Flask config
            if key == 'max_upload_size_mb':
                try:
                    current_app.config['MAX_CONTENT_LENGTH'] = int(value) * 1024 * 1024
                except (ValueError, TypeError):
                    pass
            updated.append(key)
        except Exception as exc:
            errors.append(f"{key}: {exc}")

    if errors and not updated:
        return jsonify({'error': '; '.join(errors)}), 400
    return jsonify({'updated': updated, 'errors': errors}), 200
