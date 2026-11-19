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

# Branding is read by PDF/HTML export workers and changed from the admin page.
# A process-local cache cannot be invalidated reliably across Gunicorn workers.
UNCACHED_SETTINGS = {
    'export_brand_name',
    'export_pdf_title_logo',
    'export_pdf_cover_logo_placement',
    'export_pdf_footer_logo',
    'export_pdf_cover_background',
    'export_pdf_cover_text_alignment',
    'export_pdf_cover_text_vertical_alignment',
    'export_pdf_cover_text_color',
    'export_html_logo',
    'export_html_primary_color',
    'export_html_accent_color',
    'export_branding_hidden_assets',
    'export_branding_templates',
}

# Defaults used when no DB row exists yet
DEFAULTS: dict[str, tuple[str, str]] = {
    # key: (default_value, human description)
    'import_rate_limit':          ('20 per hour',  'Max document imports per hour per IP'),
    'review_token_rate_limit':    ('10 per hour',  'Max review token generations per hour per IP'),
    'review_feedback_rate_limit': ('30 per hour',  'Max review feedback submissions per hour per IP'),
    'max_upload_size_mb':         ('20',           'Max upload file size in megabytes'),
    'export_brand_name':          ('StructuredDocs', 'Brand name shown in PDF and HTML exports'),
    'export_pdf_title_logo':      ('Title_Page_Logo.png', 'PDF title page logo (filename in backend/static/backgrounds or absolute path)'),
    'export_pdf_cover_logo_placement': ('bottom-left', 'Placement of the logo on the PDF cover only'),
    'export_pdf_footer_logo':     ('Footer_Logo.png', 'PDF footer logo (filename in backend/static/backgrounds or absolute path)'),
    'export_pdf_cover_background':('SC Cover Background.png', 'Default PDF cover background image (filename in backend/static/backgrounds or absolute path)'),
    'export_pdf_cover_text_alignment': ('right', 'Horizontal alignment of the PDF cover title and subtitle'),
    'export_pdf_cover_text_vertical_alignment': ('top', 'Vertical alignment of the PDF cover title and subtitle as a group'),
    'export_pdf_cover_text_color': ('', 'Title and subtitle color (#RRGGBB). Leave blank for white on image covers or the default text colors on plain covers.'),
    'export_html_logo':           ('', 'HTML export logo URL, data URI, or local image filename/path to embed'),
    'export_html_primary_color':  ('#005a9c', 'Primary HTML export brand color (#RRGGBB)'),
    'export_html_accent_color':   ('#112E51', 'Accent HTML export brand color (#RRGGBB)'),
    'export_branding_hidden_assets': ('[]', 'JSON array of branding asset filenames hidden from admin selectors'),
    'export_branding_templates': ('[]', 'JSON array of export branding templates mapped to selected variable values'),
}


def get_setting(key: str, default: str | None = None) -> str:
    """Return the current value for *key*, querying DB on cache miss."""
    use_cache = key not in UNCACHED_SETTINGS
    if use_cache:
        with _cache_lock:
            if key in _cache:
                return _cache[key]

    # Cache miss — query DB inside app context
    try:
        from ..models import SystemSetting
        row = SystemSetting.query.filter_by(key=key).first()
        if row:
            if use_cache:
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

    if key not in UNCACHED_SETTINGS:
        with _cache_lock:
            _cache[key] = value
    else:
        with _cache_lock:
            _cache.pop(key, None)


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
