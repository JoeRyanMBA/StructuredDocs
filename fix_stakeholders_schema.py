#!/usr/bin/env python3
"""
Quick fix for stakeholders table schema
"""
import psycopg2
import sys

# PostgreSQL connection details
PG_CONFIG = {
    'host': 'JoeRyanMBA-4757.postgres.pythonanywhere-services.com',
    'port': 14757,
    'database': 'structured_docs',
    'user': 'super',
    'password': 'Picklehead1!'
}

def fix_stakeholders_table():
    """Fix the stakeholders table schema"""
    print("🔧 Fixing stakeholders table schema...")
    
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        
        # Check current columns in stakeholders table
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'stakeholders' 
            ORDER BY ordinal_position;
        """)
        
        current_columns = [(row[0], row[1]) for row in cursor.fetchall()]
        print(f"Current stakeholders columns: {[col[0] for col in current_columns]}")
        
        # Add missing columns if they don't exist
        missing_columns = [
            ('role', 'VARCHAR(50)'),
            ('phone', 'VARCHAR(20)'),
            ('department', 'VARCHAR(100)'),
            ('title', 'VARCHAR(100)'),
            ('notes', 'TEXT')
        ]
        
        for column_name, column_type in missing_columns:
            if column_name not in [col[0] for col in current_columns]:
                try:
                    cursor.execute(f"ALTER TABLE stakeholders ADD COLUMN {column_name} {column_type};")
                    conn.commit()
                    print(f"  ✅ Added {column_name} column")
                except Exception as e:
                    print(f"  ⚠️  Failed to add {column_name}: {e}")
                    conn.rollback()
            else:
                print(f"  ✅ {column_name} column already exists")
        
        # Check final schema
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'stakeholders' 
            ORDER BY ordinal_position;
        """)
        
        final_columns = [(row[0], row[1]) for row in cursor.fetchall()]
        print(f"\nFinal stakeholders columns: {[col[0] for col in final_columns]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to fix stakeholders table: {e}")
        return False

def run_simplified_test():
    """Run a simplified test to verify the fix"""
    print("\n🧪 Running simplified test...")
    
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        
        # Test stakeholder insertion
        cursor.execute("""
            INSERT INTO stakeholders (name, email, role, expertise_areas, active, created_at) 
            VALUES (%s, %s, %s, %s, %s, NOW()) 
            RETURNING id
        """, ('Test Stakeholder', 'test@example.com', 'reviewer', 'Testing', True))
        
        stakeholder_id = cursor.fetchone()[0]
        print(f"  ✅ Successfully inserted stakeholder (ID: {stakeholder_id})")
        
        # Clean up
        cursor.execute("DELETE FROM stakeholders WHERE id = %s", (stakeholder_id,))
        conn.commit()
        print("  ✅ Test data cleaned up")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"  ❌ Stakeholder test failed: {e}")
        return False

def main():
    print("🛠️  Stakeholders Table Schema Fix")
    print("=" * 40)
    
    if fix_stakeholders_table():
        if run_simplified_test():
            print("\n✅ Stakeholders table is now properly configured!")
            print("You can now run the full database test again:")
            print("python3 test_database_configuration.py")
            return 0
        else:
            print("\n❌ Test still failing after fix")
            return 1
    else:
        print("\n❌ Failed to fix stakeholders table")
        return 1

if __name__ == "__main__":
    sys.exit(main())
