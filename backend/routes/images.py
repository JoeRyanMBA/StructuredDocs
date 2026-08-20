# backend/routes/images.py

import os
import uuid
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
from datetime import datetime
from ..models import db, ImportDocument, ImportImage
from ..utils.storage import S3CompatibleStorage, LocalStorage, get_storage_backend
from ..utils.image_registry import (
    build_canonical_image_payload,
    derive_local_image_paths,
    normalize_import_image_public_url,
    register_canonical_image,
)

images_bp = Blueprint('images', __name__, url_prefix='/api/images')

# Allowed file extensions for image uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'svg'}


def _require_admin_user():
    """Return the current admin user or None when access is denied."""
    from ..models import User
    from flask_jwt_extended import get_jwt_identity

    try:
        user_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        return None

    user = User.query.get(user_id)
    if not user or getattr(user, 'role', None) != 'admin':
        return None
    return user


def _delete_image_record(image):
    """Delete the on-disk file and database record for a single image."""
    for candidate in [image.backend_path, image.frontend_path]:
        if candidate and os.path.exists(candidate):
            try:
                os.remove(candidate)
            except OSError:
                current_app.logger.warning(f"Could not remove image file at {candidate}")

    db.session.delete(image)


def allowed_file(filename):
    """Check if file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@images_bp.route('', methods=['GET'])
@jwt_required()
def get_images():
    """Get all available images using ImportImage rows as the canonical source."""
    try:
        include_missing = request.args.get('include_missing', 'false').lower() == 'true'

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

        discovered_public_urls = set()
        registered_new_images = 0

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
            if public_url in discovered_public_urls:
                return
            discovered_public_urls.add(public_url)
            try:
                stat = os.stat(file_path)
                backend_path, frontend_path = derive_local_image_paths(current_app, public_url, file_path)
                _img, created = register_canonical_image(
                    db,
                    ImportImage,
                    ImportDocument,
                    filename=filename,
                    original_name=filename,
                    public_url=public_url,
                    backend_path=backend_path,
                    frontend_path=frontend_path,
                    file_size=stat.st_size,
                    created_at=datetime.fromtimestamp(getattr(stat, 'st_mtime', stat.st_ctime)),
                )
                nonlocal registered_new_images
                if created:
                    registered_new_images += 1
            except Exception:
                current_app.logger.warning(f"Could not register local image {public_url}")

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

        # Include remote object storage images when remote storage is configured
        try:
            storage = get_storage_backend()
            if isinstance(storage, S3CompatibleStorage):
                continuation_token = None
                while True:
                    list_kwargs = {
                        'Bucket': storage.bucket,
                        'Prefix': 'images/'
                    }
                    if continuation_token:
                        list_kwargs['ContinuationToken'] = continuation_token

                    response = storage.s3_client.list_objects_v2(**list_kwargs)
                    for obj in response.get('Contents', []):
                        key = obj.get('Key') or ''
                        if not key or key.endswith('/'):
                            continue
                        filename = os.path.basename(key)
                        if not allowed_file(filename):
                            continue

                        public_url = storage.get_url(key)
                        if public_url in discovered_public_urls:
                            continue
                        discovered_public_urls.add(public_url)

                        last_modified = obj.get('LastModified')
                        _img, created = register_canonical_image(
                            db,
                            ImportImage,
                            ImportDocument,
                            filename=filename,
                            original_name=filename,
                            public_url=public_url,
                            file_size=obj.get('Size'),
                            created_at=last_modified,
                        )
                        if created:
                            registered_new_images += 1

                    if not response.get('IsTruncated'):
                        break
                    continuation_token = response.get('NextContinuationToken')
        except Exception as e:
            current_app.logger.warning(f"Could not list remote storage images: {e}")

        if registered_new_images:
            db.session.commit()

        images = ImportImage.query.order_by(ImportImage.filename.asc()).all()
        images_data = []
        for image in images:
            payload = build_canonical_image_payload(image, include_file_exists=True)
            if payload.get('file_exists') or include_missing:
                images_data.append(payload)

        return jsonify(images_data), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching images: {str(e)}")
        return jsonify({'error': 'Failed to fetch images'}), 500

@images_bp.route('/upload', methods=['POST'])
@jwt_required()
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

            # Read upload into memory once so we can route through configured storage backend
            file_bytes = file.read()
            file_size = len(file_bytes)
            content_type = file.mimetype or None

            storage = get_storage_backend()

            # Keep legacy local path shape while using a remote public URL when object storage is configured
            if isinstance(storage, LocalStorage):
                storage_path = unique_filename
            else:
                storage_path = f"images/{unique_filename}"

            stored_url = storage.save_file(file_bytes, storage_path, content_type=content_type)

            if isinstance(storage, LocalStorage):
                public_url = f"/images/{unique_filename}"

                # Ensure legacy static/images path is still populated for existing consumers
                static_images_dir = os.path.join(current_app.config['STATIC_FOLDER'], 'images')
                os.makedirs(static_images_dir, exist_ok=True)
                static_file_path = os.path.join(static_images_dir, unique_filename)
                if not os.path.exists(static_file_path):
                    with open(static_file_path, 'wb') as image_file:
                        image_file.write(file_bytes)
            else:
                public_url = stored_url

            backend_path, frontend_path = derive_local_image_paths(
                current_app,
                public_url,
                static_file_path if isinstance(storage, LocalStorage) else '',
            )
            image_record, _created = register_canonical_image(
                db,
                ImportImage,
                ImportDocument,
                filename=unique_filename,
                original_name=original_filename,
                public_url=public_url,
                backend_path=backend_path,
                frontend_path=frontend_path,
                file_size=file_size,
                mime_type=content_type,
                created_at=datetime.utcnow(),
            )
            db.session.commit()

            return jsonify(build_canonical_image_payload(image_record, include_file_exists=True)), 201
            
        else:
            return jsonify({'error': 'Invalid file type. Allowed types: ' + ', '.join(ALLOWED_EXTENSIONS)}), 400
            
    except Exception as e:
        current_app.logger.error(f"Error uploading image: {str(e)}")
        return jsonify({'error': 'Failed to upload image'}), 500

@images_bp.route('/bulk-delete', methods=['POST'])
@jwt_required()
def bulk_delete_images():
    """Delete multiple images after verifying admin permissions."""
    try:
        admin_user = _require_admin_user()
        if not admin_user:
            return jsonify({'error': 'Admin access required'}), 403

        data = request.get_json(silent=True) or {}
        image_ids = data.get('image_ids') or data.get('ids') or []
        if not isinstance(image_ids, list):
            return jsonify({'error': 'image_ids must be a list'}), 400

        normalized_ids = []
        for value in image_ids:
            try:
                normalized_ids.append(int(value))
            except (TypeError, ValueError):
                continue

        if not normalized_ids:
            return jsonify({'message': 'No images selected for deletion', 'deleted': 0}), 400

        images = ImportImage.query.filter(ImportImage.id.in_(normalized_ids)).all()
        for image in images:
            _delete_image_record(image)

        db.session.commit()
        return jsonify({
            'message': 'Images deleted successfully',
            'deleted': len(images),
            'image_ids': [image.id for image in images],
        }), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception('Error deleting multiple images')
        return jsonify({'error': 'Failed to delete selected images'}), 500


@images_bp.route('/<int:image_id>', methods=['DELETE'])
@jwt_required()
def delete_image(image_id):
    """Delete an image by its canonical ImportImage record ID."""
    try:
        admin_user = _require_admin_user()
        if not admin_user:
            return jsonify({'error': 'Admin access required'}), 403

        image = ImportImage.query.get_or_404(image_id)
        _delete_image_record(image)
        db.session.commit()
        return jsonify({'message': 'Image deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting image: {str(e)}")
        return jsonify({'error': 'Failed to delete image'}), 500


@images_bp.route('/usage-summary', methods=['GET'])
@jwt_required()
def images_usage_summary():
    """For each ImportImage, find which topics reference its public_url in content,
    then return per-image collection + project usage."""
    try:
        from sqlalchemy import select as sa_select
        from ..models import Collection, Project, collection_topic_tree, Topic

        images = ImportImage.query.filter(ImportImage.public_url.isnot(None)).all()
        if not images:
            return jsonify({}), 200

        # Load all topics with content once
        topics = Topic.query.with_entities(Topic.id, Topic.title, Topic.content).all()
        topic_title_map = {t.id: t.title for t in topics}

        # Build map: canonical image URL → list of topic_ids that reference it
        image_topic_map = {}  # canonical public_url → set of topic_ids
        for img in images:
            raw_url = img.public_url
            if not raw_url:
                continue
            url = normalize_import_image_public_url(raw_url, document_id=img.document_id, filename=img.filename)
            if not url:
                continue
            referencing = {t.id for t in topics if t.content and (url in t.content or raw_url in t.content)}
            image_topic_map[url] = referencing

        # For each image, look up collections/projects for those topic_ids
        col_cache = {}   # collection_id → (name, proj_id, proj_name)

        def get_col_info(col_id):
            if col_id not in col_cache:
                col = Collection.query.get(col_id)
                if col:
                    col_cache[col_id] = (
                        col.name,
                        col.project_id,
                        col.project.name if col.project else None
                    )
                else:
                    col_cache[col_id] = (None, None, None)
            return col_cache[col_id]

        result = {}
        for img in images:
            url = normalize_import_image_public_url(img.public_url, document_id=img.document_id, filename=img.filename)
            topic_ids = image_topic_map.get(url, set())
            collections = {}
            projects = {}
            for tid in topic_ids:
                rows = db.session.execute(
                    sa_select(collection_topic_tree.c.collection_id)
                    .where(collection_topic_tree.c.topic_id == tid)
                ).fetchall()
                for row in rows:
                    cname, pid, pname = get_col_info(row.collection_id)
                    if cname:
                        collections[row.collection_id] = cname
                    if pid and pname:
                        projects[pid] = pname

            result[url] = {
                'topics':      [{'id': tid, 'name': topic_title_map.get(tid, f'Topic {tid}')} for tid in topic_ids],
                'collections': [{'id': k, 'name': v} for k, v in collections.items()],
                'projects':    [{'id': k, 'name': v} for k, v in projects.items()],
            }

        return jsonify(result), 200
    except Exception as e:
        current_app.logger.exception("Failed to build image usage summary")
        return jsonify({'error': str(e)}), 500
