# 🖼️ Image Display Issue - Diagnosis & Fix Guide

## Summary

You've reported that after importing a Word document as a collection, images are not displaying when you browse images. Instead, you see just the filename without the image thumbnail/preview.

**Root Cause**: Image files are not being saved to disk during the import process.

## What Should Happen

When you import a Word document:
1. ✅ Pandoc extracts images from the DOCX file
2. ✅ The app stores them to disk at: `backend/static/images/imports/{doc_id}/`
3. ✅ Database records (ImportImage) are created with file paths
4. ✅ Frontend displays thumbnails from the stored files

**Currently**: Steps 1-3 are either failing or incomplete, so step 4 can't load the images.

## How to Diagnose

### Option 1: Run the Verification Script

```bash
cd /workspaces/StructuredDocs
python3 verify_import_images.py
```

This will check:
- ✓ Are ImportImage records in the database?
- ✓ Are image files saved to disk?
- ✓ Are API routes configured correctly?

### Option 2: Monitor Backend Logs

1. Start the app in a terminal where you can see logs
2. Upload a Word document to import
3. Watch the logs for messages containing:
   - `PANDOC:` - Shows image extraction
   - `Storing image:` - Shows image storage
   - Any error messages starting with `❌`

## Common Issues & Solutions

### Issue: No ImportImage records in database

**Cause**: Images weren't imported or database save failed

**Solution**:
1. Check if the Word document actually contains images
2. Verify the import process completed successfully
3. Check backend logs for errors during import
4. Try re-importing the document

### Issue: ImportImage records exist but files are missing

**Cause**: Image storage to disk failed (likely a file system permission issue)

**Solution**:
1. Check directory permissions: `ls -la /workspaces/StructuredDocs/backend/static/images/`
2. Ensure directory is writable:
   ```bash
   mkdir -p /workspaces/StructuredDocs/backend/static/images/imports
   chmod 755 /workspaces/StructuredDocs/backend/static/images/imports
   ```
3. Verify disk space: `df -h /workspaces/StructuredDocs/`
4. Try re-importing after fixing permissions

### Issue: Pandoc isn't extracting images

**Cause**: Pandoc command failed or images are in unsupported format

**Solution**:
1. Check that Pandoc is installed: `pandoc --version`
2. Verify the Word document opens correctly in Word
3. Check if images are embedded (not linked)
4. Try a different Word document with simple images

##Changes Made to Improve Diagnostics

I've updated the codebase with better logging and error handling:

### 1. Enhanced Image Extraction Logging
- **File**: `backend/routes/import_handler.py`
- **Change**: Added detailed logging of Pandoc output and extracted files
- **Benefit**: You can now see exactly what images Pandoc is extracting

### 2. Better Directory Creation
- **File**: `backend/utils/image_handler.py`
- **Change**: Improved error handling when creating image directories
- **Benefit**: Errors creating directories will be logged clearly

### 3. Individual File Logging
- **File**: `backend/utils/image_handler.py`
- **Change**: Each image storage attempt is now logged in detail
- **Benefit**: You can trace exactly where storage fails

### 4. Helper Scripts
- **New**: `verify_import_images.py` - Comprehensive diagnostics script
- **New**: `check_image_state.py` - Quick database and disk check

## Next Steps

1. **Run verification**: `python3 verify_import_images.py`
2. **Try importing again** and watch the backend logs
3. **Report findings**: The diagnostic script output and logs will help identify the exact issue
4. **Check permissions**: Ensure the backend/static/images directory is writable

## Additional Resources

- Image Upload Guide: `IMAGE_UPLOAD_GUIDE.md`
- Previous Fix Summary: `IMAGE_DISPLAY_FIX_SUMMARY.md`
- Complete Fix Documentation: `IMAGE_FIX_COMPLETE.md`

## Questions?

If the diagnostics show the issue is still unclear, provide:
1. Output from `verify_import_images.py`
2. Backend logs showing the import process
3. The Word document you're trying to import
4. Output of file system checks
