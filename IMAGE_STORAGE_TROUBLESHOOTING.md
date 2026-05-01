# Image Storage Troubleshooting Guide

## Problem

Document imports succeed, but images later show as missing.

## Root cause

Images are being stored on local container disk instead of external object storage. Local files can be lost on restart/redeploy.

## Solution

1. Check storage diagnostics:

```text
https://your-backend-domain.example/diagnostics/storage
```

2. Ensure these environment variables are set:

```bash
SPACES_BUCKET=your-bucket
SPACES_REGION=us-east-1
SPACES_ACCESS_KEY=your-access-key
SPACES_SECRET_KEY=your-secret-key
```

3. Do not set `IMAGE_STORAGE_ROOT` when using object storage.

4. Redeploy backend and verify diagnostics show remote storage active.

5. Re-import affected documents if original local image files are gone.

## Expected remote image URL format

```text
https://your-bucket-endpoint/images/imports/{doc_id}/{filename}
```

## Related files

- `backend/utils/storage.py`
- `backend/utils/image_handler.py`
- `backend/routes/diagnostics.py`
- `SPACES_SETUP.md`
