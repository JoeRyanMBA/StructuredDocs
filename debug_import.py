import sqlite3
import os

def fix_enum_values():
    """Fix invalid enum values in the import_documents table"""
    
    # Try different database locations
    possible_paths = [
        os.path.join(os.path.dirname(__file__), 'backend', 'instance', 'structured_docs.db'),
        os.path.join(os.path.dirname(__file__), 'instance', 'structured_docs.db'),
        'structured_docs.db'
    ]
    
    db_path = None
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("Database file not found! Tried:")
        for path in possible_paths:
            print(f"  {path}")
        return
    
    print(f"Using database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # First, check what records exist
        cursor.execute("SELECT id, status, review_step FROM import_documents;")
        records = cursor.fetchall()
        
        print(f"Found {len(records)} import document records:")
        print("Before fix:")
        for record_id, status, review_step in records:
            print(f"  ID {record_id}: status='{status}', review_step='{review_step}'")
        
        # Fix invalid status values - map 'sme_approved' status to 'approved'
        cursor.execute("UPDATE import_documents SET status = 'approved' WHERE status = 'sme_approved';")
        updated_status = cursor.rowcount
        
        # The review_step enum should be okay as 'sme_approved' is valid there
        # But let's check for any other invalid status values
        cursor.execute("UPDATE import_documents SET status = 'staging' WHERE status NOT IN ('staging', 'approved', 'rejected');")
        other_status = cursor.rowcount
        
        # Commit the changes
        conn.commit()
        
        print(f"\nFixed {updated_status} records with 'sme_approved' status")
        print(f"Fixed {other_status} records with other invalid status values")
        
        # Show the results
        cursor.execute("SELECT id, status, review_step FROM import_documents;")
        records = cursor.fetchall()
        
        print("\nAfter fix:")
        for record_id, status, review_step in records:
            print(f"  ID {record_id}: status='{status}', review_step='{review_step}'")
            
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_enum_values()
