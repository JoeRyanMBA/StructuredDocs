# Image Storage Troubleshooting Guide

## Problem
Word documents import successfully but **150 images show as "files missing"** - images are not persisting.

## Root Cause
Images are being stored to **ephemeral local container storage** instead of **Digital Ocean Spaces**. When the container restarts or redeploys, all local files are lost.

## Solution Steps

### 1. Check Current Storage Configuration

Visit this URL in your browser (replace with your actual domain):
```
https://your-app.ondigitalocean.app/diagnostics/storage
```

This will show you:
- ✅ Which storage backend is active (should be "Digital Ocean Spaces")
- ✅ Which environment variables are set/missing
- ✅ Whether boto3 is installed
- ✅ Specific recommendations for your setup

### 2. Configure Digital Ocean Spaces Environment Variables

In your **Digital Ocean App Platform** dashboard:

1. Go to your app → **Settings** → **App-Level Environment Variables**
2. Add these **4 required variables**:

   ```
   SPACES_BUCKET=1docimages
   SPACES_REGION=nyc3
   SPACES_ACCESS_KEY=<your-access-key>
   SPACES_SECRET_KEY=<your-secret-key>
   ```

3. **IMPORTANT**: 
   - Use **App-Level** variables, NOT component-level
   - Do NOT set `IMAGE_STORAGE_ROOT` when using Spaces
   - Keys are from Digital Ocean → API → Spaces Keys

4. Click **Save** and wait for automatic redeployment

### 3. Verify Spaces Storage is Active

After redeployment:

1. Visit `/diagnostics/storage` again
2. Confirm it shows:
   ```json
   {
     "storage_backend": {
       "active_type": "SpacesStorage",
       "details": {
         "type": "Digital Ocean Spaces",
         "bucket": "1docimages",
         "region": "nyc3"
       }
     }
   }
   ```

### 4. Clear Database and Re-Import

Since the previous images are lost:

1. Clear your database (or just delete the failed import records)
2. Import your Word document again
3. Images should now save to Spaces and persist across redeploys

### 5. Verify Images in Spaces Dashboard

Check your Digital Ocean Spaces dashboard:
- Go to Spaces → 1docimages
- You should see files in `images/imports/{doc_id}/`
- Total size should show actual data (not 0 Bytes)

## Expected Image URLs

### Before (Local Storage - EPHEMERAL):
```
/images/imports/120/image39_1b4569e8.png
```
**Problem**: Lost on redeploy ❌

### After (Spaces - PERSISTENT):
```
https://1docimages.nyc3.digitaloceanspaces.com/images/imports/120/image39_1b4569e8.png
```
**Solution**: Persistent across redeploys ✅

## Troubleshooting

### If `/diagnostics/storage` shows "LocalStorage"
- **Cause**: Spaces environment variables not set or incomplete
- **Fix**: Add all 4 Spaces variables (see step 2)

### If `/diagnostics/storage` shows "boto3 not available"
- **Cause**: boto3 not installed in production
- **Fix**: Ensure `requirements.txt` contains `boto3>=1.34.0` and redeploy

### If images still don't persist after configuring Spaces
1. Check application logs during import:
   - Look for "Using storage backend: SpacesStorage"
   - Look for "Saved to storage: https://..."
   - Look for any "Failed to save to storage" errors
2. Verify Spaces credentials have write permissions
3. Check Spaces CORS settings if browser errors occur

## Related Files
- `backend/utils/storage.py` - Storage backend implementation
- `backend/utils/image_handler.py` - Image processing and storage
- `backend/routes/diagnostics.py` - Diagnostics endpoint
- `APP_PLATFORM_CONFIG.md` - Environment variable documentation
- `SPACES_SETUP.md` - Digital Ocean Spaces setup guide
