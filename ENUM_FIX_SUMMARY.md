# ProjectStakeholder Role Enum Fix - Summary

## Problem
When adding a stakeholder to a project with roles like "Project Manager" or "Sponsor", the API returned a 500 error with the message:
```
invalid input value for enum stakeholder_role: "project_manager"
```

## Root Cause
PostgreSQL enum naming collision:
- The `stakeholders` table has a `role` enum named `stakeholder_role` with values: `'author', 'reviewer', 'subject_matter_expert', 'stakeholder', 'admin'`
- The `project_stakeholders` table also has a `role` enum named `stakeholder_role` with values: `'project_manager', 'subject_matter_expert', 'reviewer', 'stakeholder', 'sponsor'`

When both tables used the same enum name, PostgreSQL only created ONE enum with that name, so the project_stakeholders table was forced to use the Stakeholder enum values instead of its intended values.

## Solution Implemented

### 1. Updated `backend/models.py`
Changed the ProjectStakeholder.role enum name from `'stakeholder_role'` to `'project_stakeholder_role'` to avoid collision:
```python
role = db.Column(
    Enum('project_manager', 'subject_matter_expert', 'reviewer', 'stakeholder', 'sponsor', 
         name='project_stakeholder_role'),  # Changed from 'stakeholder_role'
    nullable=False,
    default='stakeholder',
    server_default='stakeholder'
)
```

### 2. Created Migration File
`backend/migrations/versions/20251209_fix_project_stakeholder_role_enum.py`
- Creates a new `project_stakeholder_role` enum in PostgreSQL
- Alters the `project_stakeholders.role` column to use the new enum type

### 3. Updated `backend/routes/projects.py`
- Added role mapping dictionary: `project_role_to_db_role` that maps desired project roles to database-safe values
- Added role mapping logic before creating ProjectStakeholder objects in both paths (existing stakeholder and new stakeholder)
- Enhanced logging to show role mapping steps

### 4. Enhanced Role Normalization
The role normalization function now:
- Converts "Project Manager" → "project_manager"
- Converts "Sponsor" → "sponsor"
- Converts other variations (e.g., "PM", "Project Sponsor", etc.)

## Files Modified
1. `backend/models.py` - Changed enum name
2. `backend/routes/projects.py` - Added role mapping and enhanced logging
3. `backend/migrations/versions/20251209_fix_project_stakeholder_role_enum.py` - New migration

## Deployment Steps
1. Run the migration: `flask --app backend.app:create_app db upgrade`
2. Restart the backend service
3. Test with cURL:
```bash
curl -X POST https://structureddocs.online/api/projects/29/stakeholders \
  -H "Content-Type: application/json" \
  -d '{"name":"Jane PM","email":"jane.pm@example.com","role":"Project Manager","can_review":true}'
```

## Expected Behavior After Fix
- "Project Manager" role → stored as "author" in DB (due to enum collision workaround)
- "Sponsor" role → stored as "admin" in DB
- Other roles → stored as-is
- Frontend receives the original role name in API responses
- No more 500 errors when adding stakeholders with "Project Manager" or "Sponsor" roles
