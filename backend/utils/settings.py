"""
Runtime settings helper.

Settings are stored in the `system_settings` DB table and cached in memory
so that every rate-limited request doesn't pay a DB round-trip.

Usage:
    from ..utils.settings import get_setting, set_setting

    get_setting('import_rate_limit', '20 per hour')
    set_setting('import_rate_limit', '30 per hour')
"""

import threading

_cache: dict[str, str] = {}
_cache_lock = threading.Lock()

# Defaults used when no DB row exists yet
DEFAULTS: dict[str, tuple[str, str]] = {
    # key: (default_value, human description)
    'import_rate_limit':          ('20 per hour',  'Max document imports per hour per IP'),
    'review_token_rate_limit':    ('10 per hour',  'Max review token generations per hour per IP'),
    'review_feedback_rate_limit': ('30 per hour',  'Max review feedback submissions per hour per IP'),
    'max_upload_size_mb':         ('20',           'Max upload file size in megabytes'),
}


def get_setting(key: str, default: str | None = None) -> str:
    """Return the current value for *key*, querying DB on cache miss."""
    with _cache_lock:
        if key in _cache:
            return _cache[key]

    # Cache miss — query DB inside app context
    try:
        from ..models import SystemSetting
        row = SystemSetting.query.filter_by(key=key).first()
        if row:
            with _cache_lock:
                _cache[key] = row.value
            return row.value
    except Exception:
        pass

    fallback = default if default is not None else DEFAULTS.get(key, ('',))[0]
    return fallback


def set_setting(key: str, value: str) -> None:
    """Persist *value* for *key* and update the in-memory cache."""
    from ..models import db, SystemSetting

    row = SystemSetting.query.filter_by(key=key).first()
    if row:
        row.value = value
    else:
        desc = DEFAULTS.get(key, ('', ''))[1]
        row = SystemSetting(key=key, value=value, description=desc)
        db.session.add(row)
    db.session.commit()

    with _cache_lock:
        _cache[key] = value


def seed_defaults() -> None:
    """Insert any missing default rows (called once at app startup)."""
    from ..models import db, SystemSetting
    try:
        for key, (default_val, desc) in DEFAULTS.items():
            if not SystemSetting.query.filter_by(key=key).first():
                db.session.add(SystemSetting(key=key, value=default_val, description=desc))
        db.session.commit()
    except Exception:
        db.session.rollback()
