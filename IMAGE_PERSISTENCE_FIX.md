# Image Persistence Fix - Root Cause & Solution

## Problem
Images appeared in the Images Repository immediately after import, but disappeared after logging out and back in. Links, however, persisted correctly across logout/login.

## Root Cause
The backend endpoints were checking **whether image files exist on disk** before returning database records:

**Before (broken):**
- `/api/import/staging/{doc_id}/images` - Only returned images with files on disk
- `/api/images` - Only returned images with files on disk
- `/api/import/staging/{doc_id}/links` - Returned ALL database records (correct behavior)

**Result:**
- On initial import, images were loaded into Vue component state (in memory)
- On logout, Vue state was cleared
- On login, `loadImages()` was called which fetched from the API
- Since some image files are missing from disk (due to partial extraction during import), the endpoints returned empty arrays
- Vue state remained empty → images disappeared

**Links worked correctly** because the `/api/import/staging/{doc_id}/links` endpoint returns all database records regardless of file existence.

## Solution
Updated two backend endpoints to return ALL database records, matching how links work:

### 1. `/api/import/staging/{doc_id}/images` (import_handler.py)
- Now returns all `ImportImage` database records
- Still logs warnings if files are missing (for debugging)
- Frontend handles missing files gracefully with SVG placeholder

### 2. `/api/images` (images.py)  
- Now returns all imported images from database
- Includes `file_exists` flag so frontend can show placeholder if needed
- Falls back to database `file_size` if file can't be stat'd

## Why This Works
1. **Consistency**: Images now work like links - database is the source of truth
2. **Persistence**: Images survive logout/login because they're fetched from database each time
3. **Graceful degradation**: Frontend shows placeholder SVG if file is missing (already implemented)
4. **Debugging**: Warnings still logged for missing files to track extraction issues

## Related Issue
The root cause of missing image files is that some imports (63, 64) had partial image extraction - only a few of ~80 images were actually extracted to disk. This is a separate issue in the image extraction logic that should be investigated separately.

## Testing
To verify the fix:
1. Import a document with images
2. Images should appear in Images Repository
3. Logout of the app
4. Login back in
5. Images should still be visible (or show placeholder if files are missing)
6. No "disappearing images" issue after logout/login

## Frontend Behavior
- `getImageUrl()` constructs the image URL
- `loadImages()` fetches from `/api/import/history` and `/api/import/staging/{id}/images`
- `handleImageError()` shows SVG placeholder if image fails to load (HTTP 404, connection error, etc.)
- `copyImagePath()` allows users to copy image paths to insert into documents
