"""
Audit logging utilities.

Usage in a route:
    from ..utils.audit import log_audit

    log_audit('create', 'topic', topic.id)
    log_audit('update', 'collection', coll.id, details={'title': coll.title})
    log_audit('delete', 'project', project_id)
"""

import json
from flask import request, current_app

def log_audit(action: str, resource_type: str, resource_id=None, details: dict | None = None, user_id=None):
    """Write one AuditLog row.  Silently ignores errors so a logging failure
    never breaks the actual API response.

    Parameters
    ----------
    action        : 'create' | 'update' | 'delete' (or any short verb)
    resource_type : e.g. 'topic', 'collection', 'publication'
    resource_id   : the PK of the affected row, or None
    details       : optional dict serialised to JSON in the 'details' column
    user_id       : override; defaults to the JWT identity of the current request
    """
    try:
        from ..extensions import db
        from ..models import AuditLog
        from flask_jwt_extended import get_jwt_identity

        if user_id is None:
            try:
                identity = get_jwt_identity()
                user_id = int(identity) if identity is not None else None
            except Exception:
                user_id = None

        ip = (request.headers.get('X-Forwarded-For') or request.remote_addr or '')[:45]

        entry = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=json.dumps(details) if details else None,
            ip_address=ip or None,
        )
        db.session.add(entry)
        db.session.flush()   # flush within the current transaction; caller commits
    except Exception as exc:
        try:
            current_app.logger.warning(f"audit log failed: {exc}")
        except Exception:
            pass
