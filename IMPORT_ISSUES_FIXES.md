# Import Issues - Root Causes & Fixes

## Root Cause Summary

The images appear in the Insert Image modal but show no thumbnails because:
1. **Image metadata is stored in database** ✅
2. **But image files can't be written to disk** ❌ 
3. **Cause: Volume mount permission denied** ❌ FIXED

## Issues Found & Fixed

### 1. **Database Connection Failed** ✅ FIXED
**Problem**: The `DATABASE_URL` was set to `sqlite:///instance/structured_docs.db` which is a relative path. Inside the Docker container, this was being interpreted as `/app/instance/instance/structured_docs.db` (doubled path).

**Error**: `unable to open database file`

**Fix Applied**:
```bash
# Changed from:
DATABASE_URL=sqlite:///instance/structured_docs.db

# To:
DATABASE_URL=sqlite:////opt/structureddocs/instance/structured_docs.db
```

Four slashes: `sqlite://` (protocol) + `//` (network location) + `/opt/structureddocs/instance/structured_docs.db` (absolute path)

### 2. **Volume Mounts Not Configured** ✅ FIXED
**Problem**: The original deployment script used `docker run` without volume mounts. This means:
- Images were stored inside the container (ephemeral)
- Database wasn't persisted
- Everything was lost on container restart

**Fix Applied**:
```yaml
# Updated docker-compose.yml includes:
volumes:
  - ./instance:/app/instance  # Database persists
  - ./data/images:/app/backend/static/images  # Images persist
```

### 3. **CRITICAL: Permission Denied on Volume Mount** ✅ FIXED
**Root Cause of Missing Thumbnails**: The container runs as user `appuser` (UID 1000), but the host directory `/opt/structureddocs/data/images/` had permissions `755` (owned by root). This caused:

```
❌ Permission denied: cannot write to /app/backend/static/images/
```

**Evidence**:
```bash
# Before fix - container couldn't write
docker exec app touch /app/backend/static/images/test.txt
# Error: Permission denied

# After fix - works fine
chmod 777 /opt/structureddocs/data/images
docker exec app touch /app/backend/static/images/test.txt
# Success
```

**Fix Applied**:
```bash
# On Digital Ocean server:
chmod 777 /opt/structureddocs/data/images
chmod 777 /opt/structureddocs/instance
```

**Updated Setup Script**: Now automatically sets correct permissions during initial setup

## Why This Caused Images to Show Without Thumbnails

1. **Import happens**: Pandoc converts Word doc to Markdown ✅
2. **ImageHandler extracts images** from the temp directory
3. **Attempts to save to** `/app/backend/static/images/imports/{doc_id}/image.png`
4. **Permission denied** ❌ - file write fails silently
5. **Database record still created** with image metadata ✅  
6. **But file doesn't exist on disk** ❌
7. **Frontend shows image in modal** (because metadata exists in DB)
8. **But no thumbnail** (because file doesn't exist to display)

## Next Steps

### 1. **Verify Fix on Server**
```bash
# Check permissions are correct:
ssh root@64.225.29.187 "ls -ld /opt/structureddocs/data/images /opt/structureddocs/instance"
# Should show: drwxrwxrwx (777 permissions)

# Verify container can write:
cd /opt/structureddocs
docker compose exec -T app bash -c 'touch /app/backend/static/images/test.txt && ls -la /app/backend/static/images/test.txt'
```

### 2. **Clear Old Data**
Delete the test files and any old image records:
```bash
ssh root@64.225.29.187 "rm /opt/structureddocs/data/images/*.txt"

# Optional: If you want to start fresh, delete the old database:
ssh root@64.225.29.187 "rm /opt/structureddocs/instance/structured_docs.db 2>/dev/null; echo 'Database cleared'"
```

### 3. **Try Importing Again**
Now import a Word document and the images should:
- ✅ Be extracted from the Word document
- ✅ Be written to `/opt/structureddocs/data/images/imports/{doc_id}/`
- ✅ Show thumbnails in the Insert Image modal
- ✅ Persist across container restarts

### 4. **Monitor Import**
Watch logs while importing:
```bash
ssh root@64.225.29.187 "cd /opt/structureddocs && docker compose logs -f app | grep -i 'image\|pandoc'"
```

### 5. **Verify Results**
After import:
```bash
# Check files were created:
ssh root@64.225.29.187 "find /opt/structureddocs/data/images -type f | head -10"

# Check they're accessible from frontend:
curl https://structureddocs.online/api/images | jq '.[] | select(.filename | contains("image40"))' 2>/dev/null
```

## Configuration Summary

Your updated `.env` file on the server should have:
```bash
PORT=8080
DATABASE_URL=sqlite:////opt/structureddocs/instance/structured_docs.db
ENABLE_BLUEPRINTS_FILE=.enable_blueprints
SECRET_KEY=change-to-random-value
EMAIL_PROVIDER=sendgrid
DEFAULT_FROM_EMAIL=no-reply@structureddocs.online
FRONTEND_URL=https://structureddocs.online
```

## Persistent Paths

All data now persists on the host at:
- **Images**: `/opt/structureddocs/data/images/`
- **Database**: `/opt/structureddocs/instance/structured_docs.db`
- **Blueprints**: `/opt/structureddocs/.enable_blueprints`

These survive container restarts and redeployments ✅
