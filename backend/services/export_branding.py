import os
import re
import json
import logging
from urllib.parse import unquote
from typing import Dict

from ..utils.settings import get_setting


HEX_COLOR_RE = re.compile(r"^#?[0-9A-Fa-f]{6}$")
NO_COVER_BACKGROUND_SENTINEL = "__none__"
PDF_COVER_TEXT_ALIGNMENT_KEY = "export_pdf_cover_text_alignment"
PDF_COVER_TEXT_ALIGNMENTS = ("right", "center")
PDF_COVER_TEXT_VERTICAL_ALIGNMENT_KEY = "export_pdf_cover_text_vertical_alignment"
PDF_COVER_TEXT_VERTICAL_ALIGNMENTS = ("top", "center")
PDF_COVER_TEXT_COLOR_KEY = "export_pdf_cover_text_color"
PDF_COVER_LOGO_PLACEMENT_KEY = "export_pdf_cover_logo_placement"
DEFAULT_PDF_COVER_LOGO_PLACEMENT = "bottom-left"
PDF_COVER_LOGO_PLACEMENTS = (
    "top-left", "top-center", "top-right", "bottom-left", "bottom-center", "bottom-right",
)


DEFAULT_BRANDING: Dict[str, str] = {
    "brand_name": "StructuredDocs",
    "pdf_title_logo": "Title_Page_Logo.png",
    "pdf_cover_logo_placement": DEFAULT_PDF_COVER_LOGO_PLACEMENT,
    "pdf_footer_logo": "Footer_Logo.png",
    "pdf_cover_background": "SC Cover Background.png",
    "pdf_cover_text_alignment": "right",
    "pdf_cover_text_vertical_alignment": "top",
    "pdf_cover_text_color": "",
    "html_logo": "",
    "html_primary_color": "#005a9c",
    "html_accent_color": "#112E51",
}


def get_brand_asset_filename(value: str) -> str:
    """Return the basename represented by a branding setting value."""
    candidate = (value or "").strip()
    admin_asset_prefix = "/api/admin/export-branding/assets/"
    if candidate.startswith(admin_asset_prefix):
        candidate = candidate[len(admin_asset_prefix):].split("?", 1)[0].split("#", 1)[0]
        if candidate.endswith("/preview"):
            candidate = candidate[:-len("/preview")]
        candidate = unquote(candidate)
    return os.path.basename(candidate)


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

    if candidate.startswith("/api/admin/export-branding/assets/"):
        candidate = get_brand_asset_filename(candidate)
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
        PDF_COVER_LOGO_PLACEMENT_KEY: get_setting(PDF_COVER_LOGO_PLACEMENT_KEY, DEFAULT_PDF_COVER_LOGO_PLACEMENT),
        "export_pdf_footer_logo": get_setting("export_pdf_footer_logo", DEFAULT_BRANDING["pdf_footer_logo"]),
        "export_pdf_cover_background": get_setting("export_pdf_cover_background", DEFAULT_BRANDING["pdf_cover_background"]),
        PDF_COVER_TEXT_ALIGNMENT_KEY: get_setting(PDF_COVER_TEXT_ALIGNMENT_KEY, DEFAULT_BRANDING["pdf_cover_text_alignment"]),
        PDF_COVER_TEXT_VERTICAL_ALIGNMENT_KEY: get_setting(
            PDF_COVER_TEXT_VERTICAL_ALIGNMENT_KEY, DEFAULT_BRANDING["pdf_cover_text_vertical_alignment"],
        ),
        PDF_COVER_TEXT_COLOR_KEY: get_setting(PDF_COVER_TEXT_COLOR_KEY, DEFAULT_BRANDING["pdf_cover_text_color"]),
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
        # Older templates retain their original cover styling.
        values[PDF_COVER_LOGO_PLACEMENT_KEY] = DEFAULT_PDF_COVER_LOGO_PLACEMENT
        values[PDF_COVER_TEXT_ALIGNMENT_KEY] = DEFAULT_BRANDING["pdf_cover_text_alignment"]
        values[PDF_COVER_TEXT_VERTICAL_ALIGNMENT_KEY] = DEFAULT_BRANDING["pdf_cover_text_vertical_alignment"]
        values[PDF_COVER_TEXT_COLOR_KEY] = DEFAULT_BRANDING["pdf_cover_text_color"]
        values.update({
            key: value for key, value in selected_template.get("settings", {}).items()
            if key in values
        })

    cover_logo_placement = values[PDF_COVER_LOGO_PLACEMENT_KEY]
    if cover_logo_placement not in PDF_COVER_LOGO_PLACEMENTS:
        logging.getLogger(__name__).warning("Invalid PDF cover logo placement; using Bottom Left")
        cover_logo_placement = DEFAULT_PDF_COVER_LOGO_PLACEMENT

    cover_text_alignment = values[PDF_COVER_TEXT_ALIGNMENT_KEY]
    if cover_text_alignment not in PDF_COVER_TEXT_ALIGNMENTS:
        logging.getLogger(__name__).warning("Invalid PDF cover text alignment; using Right")
        cover_text_alignment = DEFAULT_BRANDING["pdf_cover_text_alignment"]
    cover_text_vertical_alignment = values[PDF_COVER_TEXT_VERTICAL_ALIGNMENT_KEY]
    if cover_text_vertical_alignment not in PDF_COVER_TEXT_VERTICAL_ALIGNMENTS:
        logging.getLogger(__name__).warning("Invalid PDF cover text vertical alignment; using Top")
        cover_text_vertical_alignment = DEFAULT_BRANDING["pdf_cover_text_vertical_alignment"]

    raw_cover_text_color = values[PDF_COVER_TEXT_COLOR_KEY]
    cover_text_color = _normalize_hex_color(raw_cover_text_color, "") if isinstance(raw_cover_text_color, str) else ""
    if raw_cover_text_color != "" and not cover_text_color:
        logging.getLogger(__name__).warning("Invalid PDF cover text color; using the default cover colors")

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
        "pdf_cover_logo_placement": cover_logo_placement,
        "pdf_footer_logo": pdf_footer_logo,
        "pdf_cover_background": pdf_cover_background,
        "pdf_cover_text_alignment": cover_text_alignment,
        "pdf_cover_text_vertical_alignment": cover_text_vertical_alignment,
        "pdf_cover_text_color": cover_text_color,
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
