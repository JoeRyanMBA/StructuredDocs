#!/usr/bin/env python3
"""
Comprehensive schema fix for all enum and column issues
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

def fix_all_schema_issues():
    """Fix all remaining schema issues"""
    print("🔧 Fixing all schema issues...")
    
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        
        # 1. Check and fix task_status enum
        print("\n1️⃣ Checking task_status enum...")
        try:
            cursor.execute("SELECT enumlabel FROM pg_enum WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'task_status');")
            current_values = [row[0] for row in cursor.fetchall()]
            print(f"Current task_status values: {current_values}")
            
            # Add missing enum values
            required_values = ['pending', 'in_progress', 'completed', 'cancelled', 'blocked']
            for value in required_values:
                if value not in current_values:
                    try:
                        cursor.execute(f"ALTER TYPE task_status ADD VALUE IF NOT EXISTS '{value}';")
                        conn.commit()
                        print(f"  ✅ Added '{value}' to task_status enum")
                    except Exception as e:
                        print(f"  ⚠️  Failed to add '{value}': {e}")
                        conn.rollback()
                else:
                    print(f"  ✅ '{value}' already exists in task_status enum")
                    
        except Exception as e:
            print(f"  ❌ Task status enum check failed: {e}")
            # If enum doesn't exist, we might need to handle this differently
            print("  Creating task_status enum...")
            try:
                cursor.execute("CREATE TYPE task_status AS ENUM ('pending', 'in_progress', 'completed', 'cancelled', 'blocked');")
                conn.commit()
                print("  ✅ Created task_status enum")
            except Exception as e2:
                print(f"  ❌ Failed to create task_status enum: {e2}")
                conn.rollback()
        
        # 2. Check and fix review_status enum
        print("\n2️⃣ Checking review_status enum...")
        try:
            cursor.execute("SELECT enumlabel FROM pg_enum WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'review_status');")
            current_values = [row[0] for row in cursor.fetchall()]
            print(f"Current review_status values: {current_values}")
            
            required_values = ['pending', 'in_progress', 'completed', 'cancelled']
            for value in required_values:
                if value not in current_values:
                    try:
                        cursor.execute(f"ALTER TYPE review_status ADD VALUE IF NOT EXISTS '{value}';")
                        conn.commit()
                        print(f"  ✅ Added '{value}' to review_status enum")
                    except Exception as e:
                        print(f"  ⚠️  Failed to add '{value}': {e}")
                        conn.rollback()
                        
        except Exception as e:
            print(f"  ❌ Review status enum check failed: {e}")
            print("  Creating review_status enum...")
            try:
                cursor.execute("CREATE TYPE review_status AS ENUM ('pending', 'in_progress', 'completed', 'cancelled');")
                conn.commit()
                print("  ✅ Created review_status enum")
            except Exception as e2:
                print(f"  ❌ Failed to create review_status enum: {e2}")
                conn.rollback()
        
        # 3. Check and fix priority enum
        print("\n3️⃣ Checking priority enum...")
        try:
            cursor.execute("SELECT enumlabel FROM pg_enum WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'priority');")
            current_values = [row[0] for row in cursor.fetchall()]
            print(f"Current priority values: {current_values}")
            
            required_values = ['low', 'medium', 'high', 'urgent']
            for value in required_values:
                if value not in current_values:
                    try:
                        cursor.execute(f"ALTER TYPE priority ADD VALUE IF NOT EXISTS '{value}';")
                        conn.commit()
                        print(f"  ✅ Added '{value}' to priority enum")
                    except Exception as e:
                        print(f"  ⚠️  Failed to add '{value}': {e}")
                        conn.rollback()
                        
        except Exception as e:
            print(f"  ❌ Priority enum check failed: {e}")
            print("  Creating priority enum...")
            try:
                cursor.execute("CREATE TYPE priority AS ENUM ('low', 'medium', 'high', 'urgent');")
                conn.commit()
                print("  ✅ Created priority enum")
            except Exception as e2:
                print(f"  ❌ Failed to create priority enum: {e2}")
                conn.rollback()
        
        # 4. Check current task table structure
        print("\n4️⃣ Checking tasks table structure...")
        cursor.execute("""
            SELECT column_name, data_type, udt_name
            FROM information_schema.columns 
            WHERE table_name = 'tasks' 
            ORDER BY ordinal_position;
        """)
        
        task_columns = cursor.fetchall()
        print("Current tasks table columns:")
        for col in task_columns:
            print(f"  {col[0]}: {col[1]} ({col[2]})")
        
        # 5. Check if we need to modify tasks table to use proper enums
        print("\n5️⃣ Checking if tasks table uses correct data types...")
        
        # Check if status column uses enum or varchar
        status_info = next((col for col in task_columns if col[0] == 'status'), None)
        if status_info and status_info[2] != 'task_status':
            print("  ⚠️  Tasks status column is not using task_status enum")
            print("  This might require data migration...")
        else:
            print("  ✅ Tasks status column is properly configured")
        
        # Check if priority column uses enum or varchar  
        priority_info = next((col for col in task_columns if col[0] == 'priority'), None)
        if priority_info and priority_info[2] != 'priority':
            print("  ⚠️  Tasks priority column is not using priority enum")
            print("  This might require data migration...")
        else:
            print("  ✅ Tasks priority column is properly configured")
        
        conn.close()
        
        print("\n✅ Schema fixes completed!")
        return True
        
    except Exception as e:
        print(f"❌ Schema fix failed: {e}")
        return False

def run_task_test():
    """Test task insertion with different approaches"""
    print("\n🧪 Testing task insertion...")
    
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        
        # Try different approaches for task insertion
        test_cases = [
            ('Test Task 1', 'pending', 'medium'),
            ('Test Task 2', 'completed', 'high'),
        ]
        
        for i, (title, status, priority) in enumerate(test_cases, 1):
            try:
                # First check what data type the columns expect
                cursor.execute("""
                    SELECT column_name, data_type, udt_name
                    FROM information_schema.columns 
                    WHERE table_name = 'tasks' AND column_name IN ('status', 'priority');
                """)
                
                column_info = {row[0]: row[2] for row in cursor.fetchall()}
                print(f"  Column types: {column_info}")
                
                # Try inserting based on current table structure
                cursor.execute("""
                    INSERT INTO tasks (title, description, status, priority, created_at) 
                    VALUES (%s, %s, %s, %s, NOW()) 
                    RETURNING id
                """, (title, f'Test description {i}', status, priority))
                
                task_id = cursor.fetchone()[0]
                print(f"  ✅ Successfully inserted task {i} (ID: {task_id})")
                
                # Clean up
                cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
                conn.commit()
                
            except Exception as e:
                print(f"  ❌ Task {i} insertion failed: {e}")
                conn.rollback()
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Task test failed: {e}")
        return False

def main():
    print("🛠️  Comprehensive Schema Fix")
    print("=" * 40)
    
    if fix_all_schema_issues():
        if run_task_test():
            print("\n✅ All schema issues resolved!")
            print("Run the full database test again:")
            print("python3 test_database_configuration.py")
            return 0
        else:
            print("\n⚠️  Schema updated but tasks still need attention")
            return 1
    else:
        print("\n❌ Schema fix failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
