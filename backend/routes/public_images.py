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
        # Prevent directory traversal attacks
        if '..' in filename or filename.startswith('/'):
            current_app.logger.warning(f"Attempted directory traversal: {filename}")
            abort(400)
        
        # Backend static path (primary)
        backend_dir = Path(current_app.root_path) / 'static' / 'images' / 'imports' / str(doc_id)
        backend_file = backend_dir / filename
        
        if backend_file.exists() and backend_file.is_file():
            current_app.logger.debug(f"Serving image from backend: {backend_file}")
            return send_from_directory(str(backend_dir), filename)

        # Frontend public fallback (secondary)
        public_dir = Path(current_app.root_path).parent / 'frontend' / 'public' / 'images' / 'imports' / str(doc_id)
        public_file = public_dir / filename
        
        if public_file.exists() and public_file.is_file():
            current_app.logger.debug(f"Serving image from frontend public: {public_file}")
            return send_from_directory(str(public_dir), filename)

        # Not found - log for debugging
        current_app.logger.warning(f"Image not found: /images/imports/{doc_id}/{filename}")
        current_app.logger.debug(f"  Checked backend: {backend_file} (exists: {backend_file.exists()})")
        current_app.logger.debug(f"  Checked frontend: {public_file} (exists: {public_file.exists()})")
        abort(404)
        
    except (ValueError, OSError) as e:
        current_app.logger.error(f"Error serving image: {e}")
        abort(404)

