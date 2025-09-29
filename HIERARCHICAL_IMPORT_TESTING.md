# Hierarchical Import Testing Guide

This document provides step-by-step instructions to test the new hierarchical import functionality.

## Overview

The hierarchical import feature allows users to import Word documents while preserving their heading structure. When enabled, H1, H2, and H3 headings are maintained as parent-child relationships in a collection, rather than being flattened to individual topics.

## Changes Made

### Backend Changes (`backend/routes/import_handler.py`)

1. **Enhanced `_upload_file` function**:
   - Added `preserve_hierarchy` parameter parsing from form data
   - Routes hierarchical imports through special logic

2. **Modified `_import_as_topics` function**:
   - When `preserve_hierarchy=True`, automatically creates a collection instead of individual topics
   - Uses existing `_parse_hierarchical_structure` function
   - Creates topics with proper parent-child relationships in `collection_topic_tree` table

3. **Updated `_parse_and_store` function**:
   - Conditionally preserves or promotes heading levels based on `preserve_hierarchy` parameter
   - For Word documents: preserves H1, H2, H3 levels when hierarchy is enabled
   - For Markdown documents: prevents promotion of H2/H3 to H1 when hierarchy is enabled

### Frontend Changes (`frontend/src/views/ImportView.vue`)

1. **Added Advanced Options Section**:
   - Appears only for "Individual Topics" import type
   - Checkbox for "Preserve Document Hierarchy"
   - Clear explanation of functionality

2. **Enhanced Form Submission**:
   - Includes `preserve_hierarchy` parameter in form data
   - Updated response handling for hierarchical imports

3. **Improved Navigation**:
   - Hierarchical topic imports redirect to Organize page (like collections)
   - Regular topic imports still go to Import Review page

## Testing Instructions

### Prerequisites

1. Start the backend server:

   ```bash
   cd /workspaces/StructuredDocs
   python3 start.py
   ```

2. Start the frontend development server:

   ```bash
   cd /workspaces/StructuredDocs/frontend
   npm run dev
   ```

3. Ensure you have at least one project created (required for collections)

### Test Cases

#### Test Case 1: Regular Topic Import (Baseline)

1. Navigate to Import page
2. Select "Individual Topics"
3. Keep "Preserve Document Hierarchy" **unchecked**
4. Upload the test document: `test_employee_handbook.md`
5. Click "Start Import"

**Expected Result**:

- Redirected to Import Review page
- All headings promoted to H1 level
- Creates individual topics: "Employee Handbook", "Getting Started", "Your First Day", etc.
- No hierarchical relationships

#### Test Case 2: Hierarchical Topic Import (New Feature)

1. Navigate to Import page
2. Select "Individual Topics"
3. **Check** "Preserve Document Hierarchy"
4. Upload the test document: `test_employee_handbook.md`
5. Click "Start Import"

**Expected Result**:

- Redirected to Organize page for auto-created collection
- Collection name: "Document Import - test_employee_handbook.md"
- Hierarchical structure preserved:

  ```text
  └─ Employee Handbook (H1)
     ├─ Getting Started (H2)
     │  ├─ Your First Day (H3)
     │  ├─ Office Tour (H3)
     │  └─ Meeting Your Team (H3)
     ├─ Policies and Procedures (H2)
     │  ├─ Work Hours (H3)
     │  ├─ Time Off Policy (H3)
     │  └─ Code of Conduct (H3)
     └─ Benefits and Compensation (H2)
        ├─ Health Insurance (H3)
        └─ Retirement Plans (H3)
  └─ IT Resources (H1)
     ├─ Equipment and Software (H2)
     │  ├─ Laptop and Hardware (H3)
     │  └─ Software Access (H3)
     └─ Security Policies (H2)
        ├─ Password Requirements (H3)
        └─ Data Protection (H3)
  ```

#### Test Case 3: Collection Import (Comparison)

1. Navigate to Import page
2. Select "Collection (Document)"
3. Fill in collection details
4. Upload the same test document
5. Click "Start Import"

**Expected Result**:

- Should produce the same hierarchical structure as Test Case 2
- But with user-specified collection name and details

### Verification Steps

For each test case, verify:

1. **Navigation**: Correct redirection after import
2. **Topic Creation**: Correct number of topics created
3. **Hierarchy**: Parent-child relationships preserved (for hierarchical imports)
4. **Content**: Topic content properly extracted and cleaned
5. **Organization**: Topics appear correctly on Organize page

### API Testing

You can also test the API directly using the provided test script:

```bash
cd /workspaces/StructuredDocs
python3 test_hierarchical_api.py
```

This script tests the backend API with the hierarchical import parameters.

### Debugging

If issues occur, check:

1. **Backend Logs**: Look for "HIERARCHICAL_TOPIC_IMPORT" log messages
2. **Database**: Check `collections` and `collection_topic_tree` tables
3. **Network Tab**: Verify form data includes `preserve_hierarchy=true`
4. **Console**: Check for JavaScript errors in browser console

### Expected Database Changes

For hierarchical imports, the following should be created:

1. **Collection record** in `collections` table with auto-generated name
2. **Topic records** in `topics` table for each heading
3. **Hierarchy records** in `collection_topic_tree` table with `parent_topic_id` relationships

## Test Document Structure

The `test_employee_handbook.md` document has this structure:

- 2 H1 headings (Employee Handbook, IT Resources)
- 5 H2 headings (Getting Started, Policies and Procedures, Benefits and Compensation, Equipment and Software, Security Policies)
- 11 H3 headings (various sub-topics)

This should result in 18 total topics with proper parent-child relationships when hierarchy is preserved.

## Success Criteria

✅ **Feature Complete** when:

1. Checkbox appears and functions correctly in UI
2. Hierarchical imports create collections with proper relationships
3. Regular imports continue to work as before (backward compatibility)
4. Topics display correctly in hierarchical structure on Organize page
5. No errors in backend or frontend logs
6. All existing functionality remains unaffected
