# S3-Compatible Object Storage Configuration

## Overview

StructuredDocs supports S3-compatible object storage for persistent image storage across redeployments and multiple app instances.

## Required environment variables

Set these in your backend environment:

```bash
SPACES_BUCKET=your-bucket-name
SPACES_REGION=us-east-1
SPACES_ACCESS_KEY=your-access-key
SPACES_SECRET_KEY=your-secret-key
```

Optional:

```bash
SPACES_KEY_PREFIX=prod
SPACES_CDN_ENDPOINT=https://cdn.your-provider.example/your-bucket
```

## How it works

- If storage variables are present, the app uses S3-compatible storage.
- If not present, it falls back to local filesystem storage.

## Verification

1. Import a document with images.
2. Check `/diagnostics/storage` and verify remote storage is active.
3. Confirm images exist under `images/imports/{doc_id}/` in your bucket.

## Fallback behavior

Without storage variables, images are written to local disk and can be lost on container rebuild/redeploy.
