# Import Issues - Root Causes & Fixes

## Issues Found

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

### 3. **Missing Content in Import** - Possible Causes

If your import still has missing content after these fixes, it's likely:

#### A. **No H1 Headings in Word Document**
The import handler looks for Heading 1 (`#`) level headings to create topics. If your Word document only has body text or Heading 2+, the content won't be extracted.

**Check**: Open your Word document and verify it has proper H1 headings

**Solution**: 
- Use Styles > Heading 1 for main sections
- Re-import the document

#### B. **Pandoc Conversion Failed**
Pandoc converts .docx to Markdown. If it fails, content is lost.

**Check on server**:
```bash
cd /opt/structureddocs
docker compose logs app | grep -i "pandoc"
docker compose exec -T app pandoc --version
```

**Solution**: 
- If Pandoc isn't installed, check Dockerfile has: `RUN apt-get install -y pandoc`
- Rebuild the Docker image if needed

#### C. **Word Document Structure Not Supported**
Some complex Word documents with:
- Tables without recognizable structure
- Nested content boxes
- Complex formatting

may not import cleanly.

**Solution**: Simplify the Word document structure

### 4. **Missing Images** - Possible Causes

If images aren't appearing after import:

#### A. **Volume Mount Not Working**
```bash
# Check on server:
ls -la /opt/structureddocs/data/images/

# Should show imported image subdirectories like:
# imports/
# └── 123/  (where 123 is the import document ID)
```

#### B. **Image Extraction Failed**
```bash
# Check logs:
cd /opt/structureddocs
docker compose logs app | grep -i "image"
```

#### C. **ImageHandler Permission Issues**
```bash
# Fix permissions on server:
chmod 777 /opt/structureddocs/data/images
```

## Next Steps

### 1. **Try Importing Again**
Now that the database and volumes are fixed, try importing a Word document again.

### 2. **Monitor the Import**
```bash
# Watch logs in real-time:
ssh root@64.225.29.187 "cd /opt/structureddocs && docker compose logs -f app"
```

### 3. **Check Results**
After import completes, check:
```bash
# Database tables created?
ssh root@64.225.29.187 "ls -lah /opt/structureddocs/instance/"

# Images stored?
ssh root@64.225.29.187 "ls -la /opt/structureddocs/data/images/"

# Content and images in DB?
# Check via the UI at https://structureddocs.online
```

### 4. **Diagnostic Script**
To check why a specific import failed, you can use:
```bash
python scripts/diagnose_server_import.py  # (when run in Flask context)
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
