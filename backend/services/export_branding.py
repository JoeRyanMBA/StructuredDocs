import os
import re
from typing import Dict

from ..utils.settings import get_setting


HEX_COLOR_RE = re.compile(r"^#?[0-9A-Fa-f]{6}$")


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
    if not candidate:
        return ""

    if os.path.isabs(candidate) and os.path.exists(candidate):
        return candidate

    service_dir = os.path.dirname(__file__)
    backend_dir = os.path.dirname(service_dir)
    repo_root = os.path.dirname(backend_dir)
    backgrounds_dir = os.path.join(backend_dir, "static", "backgrounds")

    direct_in_backgrounds = os.path.join(backgrounds_dir, os.path.basename(candidate))
    if os.path.exists(direct_in_backgrounds):
        return direct_in_backgrounds

    from_repo = os.path.join(repo_root, candidate)
    if os.path.exists(from_repo):
        return from_repo

    from_backend = os.path.join(backend_dir, candidate)
    if os.path.exists(from_backend):
        return from_backend

    return ""


def get_export_branding_settings() -> Dict[str, str]:
    """Return normalized export branding settings from runtime admin settings."""
    brand_name = get_setting("export_brand_name", DEFAULT_BRANDING["brand_name"]).strip()
    if not brand_name:
        brand_name = DEFAULT_BRANDING["brand_name"]

    html_primary_color = _normalize_hex_color(
        get_setting("export_html_primary_color", DEFAULT_BRANDING["html_primary_color"]),
        DEFAULT_BRANDING["html_primary_color"],
    )
    html_accent_color = _normalize_hex_color(
        get_setting("export_html_accent_color", DEFAULT_BRANDING["html_accent_color"]),
        DEFAULT_BRANDING["html_accent_color"],
    )

    return {
        "brand_name": brand_name,
        "pdf_title_logo": get_setting("export_pdf_title_logo", DEFAULT_BRANDING["pdf_title_logo"]).strip(),
        "pdf_footer_logo": get_setting("export_pdf_footer_logo", DEFAULT_BRANDING["pdf_footer_logo"]).strip(),
        "pdf_cover_background": get_setting("export_pdf_cover_background", DEFAULT_BRANDING["pdf_cover_background"]).strip(),
        "html_logo": get_setting("export_html_logo", DEFAULT_BRANDING["html_logo"]).strip(),
        "html_primary_color": html_primary_color,
        "html_accent_color": html_accent_color,
    }
