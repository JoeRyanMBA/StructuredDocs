from __future__ import annotations

import os
import re
from datetime import datetime


IMAGE_REGISTRY_FILENAME = '__system_image_registry__.md'
IMAGE_REGISTRY_REVIEWER = 'system:image-registry'


def normalize_import_image_public_url(public_url: str | None, *, document_id: int | None = None, filename: str | None = None) -> str:
    """Normalize import image URLs to a single canonical /images/imports/... form.

    Imported documents may carry legacy variants such as /imports/<id>/<file>,
    images/imports/<id>/<file>, or a full remote URL. We normalize all local
    import variants to the same canonical path so matching and file existence
    checks stay consistent across the app.
    """
    raw = (public_url or '').strip()
    if not raw:
        return ''
    if raw.startswith(('http://', 'https://')):
        return raw

    normalized = raw.replace('\\', '/').strip()
    while normalized.startswith('./'):
        normalized = normalized[2:]

    if normalized.startswith('images/imports/'):
        normalized = '/' + normalized
    elif normalized.startswith('imports/'):
        normalized = '/images/' + normalized
    elif normalized.startswith('/imports/'):
        normalized = '/images' + normalized
    elif normalized.startswith('images/') and not normalized.startswith('/images/'):
        normalized = '/' + normalized

    if document_id is not None and filename:
        canonical = f'/images/imports/{document_id}/{filename}'
        if '/images/imports/' in normalized or normalized.startswith('/imports/') or normalized.startswith('images/imports/') or normalized.startswith('imports/'):
            return canonical

    return normalized


def build_import_image_basename_map(images=None):
    """Build a basename -> canonical public URL map for imported images.

    This is used to rewrite stale pandoc /tmp/.../media/... refs back to their
    permanent /images/imports/<doc>/<filename> equivalents in already-saved content.
    """
    if images is None:
        try:
            from backend.models import ImportImage
            images = ImportImage.query.filter(ImportImage.public_url.isnot(None)).all()
        except Exception:
            return {}

    mapping: dict[str, str] = {}
    for image in images or []:
        if image is None:
            continue
        public_url = getattr(image, 'public_url', '') or ''
        normalized = normalize_import_image_public_url(
            public_url,
            document_id=getattr(image, 'document_id', None),
            filename=getattr(image, 'filename', None),
        )
        if not normalized:
            continue
        basename = os.path.basename(normalized.replace('\\', '/'))
        if basename:
            mapping[basename] = normalized
    return mapping


def normalize_stale_temp_image_refs_in_content(content: str | None, *, basename_map: dict[str, str] | None = None) -> str:
    """Rewrite stale pandoc temp image refs to their canonical permanent URLs when known."""
    if not content:
        return content or ''
    if not basename_map:
        return content

    def resolve_url(url: str | None) -> str | None:
        if not url:
            return None
        cleaned = url.strip().replace('\\', '/')
        cleaned = cleaned.split('?', 1)[0].split('#', 1)[0]
        basename = os.path.basename(cleaned)
        if not basename or '/tmp/' not in cleaned.lower():
            return None
        canonical = basename_map.get(basename)
        return canonical if canonical else None

    def replace_markdown(match):
        alt_text = match.group(1)
        ref = match.group(2)
        replacement = resolve_url(ref)
        if replacement is None:
            return match.group(0)
        return f'![{alt_text}]({replacement})'

    def replace_html(match):
        prefix = match.group(1)
        ref = match.group(2)
        suffix = match.group(3)
        replacement = resolve_url(ref)
        if replacement is None:
            return match.group(0)
        return f'{prefix}{replacement}{suffix}'

    rewritten = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_markdown, content)
    rewritten = re.sub(r'(<img\b[^>]*\bsrc=["\'])([^"\']+)(["\'][^>]*>)', replace_html, rewritten)
    return rewritten


def normalize_stale_temp_image_refs_in_database(db_session, *, include_topics=True, include_publications=True):
    """One-time repair for topic/publication content that still contains temp pandoc refs."""
    try:
        from backend.models import ImportImage, Topic, PublicationNode

        basename_map = build_import_image_basename_map(ImportImage.query.filter(ImportImage.public_url.isnot(None)).all())
        if not basename_map:
            return {'topics_updated': 0, 'publication_nodes_updated': 0, 'updated_records': []}

        updated = []
        topics_updated = 0
        if include_topics:
            for topic in Topic.query.all():
                if not topic or not topic.content:
                    continue
                rewritten = normalize_stale_temp_image_refs_in_content(topic.content, basename_map=basename_map)
                if rewritten != topic.content:
                    topic.content = rewritten
                    updated.append({'type': 'topic', 'id': topic.id})
                    topics_updated += 1

        publication_nodes_updated = 0
        if include_publications:
            for node in PublicationNode.query.all():
                if not node or not node.content_snapshot:
                    continue
                rewritten = normalize_stale_temp_image_refs_in_content(node.content_snapshot, basename_map=basename_map)
                if rewritten != node.content_snapshot:
                    node.content_snapshot = rewritten
                    updated.append({'type': 'publication_node', 'id': node.id})
                    publication_nodes_updated += 1

        if updated:
            db_session.session.commit()
        return {
            'topics_updated': topics_updated,
            'publication_nodes_updated': publication_nodes_updated,
            'updated_records': updated,
        }
    except Exception:
        if 'db_session' in locals() and hasattr(db_session, 'session'):
            db_session.session.rollback()
        raise


