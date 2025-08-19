# Data Migration Instructions

## Problem Identified

The production PostgreSQL database on PythonAnywhere is missing the data that exists in the local SQLite database. This explains why:

- Topics page shows "Failed to load topics" 
- Tasks and Reviews are missing
- Only notifications were working

## Data Verification

Local SQLite database (`instance/structured_docs.db`) contains:
- **660 topics** (vs. 228 in CSV export - SQLite is more current)
- **2 tasks** 
- **19 reviews**
- **6 stakeholders**
- **42 projects** 
- **1 collection**

## Solution: Re-run Data Migration

### Step 1: Upload Migration Script
Upload `migrate_to_postgresql.py` to PythonAnywhere console.

### Step 2: Upload SQLite Database  
Upload the current `instance/structured_docs.db` file to PythonAnywhere (it has more recent data than the CSV exports).

### Step 3: Run Migration on PythonAnywhere

```bash
# In PythonAnywhere console
cd ~/StructuredDocs
python3 migrate_to_postgresql.py
```

The migration script will:
1. Connect to both SQLite and PostgreSQL databases
2. Migrate all tables in the correct order (respecting foreign key dependencies)
3. Handle duplicate key conflicts gracefully
4. Provide detailed progress output

### Step 4: Verify Migration

After migration, test these URLs on your live site:
- `https://yoursite.pythonanywhere.com/api/topics/` - Should show 660 topics
- `https://yoursite.pythonanywhere.com/api/tasks/` - Should show 2 tasks  
- `https://yoursite.pythonanywhere.com/api/reviews/` - Should show 19 reviews

### Step 5: Test Frontend

Visit your site and verify:
- All Topics page loads and shows topics
- Tasks section shows data
- Reviews section shows data
- Notifications still work (already fixed)

## Alternative: Temporary SQLite Solution

If PostgreSQL migration fails, you can temporarily switch the production app to use SQLite by uncommenting these lines in the app:

```python
# Local SQLite fallback for development (uncomment if PostgreSQL not accessible)
sqlite_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'structured_docs.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{sqlite_path}'
```

And commenting out the PostgreSQL configuration. However, PostgreSQL is recommended for production.

## Files to Upload

1. `app_final_with_notifications_fix.py` - Contains both notification fixes and API routing fixes
2. `migrate_to_postgresql.py` - Migration script
3. `instance/structured_docs.db` - Current SQLite database with all data
4. Updated frontend files (if needed)

## Expected Outcome

After successful migration:
- Topics page will load with 660 topics
- Tasks and Reviews will be visible
- All API endpoints will return data
- Notifications will continue working with proper date formatting
