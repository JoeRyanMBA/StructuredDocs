#!/usr/bin/env python3
"""
Test script to verify PostgreSQL database is properly configured for new data entry
"""
import psycopg2
from datetime import datetime
import sys

# PostgreSQL connection details
PG_CONFIG = {
    'host': 'JoeRyanMBA-4757.postgres.pythonanywhere-services.com',
    'port': 14757,
    'database': 'structured_docs',
    'user': 'super',
    'password': 'Picklehead1!'
}

def test_database_operations():
    """Test basic database operations to ensure it's ready for new data"""
    print("🧪 Testing database configuration for new data entry...")
    
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        
        print("\n1️⃣ Testing table structure...")
        
        # Check if all expected tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        expected_tables = ['users', 'stakeholders', 'projects', 'collections', 'topics', 'tasks', 'reviews', 'notifications']
        
        missing_tables = []
        for table in expected_tables:
            if table in tables:
                print(f"  ✅ {table} table exists")
            else:
                print(f"  ❌ {table} table missing")
                missing_tables.append(table)
        
        if missing_tables:
            print(f"\n❌ Missing tables: {missing_tables}")
            return False
        
        print("\n2️⃣ Testing data insertion...")
        
        # Test 1: Insert a new user
        try:
            cursor.execute("""
                INSERT INTO users (name, email, role, active, created_at) 
                VALUES (%s, %s, %s, %s, %s) 
                RETURNING id
            """, ('Test User', 'test@example.com', 'author', True, datetime.now()))
            
            new_user_id = cursor.fetchone()[0]
            print(f"  ✅ Successfully inserted new user (ID: {new_user_id})")
            
        except Exception as e:
            print(f"  ❌ User insertion failed: {e}")
            conn.rollback()
            return False
        
        # Test 2: Insert a new stakeholder
        try:
            cursor.execute("""
                INSERT INTO stakeholders (name, email, role, expertise_areas, active, created_at) 
                VALUES (%s, %s, %s, %s, %s, %s) 
                RETURNING id
            """, ('Test Stakeholder', 'stakeholder@example.com', 'reviewer', 'Testing', True, datetime.now()))
            
            new_stakeholder_id = cursor.fetchone()[0]
            print(f"  ✅ Successfully inserted new stakeholder (ID: {new_stakeholder_id})")
            
        except Exception as e:
            print(f"  ❌ Stakeholder insertion failed: {e}")
            conn.rollback()
            return False
        
        # Test 3: Insert a new topic
        try:
            cursor.execute("""
                INSERT INTO topics (title, content, status, created_at, updated_at) 
                VALUES (%s, %s, %s, %s, %s) 
                RETURNING id
            """, ('Test Topic', 'This is a test topic content', 'draft', datetime.now(), datetime.now()))
            
            new_topic_id = cursor.fetchone()[0]
            print(f"  ✅ Successfully inserted new topic (ID: {new_topic_id})")
            
        except Exception as e:
            print(f"  ❌ Topic insertion failed: {e}")
            conn.rollback()
            return False
        
        # Test 4: Insert a new task
        try:
            cursor.execute("""
                INSERT INTO tasks (title, description, status, priority, created_at) 
                VALUES (%s, %s, %s, %s, %s) 
                RETURNING id
            """, ('Test Task', 'This is a test task', 'pending', 'medium', datetime.now()))
            
            new_task_id = cursor.fetchone()[0]
            print(f"  ✅ Successfully inserted new task (ID: {new_task_id})")
            
        except Exception as e:
            print(f"  ❌ Task insertion failed: {e}")
            conn.rollback()
            return False
        
        # Test 5: Insert a new review (using the new user and topic)
        try:
            cursor.execute("""
                INSERT INTO reviews (topic_id, requested_by, reviewer_id, status, priority, requested_at, author_message) 
                VALUES (%s, %s, %s, %s, %s, %s, %s) 
                RETURNING id
            """, (new_topic_id, new_user_id, new_stakeholder_id, 'pending', 'medium', datetime.now(), 'Test review request'))
            
            new_review_id = cursor.fetchone()[0]
            print(f"  ✅ Successfully inserted new review (ID: {new_review_id})")
            
        except Exception as e:
            print(f"  ❌ Review insertion failed: {e}")
            conn.rollback()
            return False
        
        # Test 6: Insert a new notification
        try:
            cursor.execute("""
                INSERT INTO notifications (message, user_id, type, created_at) 
                VALUES (%s, %s, %s, %s) 
                RETURNING id
            """, ('Test notification', new_user_id, 'info', datetime.now()))
            
            new_notification_id = cursor.fetchone()[0]
            print(f"  ✅ Successfully inserted new notification (ID: {new_notification_id})")
            
        except Exception as e:
            print(f"  ❌ Notification insertion failed: {e}")
            conn.rollback()
            return False
        
        print("\n3️⃣ Testing foreign key relationships...")
        
        # Test foreign key constraints are working
        try:
            cursor.execute("""
                INSERT INTO reviews (topic_id, requested_by, reviewer_id, status) 
                VALUES (%s, %s, %s, %s)
            """, (99999, new_user_id, new_stakeholder_id, 'pending'))  # Non-existent topic_id
            
            print("  ❌ Foreign key constraint not working (should have failed)")
            conn.rollback()
            return False
            
        except psycopg2.IntegrityError:
            print("  ✅ Foreign key constraints are working correctly")
            conn.rollback()
        
        print("\n4️⃣ Cleaning up test data...")
        
        # Clean up test data
        cursor.execute("DELETE FROM notifications WHERE id = %s", (new_notification_id,))
        cursor.execute("DELETE FROM reviews WHERE id = %s", (new_review_id,))
        cursor.execute("DELETE FROM tasks WHERE id = %s", (new_task_id,))
        cursor.execute("DELETE FROM topics WHERE id = %s", (new_topic_id,))
        cursor.execute("DELETE FROM stakeholders WHERE id = %s", (new_stakeholder_id,))
        cursor.execute("DELETE FROM users WHERE id = %s", (new_user_id,))
        
        conn.commit()
        print("  ✅ Test data cleaned up")
        
        print("\n5️⃣ Checking sequences...")
        
        # Check that sequences are properly set
        tables_with_sequences = ['users', 'stakeholders', 'projects', 'collections', 'topics', 'tasks', 'reviews', 'notifications']
        
        for table in tables_with_sequences:
            try:
                cursor.execute(f"SELECT MAX(id) FROM {table}")
                max_id = cursor.fetchone()[0] or 0
                
                cursor.execute(f"SELECT last_value FROM {table}_id_seq")
                seq_value = cursor.fetchone()[0]
                
                if seq_value >= max_id:
                    print(f"  ✅ {table} sequence is properly set ({seq_value} >= {max_id})")
                else:
                    print(f"  ⚠️  {table} sequence needs updating ({seq_value} < {max_id})")
                    cursor.execute(f"SELECT setval('{table}_id_seq', (SELECT MAX(id) FROM {table}))")
                    conn.commit()
                    print(f"     ✅ Fixed {table} sequence")
                    
            except Exception as e:
                print(f"  ❌ {table} sequence check failed: {e}")
        
        conn.close()
        
        print("\n🎉 Database is properly configured for new data entry!")
        print("\n✅ Summary:")
        print("  - All required tables exist")
        print("  - Data insertion works for all entity types")
        print("  - Foreign key constraints are enforced")
        print("  - Sequences are properly configured")
        print("  - Ready for fresh start or continued use")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def show_current_data_counts():
    """Show current data counts"""
    print("\n📊 Current data in database:")
    
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        
        tables = ['users', 'stakeholders', 'projects', 'collections', 'topics', 'tasks', 'reviews', 'notifications']
        
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  {table}: {count} rows")
            except Exception as e:
                print(f"  {table}: ERROR - {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Data count check failed: {e}")

def main():
    print("🔧 Database Configuration Test")
    print("=" * 40)
    
    # Show current state
    show_current_data_counts()
    
    # Test database operations
    if test_database_operations():
        print("\n💡 Recommendation:")
        print("  Your database is properly configured! You can safely:")
        print("  1. Continue with existing data, or")
        print("  2. Clear all data for a fresh start")
        print("  3. Add new data through your application")
        return 0
    else:
        print("\n❌ Database needs additional configuration before use")
        return 1

if __name__ == "__main__":
    sys.exit(main())
