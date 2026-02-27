# Fix: Missing email_delivery_unavailable Column

## Problem
Review History page shows error:
```
psycopg2.errors.UndefinedColumn: column reviews.email_delivery_unavailable does not exist
```

This happens because the `Review` model in the code has a column that doesn't exist in your PostgreSQL database.

## Solution: Run Database Migration

Choose **one** of the following methods:

---

### Method 1: Python Migration Script (Recommended)

**On your production server**, run:

```bash
cd /path/to/StructuredDocs
python add_email_delivery_unavailable_column.py
```

This will:
- Check if the column already exists
- Add the column if missing
- Show success/error messages

---

### Method 2: Direct SQL Execution

**Connect to your PostgreSQL database** and run:

```bash
psql -h structureddocs-postgres-do-user-25179902-0.l.db.ondigitalocean.com \
     -U your_username \
     -d your_database \
     -f add_email_delivery_unavailable.sql
```

Or use a PostgreSQL GUI tool (pgAdmin, DBeaver, etc.) and execute the contents of `add_email_delivery_unavailable.sql`.

---

### Method 3: Manual SQL

If you have direct database access:

```sql
-- Add the missing column
ALTER TABLE reviews 
ADD COLUMN email_delivery_unavailable BOOLEAN NOT NULL DEFAULT FALSE;

-- Verify it was added
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name='reviews' 
AND column_name='email_delivery_unavailable';
```

---

## Verify the Fix

After running the migration:

1. **Refresh the Review History page** in your browser
2. The error should be gone
3. The page should display the review list

## What This Column Does

`email_delivery_unavailable` is a boolean flag that tracks when email delivery fails for a reviewer (e.g., bounce, invalid email, disabled notifications). This allows the system to:
- Stop sending emails to addresses that bounce
- Display appropriate UI warnings
- Track delivery issues for debugging

## If Migration Fails

If you get an error running the migration:

1. **Check database connection**: Ensure you can connect to PostgreSQL
2. **Check permissions**: Ensure your database user has `ALTER TABLE` permissions
3. **Check if column exists**: Run this query:
   ```sql
   SELECT column_name FROM information_schema.columns 
   WHERE table_name='reviews' AND column_name='email_delivery_unavailable';
   ```
   If it returns a row, the column already exists (migration not needed)

4. **Check for typos**: Ensure table name is `reviews` (lowercase)

## Need Help?

If migration fails with a specific error, share the error message for further assistance.
