# Collections Dashboard Edit Button Fix

## Problem
When clicking the "Edit" button on a collection card in the Collections Dashboard, users were being taken to the Start Page dashboard instead of an edit interface.

## Root Cause
The `editCollection` method in `CollectionsDashboard.vue` was trying to navigate to a non-existent route: `/collections/${collection.id}/edit`

## Solution Implemented

### 1. Fixed Navigation Route
Updated the `editCollection` method to navigate to the existing `/organize/${collection.id}` route with an `edit=true` query parameter:

```javascript
editCollection(collection) {
  this.$router.push(`/organize/${collection.id}?edit=true`)
}
```

### 2. Enhanced Organize Component
Added edit mode detection and a collection properties edit panel in `Organize.vue`:

- **Edit Mode Detection**: Checks for `?edit=true` query parameter
- **Visual Indicator**: Changes header from "📋 Organize Collection" to "✏️ Edit Collection"
- **Edit Panel**: Shows collection name and form number fields for inline editing

### 3. Added Backend API Endpoint
Created a new PUT endpoint for updating individual collections:

```python
@collections_bp.route('/<int:collection_id>', methods=['PUT'])
def update_collection(collection_id):
    # Allows updating name, form_number, project_id, parent_id, position
    # Validates form_number uniqueness
    # Returns updated collection data
```

## Features Added

### Collection Properties Editing
When accessing a collection via the "Edit" button:
- ✅ Page title changes to "Edit Collection"
- ✅ Collection properties panel appears with editable fields:
  - Collection Name (auto-saves on blur)
  - Form Number (auto-saves on blur with uniqueness validation)
- ✅ All existing organize functionality remains available

### API Validation
- ✅ Form number uniqueness validation
- ✅ Proper error handling and user feedback
- ✅ Automatic saving on field blur

## User Experience

| Action | Before | After |
|--------|--------|-------|
| Click "Edit" button | Redirected to Start Page ❌ | Opens organize page in edit mode ✅ |
| Edit collection name | Not possible | Inline editing with auto-save ✅ |
| Edit form number | Not possible | Inline editing with validation ✅ |
| Organize topics | Not accessible | Full functionality available ✅ |

## Files Modified

1. **`frontend/src/views/CollectionsDashboard.vue`**
   - Fixed `editCollection` method routing
   - Added `?edit=true` query parameter

2. **`frontend/src/views/Organize.vue`**
   - Added edit mode detection
   - Added collection properties edit panel
   - Added `saveCollectionProperty` method
   - Enhanced styling for edit interface

3. **`backend/routes/collections.py`**
   - Added PUT endpoint for updating individual collections
   - Added validation for form_number uniqueness
   - Added error handling

## Testing

To test the fix:
1. Go to Collections Dashboard
2. Click "Edit" on any collection card
3. Verify you're taken to the organize page with "Edit Collection" header
4. Verify the collection properties panel appears
5. Try editing the collection name and form number
6. Verify auto-save functionality works

The Edit button now properly functions and provides a comprehensive editing interface for collections!
