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
        
        current_app.logger.debug(f"🖼️ Image request: {doc_id}/{filename}")

        # Backend storage candidates (shared root first)
        configured_root = (os.environ.get('IMAGE_STORAGE_ROOT') or '').strip()
        backend_roots = []
        if configured_root:
            backend_roots.append(Path(configured_root))
        backend_roots.append(Path('/app/data/images'))
        backend_roots.append(Path(current_app.root_path) / 'static' / 'images')

        checked_backend_paths = []
        for backend_root in backend_roots:
            backend_dir = backend_root / 'imports' / str(doc_id)
            backend_file = backend_dir / filename
            checked_backend_paths.append(str(backend_file))

            current_app.logger.debug(f"   Backend path: {backend_file}")
            current_app.logger.debug(f"   Backend exists: {backend_file.exists()}")

            if backend_file.exists() and backend_file.is_file():
                file_size = backend_file.stat().st_size
                current_app.logger.debug(f"   ✅ Serving from backend ({file_size} bytes)")
                return send_from_directory(str(backend_dir), filename)

        # Frontend public fallback (secondary)
        public_dir = Path(current_app.root_path).parent / 'frontend' / 'public' / 'images' / 'imports' / str(doc_id)
        public_file = public_dir / filename
        
        current_app.logger.debug(f"   Frontend path: {public_file}")
        current_app.logger.debug(f"   Frontend exists: {public_file.exists()}")
        
        if public_file.exists() and public_file.is_file():
            file_size = public_file.stat().st_size
            current_app.logger.debug(f"   ✅ Serving from frontend ({file_size} bytes)")
            return send_from_directory(str(public_dir), filename)

        # Not found - log detailed debugging info
        current_app.logger.warning(f"❌ Image not found: /images/imports/{doc_id}/{filename}")
        current_app.logger.warning(f"   Backend checked: {checked_backend_paths}")
        current_app.logger.warning(f"   Frontend file: {public_file} (exists: {public_file.exists()})")

        # Check if any backend import directory exists
        existing_dirs = []
        for backend_root in backend_roots:
            backend_dir = backend_root / 'imports' / str(doc_id)
            if backend_dir.exists():
                existing_dirs.append(str(backend_dir))
                files_in_dir = list(backend_dir.glob('*'))
                current_app.logger.warning(f"   Backend dir exists with {len(files_in_dir)} files: {backend_dir}")
                for f in files_in_dir[:5]:
                    current_app.logger.warning(f"     - {f.name}")

        if not existing_dirs:
            current_app.logger.warning(f"   Backend dir doesn't exist in any root for doc {doc_id}")
        
        abort(404)
        
    except (ValueError, OSError) as e:
        current_app.logger.error(f"Error serving image: {e}")
        abort(404)

