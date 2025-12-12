# Image Extraction Diagnostics & Error Handling Improvement

## Problem Identified
After importing documents, many images show as placeholders (gray SVG) instead of actual images. The browser console shows 404 errors for these missing files. Most images load correctly, but many fail—same pattern across multiple imports.

**Root Cause:** The image extraction process during import is failing silently for ~70% of images. Database records are created for all images (because they're listed in the markdown), but many actual files are never written to disk.

## Previous Issues
1. **Silent failures**: `_optimize_image()` method caught exceptions but didn't report failures
2. **No status feedback**: Calling code didn't know if image storage succeeded or failed  
3. **No diagnostics**: No checks for disk space, permissions, or write failures
4. **Poor logging**: Errors were logged but not consistently, making it hard to diagnose

## Changes Made

### 1. Enhanced `_optimize_image()` Method
- Now **returns boolean** (True/False) instead of silently failing
- **Verifies file exists** after write operation
- **Reports failures explicitly** with clear error messages
- **Better fallback handling** with success/failure tracking

### 2. Improved `_store_single_image()` Method
- **Checks return status** from `_optimize_image()`
- **Verifies directories exist** before writing
- **Validates backend file exists** after write (CRITICAL check)
- **Better error handling** with full traceback logging (`exc_info=True`)
- **Handles frontend copy failures** gracefully (frontend is optional)

### 3. Added Pre-flight Checks in `extract_and_store_images()`
- **Disk space check**: Verifies at least 100 MB available
- **Permission check**: Tests write permission before processing
- **Success/failure tracking**: Counts successful and failed images
- **Summary logging**: Reports final statistics (e.g., "5 succeeded, 75 failed")

### 4. Better Exception Handling
- Added `timeout=30` to subprocess calls (EMF conversion)
- Added `exc_info=True` to error logging for full stack traces
- More descriptive error messages at each step

## Diagnostic Output
After these changes, the logs will show:
```
💾 Disk space available: 45.23 GB
✅ Write permissions verified for /path/to/images
🔍 Found 80 images to process (after EMF conversion)
💾 Storing image: image1.png -> image1_abc12345.png
   Backend path: /path/to/backend/image1_abc12345.png
   Frontend path: /path/to/frontend/image1_abc12345.png
   ✅ Ensured backend and frontend directories exist
   🖼️  Opening image: /tmp/image1.png
   💾 Saving optimized image to: /path/to/backend/image1_abc12345.png
   ✅ Successfully saved optimized image
   ✅ Copied to frontend
✅ Stored image: image1_abc12345.png (1920x1080, 245678 bytes, backend_exists=True)
...
📊 Image extraction summary: 80 succeeded, 0 failed out of 80 total
```

Or if failures occur:
```
📊 Image extraction summary: 5 succeeded, 75 failed out of 80 total
```

## Next Steps
1. **Deploy changes** to production
2. **Import a document** with images
3. **Check logs** for the summary line and any error messages
4. **Identify root cause**:
   - If disk space error: Need to add disk cleanup/monitoring
   - If permission error: Need to fix directory permissions
   - If corruption errors: Need to handle malformed images gracefully
   - If timeout errors: Need to increase subprocess timeout
5. **Address root cause** with targeted fix

## Testing
After deployment, look for these patterns in logs:
- **`Disk space available`**: Shows available space
- **`Write permissions verified`**: Confirms can write
- **`Image extraction summary`**: Shows success/fail counts
- **`CRITICAL` errors**: Any file write failures
- **`PermissionError`, `OSError`, `IOError`**: System-level issues

If summary shows failures, the specific error messages above it will indicate why.
