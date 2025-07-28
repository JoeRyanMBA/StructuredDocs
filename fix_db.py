import sqlite3

# Fix both database locations
db_paths = ['instance/structured_docs.db', 'backend/instance/structured_docs.db']

for db_path in db_paths:
    try:
        print(f"Fixing database: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current records
        cursor.execute('SELECT id, status, review_step FROM import_documents')
        records = cursor.fetchall()
        print(f"Found {len(records)} records")
        
        # Update invalid status values
        cursor.execute('UPDATE import_documents SET status = "approved" WHERE status = "sme_approved"')
        updated = cursor.rowcount
        print(f'Updated {updated} records with sme_approved status')
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"Error with {db_path}: {e}")

print("Database fix complete")
