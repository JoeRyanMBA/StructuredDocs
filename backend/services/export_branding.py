import os
import re
import json
from typing import Dict

from ..utils.settings import get_setting


HEX_COLOR_RE = re.compile(r"^#?[0-9A-Fa-f]{6}$")
NO_COVER_BACKGROUND_SENTINEL = "__none__"


DEFAULT_BRANDING: Dict[str, str] = {
    "brand_name": "StructuredDocs",
    "pdf_title_logo": "Title_Page_Logo.png",
    "pdf_footer_logo": "Footer_Logo.png",
    "pdf_cover_background": "SC Cover Background.png",
    "html_logo": "",
    "html_primary_color": "#005a9c",
    "html_accent_color": "#112E51",
}


def _normalize_hex_color(value: str, fallback: str) -> str:
    if not value:
        return fallback
    candidate = value.strip()
    if not HEX_COLOR_RE.match(candidate):
        return fallback
    if not candidate.startswith("#"):
        candidate = f"#{candidate}"
    return candidate


def resolve_brand_asset_path(value: str, fallback_filename: str = "") -> str:
    """Resolve branding asset paths from settings to local filesystem paths.

    Supports:
    - Absolute file paths
    - Bare filenames located under backend/static/backgrounds
    - Relative paths from repo root
    """
    candidate = (value or "").strip() or fallback_filename
    if candidate == NO_COVER_BACKGROUND_SENTINEL:
        return ""
    if not candidate:
        return ""

    if os.path.isabs(candidate) and os.path.exists(candidate):
        return candidate

    service_dir = os.path.dirname(__file__)
    backend_dir = os.path.dirname(service_dir)
    repo_root = os.path.dirname(backend_dir)
    configured_branding_dir = (os.environ.get("EXPORT_BRANDING_ASSETS_DIR") or "").strip()
    branding_dirs = [
        configured_branding_dir,
        os.path.join(backend_dir, "static", "backgrounds"),
    ]

    for branding_dir in branding_dirs:
        if not branding_dir:
            continue
        asset_path = os.path.join(branding_dir, os.path.basename(candidate))
        if os.path.exists(asset_path):
            return asset_path

    from_repo = os.path.join(repo_root, candidate)
    if os.path.exists(from_repo):
        return from_repo

    from_backend = os.path.join(backend_dir, candidate)
    if os.path.exists(from_backend):
        return from_backend

    return ""


def _validated_brand_asset(value: str, fallback: str) -> str:
    """Return the configured asset when it resolves to a real file; otherwise use the default.

    Special sentinel values such as NO_COVER_BACKGROUND_SENTINEL are preserved so the
    PDF cover can be intentionally disabled without falling back to the default cover.
    """
    candidate = (value or "").strip()
    if not candidate:
        return fallback
    if candidate == NO_COVER_BACKGROUND_SENTINEL:
        return NO_COVER_BACKGROUND_SENTINEL

    resolved = resolve_brand_asset_path(candidate, fallback)
    if not resolved or not os.path.exists(resolved):
        return fallback

    return candidate


def _load_branding_templates() -> list[dict]:
    raw = get_setting("export_branding_templates", "[]")
    try:
        templates = json.loads(raw or "[]")
    except (TypeError, ValueError):
        return []
    return templates if isinstance(templates, list) else []


def get_export_branding_settings(template_name: str = "") -> Dict[str, str]:
    """Return normalized export branding settings from runtime admin settings."""
    values = {
        "export_brand_name": get_setting("export_brand_name", DEFAULT_BRANDING["brand_name"]),
        "export_pdf_title_logo": get_setting("export_pdf_title_logo", DEFAULT_BRANDING["pdf_title_logo"]),
        "export_pdf_footer_logo": get_setting("export_pdf_footer_logo", DEFAULT_BRANDING["pdf_footer_logo"]),
        "export_pdf_cover_background": get_setting("export_pdf_cover_background", DEFAULT_BRANDING["pdf_cover_background"]),
        "export_html_logo": get_setting("export_html_logo", DEFAULT_BRANDING["html_logo"]),
        "export_html_primary_color": get_setting("export_html_primary_color", DEFAULT_BRANDING["html_primary_color"]),
        "export_html_accent_color": get_setting("export_html_accent_color", DEFAULT_BRANDING["html_accent_color"]),
    }
    selected_template = next(
        (template for template in _load_branding_templates()
         if template_name and template.get("name") == template_name),
        None,
    )
    if selected_template:
        values.update({
            key: value for key, value in selected_template.get("settings", {}).items()
            if key in values
        })

    brand_name = str(values["export_brand_name"] or "").strip()
    if not brand_name:
        brand_name = DEFAULT_BRANDING["brand_name"]

    html_primary_color = _normalize_hex_color(
        values["export_html_primary_color"],
        DEFAULT_BRANDING["html_primary_color"],
    )
    html_accent_color = _normalize_hex_color(
        values["export_html_accent_color"],
        DEFAULT_BRANDING["html_accent_color"],
    )

    pdf_title_logo = _validated_brand_asset(
        values["export_pdf_title_logo"],
        DEFAULT_BRANDING["pdf_title_logo"],
    )
    pdf_footer_logo = _validated_brand_asset(
        values["export_pdf_footer_logo"],
        DEFAULT_BRANDING["pdf_footer_logo"],
    )
    pdf_cover_background = _validated_brand_asset(
        values["export_pdf_cover_background"],
        DEFAULT_BRANDING["pdf_cover_background"],
    )

    return {
        "brand_name": brand_name,
        "pdf_title_logo": pdf_title_logo,
        "pdf_footer_logo": pdf_footer_logo,
        "pdf_cover_background": pdf_cover_background,
        "html_logo": str(values["export_html_logo"] or "").strip(),
        "html_primary_color": html_primary_color,
        "html_accent_color": html_accent_color,
    }


def get_export_branding_template_for_collection(collection_id: int) -> str | None:
    """Return the template mapped to any selected variable value in a collection."""
    from ..models import CollectionVariableSelection, VariableValue

    selected_value_ids = [
        row.variable_value_id
        for row in CollectionVariableSelection.query.filter_by(collection_id=collection_id).all()
        if row.variable_value_id
    ]
    if not selected_value_ids:
        return None

    selected_values = VariableValue.query.filter(VariableValue.id.in_(selected_value_ids)).all()
    selected_value_text = {value.value for value in selected_values}
    for template in _load_branding_templates():
        if template.get("variable_value") in selected_value_text:
            return template.get("name") or None
    return None
