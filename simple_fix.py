print("Python is working")
print("Attempting database fix...")

import sqlite3
import os

# Fix both database locations
db_paths = ['instance/structured_docs.db', 'backend/instance/structured_docs.db']

for db_path in db_paths:
    if os.path.exists(db_path):
        print(f"Found database: {db_path}")
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check current records
            cursor.execute('SELECT id, status, review_step FROM import_documents')
            records = cursor.fetchall()
            print(f"Found {len(records)} records in {db_path}")
            
            # Show current records
            for record in records:
                print(f"  Record {record[0]}: status='{record[1]}', review_step='{record[2]}'")
            
            # Update invalid status values
            cursor.execute('UPDATE import_documents SET status = "approved" WHERE status = "sme_approved"')
            updated = cursor.rowcount
            print(f'Updated {updated} records with sme_approved status in {db_path}')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error with {db_path}: {e}")
    else:
        print(f"Database not found: {db_path}")

print("Database fix complete")
