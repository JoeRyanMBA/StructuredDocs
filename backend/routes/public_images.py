"""
Serve public image paths under /images/imports/<id>/<filename> from backend storage.
This avoids 404s when frontend static host doesn't have post-import files.
"""

import os
from flask import Blueprint, current_app, send_from_directory, abort
from pathlib import Path

public_images_bp = Blueprint('public_images', __name__, url_prefix='/images')

@public_images_bp.route('/imports/<int:doc_id>/<path:filename>', methods=['GET'])
def serve_import_image(doc_id: int, filename: str):
    """Serve an imported image from backend static or frontend public fallback."""
    try:
        # Backend static path
        backend_dir = Path(current_app.root_path) / 'static' / 'images' / 'imports' / str(doc_id)
        backend_dir.mkdir(parents=True, exist_ok=True)
        backend_file = backend_dir / filename
        if backend_file.exists():
            return send_from_directory(str(backend_dir), filename)

        # Frontend public fallback
        public_dir = Path(current_app.root_path).parent / 'frontend' / 'public' / 'images' / 'imports' / str(doc_id)
        public_file = public_dir / filename
        if public_file.exists():
            return send_from_directory(str(public_dir), filename)

        abort(404)
    except Exception:
        abort(404)
