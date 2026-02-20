# backend/routes/images.py

import os
import uuid
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime
from ..models import db, ImportImage

images_bp = Blueprint('images', __name__, url_prefix='/api/images')

# Allowed file extensions for image uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'svg'}

def allowed_file(filename):
    """Check if file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@images_bp.route('', methods=['GET'])
def get_images():
    """Get all available images, scanning dist/public/backend images recursively.

    - Primary: frontend/dist/images (production build output)
    - Fallback: frontend/public/images (useful for post-build writes)
    - Fallback: backend/static/images (ingestion backend path)
    """
    try:
        images_data = []

        configured_root = (os.environ.get('IMAGE_STORAGE_ROOT') or '').strip()

        # Collect all candidate roots with their URL prefixes
        roots = []
        try:
            dist_images_dir = os.path.join(current_app.config['STATIC_FOLDER'], 'images')
            roots.append((dist_images_dir, '/images'))
        except Exception:
            pass

        public_images_dir = os.path.join(current_app.root_path, '..', 'frontend', 'public', 'images')
        roots.append((os.path.abspath(public_images_dir), '/images'))

        backend_images_dir = os.path.join(current_app.root_path, 'static', 'images')
        roots.append((backend_images_dir, '/images'))

        shared_images_dir = '/app/data/images'
        if configured_root:
            roots.append((configured_root, '/images'))
        roots.append((shared_images_dir, '/images'))

        seen = set()

        def _add_image(root_dir: str, rel_path: str, url_prefix: str):
            file_path = os.path.join(root_dir, rel_path)
            filename = os.path.basename(rel_path)
            if not allowed_file(filename):
                return
            if not os.path.isfile(file_path):
                return
            # Normalize rel path to URL form
            rel_url = rel_path.replace('\\', '/')
            public_url = f"{url_prefix}/{rel_url}"
            # Deduplicate by normalized URL
            if public_url in seen:
                return
            seen.add(public_url)
            try:
                stat = os.stat(file_path)
                images_data.append({
                    'id': hash(public_url) % 100000000,  # stable-ish
                    'filename': filename,
                    'file_path': public_url,
                    'public_url': public_url,
                    'alt_text': filename,
                    'size': stat.st_size,
                    'created_at': datetime.fromtimestamp(getattr(stat, 'st_mtime', stat.st_ctime)).isoformat()
                })
            except Exception:
                # best-effort; skip unreadable files
                pass

        for root_dir, url_prefix in roots:
            if not root_dir or not os.path.exists(root_dir):
                continue
            for base, _dirs, files in os.walk(root_dir):
                for f in files:
                    # Build path relative to root_dir so public_url = /images/<rel>
                    abs_path = os.path.join(base, f)
                    try:
                        rel_path = os.path.relpath(abs_path, root_dir)
                    except Exception:
                        # Fallback to filename-only
                        rel_path = f
                    _add_image(root_dir, rel_path, url_prefix)

        # Also include imported images from the database (ALL records, not just ones with files)
        # This matches how links work - return database truth, frontend handles missing files gracefully
        try:
            from ..models import ImportImage
            from pathlib import Path
            import_images = ImportImage.query.all()
            for img in import_images:
                public_url = (img.public_url or '').strip()
                if not public_url.startswith('/images/imports/') and img.document_id and img.filename:
                    public_url = f"/images/imports/{img.document_id}/{img.filename}"
                # Deduplicate
                if public_url not in seen:
                    seen.add(public_url)
                    try:
                        # Use created_at from database if available
                        stat = None
                        configured_root_path = Path(configured_root) if configured_root else None
                        backend_path = Path(img.backend_path)
                        frontend_path = Path(img.frontend_path)
                        fallback_backend_paths = [
                            Path('/app/data/images') / 'imports' / str(img.document_id) / img.filename,
                            Path(current_app.root_path) / 'static' / 'images' / 'imports' / str(img.document_id) / img.filename,
                        ]
                        if configured_root_path is not None:
                            fallback_backend_paths.insert(0, configured_root_path / 'imports' / str(img.document_id) / img.filename)

                        existing_backend_path = None
                        if backend_path.exists():
                            existing_backend_path = backend_path
                        elif frontend_path.exists():
                            stat = frontend_path.stat()
                        else:
                            for fallback_path in fallback_backend_paths:
                                if fallback_path.exists():
                                    existing_backend_path = fallback_path
                                    break

                        if existing_backend_path is not None:
                            stat = existing_backend_path.stat()
                        
                        images_data.append({
                            'id': hash(public_url) % 100000000,
                            'filename': img.filename,
                            'file_path': public_url,
                            'public_url': public_url,
                            'alt_text': img.original_name,
                            'size': stat.st_size if stat else img.file_size,
                            'created_at': img.created_at.isoformat() if img.created_at else None,
                            'document_id': img.document_id,
                            'source': 'import',
                            'file_exists': (existing_backend_path is not None) or frontend_path.exists()
                        })
                    except Exception as e:
                        # Still add the image record even if file check fails
                        try:
                            images_data.append({
                                'id': hash(public_url) % 100000000,
                                'filename': img.filename,
                                'file_path': public_url,
                                'public_url': public_url,
                                'alt_text': img.original_name,
                                'size': img.file_size,
                                'created_at': img.created_at.isoformat() if img.created_at else None,
                                'document_id': img.document_id,
                                'source': 'import',
                                'file_exists': False
                            })
                        except Exception:
                            pass
        except Exception as e:
            current_app.logger.warning(f"Could not fetch imported images from database: {e}")

        # Sort by filename for stability
        images_data.sort(key=lambda x: x.get('filename', ''))
        return jsonify(images_data), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching images: {str(e)}")
        return jsonify({'error': 'Failed to fetch images'}), 500

@images_bp.route('/upload', methods=['POST'])
def upload_image():
    """Upload a new image"""
    try:
        # Check if the post request has the file part
        if 'image' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['image']
        
        # If user does not select file, browser also
        # submits an empty part without filename
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            # Generate a unique filename
            original_filename = secure_filename(file.filename)
            name, ext = os.path.splitext(original_filename)
            unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
            
            # Ensure static images directory exists
            static_images_dir = os.path.join(current_app.config['STATIC_FOLDER'], 'images')
            os.makedirs(static_images_dir, exist_ok=True)
            
            # Save the file
            file_path = os.path.join(static_images_dir, unique_filename)
            file.save(file_path)
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Create public URL
            public_url = f"/images/{unique_filename}"
            
            # Return the image data
            return jsonify({
                'id': hash(unique_filename) % 1000000,
                'filename': unique_filename,
                'file_path': public_url,
                'public_url': public_url,
                'alt_text': original_filename,
                'size': file_size,
                'created_at': datetime.utcnow().isoformat()
            }), 201
            
        else:
            return jsonify({'error': 'Invalid file type. Allowed types: ' + ', '.join(ALLOWED_EXTENSIONS)}), 400
            
    except Exception as e:
        current_app.logger.error(f"Error uploading image: {str(e)}")
        return jsonify({'error': 'Failed to upload image'}), 500

@images_bp.route('/<int:image_id>', methods=['DELETE'])
def delete_image(image_id):
    """Delete an image (simplified - by filename hash)"""
    try:
        # This is a simplified approach - in production you'd want a proper database
        static_images_dir = os.path.join(current_app.config['STATIC_FOLDER'], 'images')
        
        # Find file by ID (hash)
        for filename in os.listdir(static_images_dir):
            if hash(filename) % 1000000 == image_id:
                file_path = os.path.join(static_images_dir, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    return jsonify({'message': 'Image deleted successfully'}), 200
        
        return jsonify({'error': 'Image not found'}), 404
        
    except Exception as e:
        current_app.logger.error(f"Error deleting image: {str(e)}")
        return jsonify({'error': 'Failed to delete image'}), 500
