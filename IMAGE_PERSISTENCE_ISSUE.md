# 🖼️ Image Persistence Issue - Root Cause & Solution

## Problem Summary

**Symptom**: Images appear after upload/import but disappear after:
- Container restart
- Page refresh  
- Logout/login
- Time passes

## Root Cause

Images are saved to the container's **ephemeral filesystem** (`/app/backend/static/images/`) which is:
- **Lost on container restart** (all uploaded images deleted)
- **Not shared across container instances** in multi-container setups
- **Not persisted** unless explicitly mounted to a host volume

### Why This Happens

When images are uploaded or imported:
1. ✅ Files are written to `/app/backend/static/images/` 
2. ✅ User sees them immediately (in-memory in Vue or freshly written)
3. ❌ **Container restarts or scales down**
4. ❌ Files are lost - `/app/backend/static/images/` is reset to initial state
5. ❌ Next page load: API scans `/app/backend/static/images/`, finds nothing, returns empty list

## Solution: Volume Mounts in Docker Compose

### For Production (VPS or managed hosting)

Edit your `docker-compose.prod.yml`:

```yaml
services:
  backend:
    image: <your-backend-image>
    volumes:
      # ⭐ CRITICAL: Mount persistent storage for images
      - ./data/images:/app/backend/static/images
      - ./instance:/app/instance
    environment:
      DATABASE_URL: ${DATABASE_URL}
      # ... other env vars
```

Then on your host:

```bash
# Create persistent directories
mkdir -p /srv/structured-docs/data/images
mkdir -p /srv/structured-docs/instance

# Ensure proper permissions
chmod 755 /srv/structured-docs/data/images
chmod 755 /srv/structured-docs/instance

# Restart containers with new config
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

### For Local Development

The local `docker-compose.yml` should already have this, but verify:

```yaml
services:
  backend:
    volumes:
      - ./data/images:/app/backend/static/images
      - ./instance:/app/instance
```

## Storage Locations (After Fix)

| Type | Inside Container | Host Path | Notes |
|------|-----------------|-----------|-------|
| Uploaded images | `/app/backend/static/images/` | `./data/images/` | Direct uploads via modal |
| Imported images | `/app/backend/static/images/imports/{doc_id}/` | `./data/images/imports/{doc_id}/` | From Word doc imports |
| Database | `/app/instance/` | `./instance/` | SQLite DB file |

## Verification Steps

After applying the fix:

```bash
# 1. Verify volumes are mounted
docker inspect <container-id> | grep -A 20 Mounts

# 2. Upload an image via the UI (should appear)

# 3. Restart the container
docker-compose restart backend

# 4. Check if images still appear (they should)

# 5. List files on host
ls -la ./data/images/
```

## Database vs Filesystem

**Current architecture:**
- Uploaded images: **Filesystem only** (no DB record, but present in `/api/images` scan)
- Imported images: **Both DB and Filesystem** (ImportImage records + files)

**Why this works:**
- `/api/images` endpoint scans filesystem recursively
- Returns all files it finds (regardless of DB state)
- Frontend displays them immediately
- Survives container restarts ✅ (if volumes mounted)

## Alternative: Cloud Storage (Future Improvement)

For true scalability without host volumes:

1. **AWS S3**: Upload images to S3 bucket, return pre-signed URLs
2. **S3-compatible object storage**: Similar behavior with persistent external storage
3. **Cloudinary**: Image hosting service with automatic optimization

This would require:
- Modifying `/api/images/upload` to write to S3-compatible storage instead of filesystem
- Updating `/api/import/*` endpoints to do the same
- Updating serving endpoints to redirect to cloud URLs

## Current Status

- ✅ Image upload/import logic: Working
- ✅ Image serving: Working (when files exist)
- ❌ **Persistence: Broken** (no volume mounts)
- ❌ **Production deployment**: Requires volume mount config

## Action Required on Production Server

**Status**: `docker-compose.prod.yml` is correctly configured with volume mounts.

**The issue on structureddocs.online is likely one of:**

1. **Container not using docker-compose**: If running with raw `docker run`, the volumes aren't mounted
   - **Fix**: Use `docker-compose -f docker-compose.prod.yml up -d` instead

2. **Host directories missing or read-only**: 
   - **Verify**:
     ```bash
     ls -la /srv/structured-docs/data/images 2>/dev/null || echo "Directory doesn't exist"
     ls -la /srv/structured-docs/instance 2>/dev/null || echo "Directory doesn't exist"
     ```
   - **Fix**:
     ```bash
     mkdir -p /srv/structured-docs/data/images
     mkdir -p /srv/structured-docs/instance
     chmod 755 /srv/structured-docs/data/images
     chmod 755 /srv/structured-docs/instance
     chown appuser:appgroup /srv/structured-docs/data/images  # if running as non-root
     ```

3. **Wrong docker-compose file being used**: 
   - **Verify**: Check which docker-compose file is being used to start the container
   - **Fix**: Ensure you're using `docker-compose.prod.yml` with correct paths

4. **Volume paths are relative**:
   - `./data/images` is relative to where docker-compose is running from
   - **Verify**: Check the working directory when docker-compose starts
   - **Fix**: Use absolute paths in docker-compose: `/srv/structured-docs/data/images:/app/backend/static/images`

## Next Steps

1. **Check current deployment**: Verify which docker-compose or docker run command is active
2. **Verify volumes exist**: Check if `/srv/structured-docs/data/images` exists on the host
3. **Ensure permissions**: The container user must be able to write to the volume
4. **Restart with correct config**: Use `docker-compose.prod.yml` with absolute paths
5. **Test**: Upload an image, restart container, verify image persists
