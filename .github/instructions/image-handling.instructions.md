---
description: "Use when working with image storage, retrieval, caching, rewriting, or troubleshooting image display in StructuredDocs. Covers S3-compatible storage, local fallback, image URL patterns, and CDN/proxy setup."
name: "StructuredDocs Image Handling"
applyTo: "backend/services/image*.py,backend/routes/images.py,backend/pdf_config.py,docs/object-storage*.md"
---
# Image Handling Patterns

Images in StructuredDocs are stored in S3-compatible object storage or local filesystem and accessed through URL rewriting patterns.

## Storage Configuration

Images can be stored in:
- **S3-compatible storage** (AWS S3, DigitalOcean Spaces, Wasabi, etc.)
- **Local filesystem fallback** (`instance/` or configurable directory)

**Configuration via environment:**
- `STORAGE_TYPE`: `s3` or `local`
- `S3_ENDPOINT_URL`, `S3_BUCKET_NAME`, `S3_ACCESS_KEY`, `S3_SECRET_KEY` (for S3)
- `LOCAL_STORAGE_PATH` (for local filesystem)

**Read:** [docs/object-storage-setup.md](../../docs/object-storage-setup.md)

## Image URL Patterns

- Original stored URL: `https://s3.example.com/bucket/image-uuid.png`
- Rewritten/proxied URL in content: `/api/images/<id>` or `/images/<id>`
- Frontend should never hardcode S3 URLs—always use the rewritten pattern

Image rewriting usually happens in:
- `backend/services/import_handler.py` (when importing documents)
- `backend/routes/images.py` (if serving through proxy)

## Common Operations

### Store an Image
```python
from backend.services import image_service  # or similar
image_data = b'...'  # bytes from upload or extraction
image_id = image_service.save_image(image_data, filename='doc-image-001.png')
# Returns: image_id or URL for storing in database
```

### Retrieve Image for Display
```python
# Route handler returns image data or redirect
@bp.get('/images/<image_id>')
def get_image(image_id):
    image_data, mime_type = image_service.get_image(image_id)
    return send_file(BytesIO(image_data), mimetype=mime_type)
```

### Rewrite Image URLs in Content
When importing documents, images are extracted and URLs rewritten:
```python
# Original: <img src="file:///C:\Users\...\image.png" />
# Rewritten: <img src="/api/images/abc123def456" />
content_html = rewrite_image_urls(html_content, document_id)
```

## CORS Configuration

For S3 storage to work with frontend:
- Enable CORS on S3 bucket
- Allow `GET`, `PUT`, `POST` methods for your domain
- **Read:** [docs/object-storage-cors.md](../../docs/object-storage-cors.md)

## Caching & Performance

Images may be:
- Cached by CDN (if using one)
- Cached by browser (via `Cache-Control` headers)
- Cached locally in frontend (via IndexedDB or localStorage)

When modifying image route, consider cache invalidation (e.g., version querystring).

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Images not displaying | URL rewrite failed | Check `backend/routes/import_handler.py` rewrite logic |
| S3 403 Forbidden | Bucket CORS not configured | Enable CORS, check credentials in `.env` |
| Local storage missing images | File path not writable | Check `LOCAL_STORAGE_PATH` permissions and directory existence |
| Image URLs hardcoded in exports | Export logic not rewriting URLs | Check PDF generator and HTML export service |
| Memory exhaustion on large uploads | Streaming not implemented | Use file chunking or multipart upload |

## Files to Check

- `backend/services/image*.py` — image storage/retrieval
- `backend/routes/images.py` — image serving endpoints (if exists)
- `backend/routes/import_handler.py` — image extraction and URL rewriting
- `backend/pdf_config.py` — image handling in PDF exports
- [docs/object-storage-setup.md](../../docs/object-storage-setup.md) — deployment guide
- [docs/object-storage-cors.md](../../docs/object-storage-cors.md) — CORS setup
- `.env` or environment templates — storage configuration

## Related Patterns

- Document import (extracts and rewrites images): [.github/skills/debug-import-pipeline.md](../skills/debug-import-pipeline.md)
- PDF export (embeds or links images): [.github/skills/debug-pdf-export.md](../skills/debug-pdf-export.md)