def _normalize_public_url(public_url: str | None) -> str:
    return normalize_import_image_public_url(public_url)


def is_image_registry_document(document) -> bool:
    return bool(
        document
        and document.filename == IMAGE_REGISTRY_FILENAME
        and document.reviewer == IMAGE_REGISTRY_REVIEWER
    )


def get_or_create_image_registry_document(db, import_document_model):
    registry_doc = import_document_model.query.filter_by(
        filename=IMAGE_REGISTRY_FILENAME,
        reviewer=IMAGE_REGISTRY_REVIEWER,
    ).first()
    if registry_doc:
        return registry_doc

    registry_doc = import_document_model(
        filename=IMAGE_REGISTRY_FILENAME,
        source_type='markdown',
        status='approved',
        review_step='final_approved',
        reviewer=IMAGE_REGISTRY_REVIEWER,
    )
    db.session.add(registry_doc)
    db.session.flush()
    return registry_doc


def infer_image_source(public_url: str | None, document=None) -> str:
    normalized = _normalize_public_url(public_url)
    if '/images/imports/' in normalized:
        return 'import'
    if not is_image_registry_document(document):
        return 'import'
    if normalized.startswith('http://') or normalized.startswith('https://'):
        return 'spaces'
    return 'static'


def register_canonical_image(
    db,
    import_image_model,
    import_document_model,
    *,
    filename: str,
    original_name: str | None,
    public_url: str,
    backend_path: str | None = None,
    frontend_path: str | None = None,
    width: int | None = None,
    height: int | None = None,
    format: str | None = None,
    file_size: int | None = None,
    mime_type: str | None = None,
    created_at: datetime | None = None,
):
    normalized_public_url = _normalize_public_url(public_url)
    if not normalized_public_url:
        raise ValueError('public_url is required for canonical image registration')

    existing = import_image_model.query.filter_by(public_url=normalized_public_url).first()
    if existing:
        updated = False
        if not existing.original_name and original_name:
            existing.original_name = original_name
            updated = True
        if not existing.backend_path and backend_path:
            existing.backend_path = backend_path
            updated = True
        if not existing.frontend_path and frontend_path:
            existing.frontend_path = frontend_path
            updated = True
        if existing.width is None and width is not None:
            existing.width = width
            updated = True
        if existing.height is None and height is not None:
            existing.height = height
            updated = True
        if existing.format is None and format is not None:
            existing.format = format
            updated = True
        if existing.file_size is None and file_size is not None:
            existing.file_size = file_size
            updated = True
        if existing.mime_type is None and mime_type is not None:
            existing.mime_type = mime_type
            updated = True
        if updated:
            db.session.flush()
        return existing, False

    registry_doc = get_or_create_image_registry_document(db, import_document_model)
    image = import_image_model(
        document_id=registry_doc.id,
        filename=filename,
        original_name=original_name or filename,
        public_url=normalized_public_url,
        backend_path=backend_path or '',
        frontend_path=frontend_path or '',
        width=width,
        height=height,
        format=format,
        file_size=file_size,
        mime_type=mime_type,
        created_at=created_at or datetime.utcnow(),
    )
    db.session.add(image)
    db.session.flush()
    return image, True


def build_canonical_image_payload(image, *, include_file_exists=False):
    payload = image.to_dict(include_file_exists=include_file_exists)
    payload['public_url'] = normalize_import_image_public_url(payload.get('public_url'), document_id=getattr(image, 'document_id', None), filename=getattr(image, 'filename', None))
    payload['file_path'] = payload.get('public_url')
    payload['size'] = payload.get('file_size')
    payload['source'] = infer_image_source(payload.get('public_url'), getattr(image, 'document', None))
    return payload


def derive_local_image_paths(current_app, public_url: str, file_path: str):
    normalized_public_url = _normalize_public_url(public_url)
    backend_path = ''
    frontend_path = ''

    if normalized_public_url.startswith('/images/'):
        rel_path = normalized_public_url[len('/images/'):]
        backend_root = os.path.join(current_app.root_path, 'static', 'images')
        frontend_root = os.path.join(current_app.root_path, '..', 'frontend', 'public', 'images')
        backend_path = os.path.join(backend_root, rel_path)
        frontend_path = os.path.join(frontend_root, rel_path)

    if file_path and not backend_path:
        backend_path = file_path

    return backend_path, frontend_path
