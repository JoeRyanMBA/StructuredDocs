#!/usr/bin/env python3
"""
Test script to verify PostgreSQL database is properly configured for new data entry
"""
from datetime import datetime
import sys
import pytest
import socket

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
        import psycopg2
    except Exception:
        pytest.skip("psycopg2 not installed; skipping DB integration test")

    # Skip early if host unreachable
    try:
        socket.create_connection((PG_CONFIG['host'], PG_CONFIG['port']), timeout=2).close()
    except Exception:
        pytest.skip("Postgres host unreachable; skipping DB integration test")

    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()

        print("\n1️⃣ Testing table structure...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)

        tables = [row[0] for row in cursor.fetchall()]
        expected_tables = ['users', 'stakeholders', 'projects', 'collections', 'topics', 'tasks', 'reviews', 'notifications']
        missing_tables = [t for t in expected_tables if t not in tables]
        assert not missing_tables, f"Missing tables: {missing_tables}"

        print("\n2️⃣ Testing data insertion...")

        cursor.execute("""
            INSERT INTO users (name, email, role, active, created_at) 
            VALUES (%s, %s, %s, %s, %s) 
            RETURNING id
        """, ('Test User', 'test@example.com', 'author', True, datetime.now()))
        new_user_id = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO stakeholders (name, email, role, expertise_areas, active, created_at) 
            VALUES (%s, %s, %s, %s, %s, %s) 
            RETURNING id
        """, ('Test Stakeholder', 'stakeholder@example.com', 'reviewer', 'Testing', True, datetime.now()))
        new_stakeholder_id = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO topics (title, content, status, created_at, updated_at) 
            VALUES (%s, %s, %s, %s, %s) 
            RETURNING id
        """, ('Test Topic', 'This is a test topic content', 'draft', datetime.now(), datetime.now()))
        new_topic_id = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO tasks (title, description, status, priority, created_at) 
            VALUES (%s, %s, %s, %s, %s) 
            RETURNING id
        """, ('Test Task', 'This is a test task', 'pending', 'medium', datetime.now()))
        new_task_id = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO reviews (topic_id, requested_by, reviewer_id, status, priority, requested_at, author_message) 
            VALUES (%s, %s, %s, %s, %s, %s, %s) 
            RETURNING id
        """, (new_topic_id, new_user_id, new_stakeholder_id, 'pending', 'medium', datetime.now(), 'Test review request'))
        new_review_id = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO notifications (message, user_id, type, created_at) 
            VALUES (%s, %s, %s, %s) 
            RETURNING id
        """, ('Test notification', new_user_id, 'info', datetime.now()))
        new_notification_id = cursor.fetchone()[0]

        print("\n3️⃣ Testing foreign key relationships...")
        try:
            cursor.execute("""
                INSERT INTO reviews (topic_id, requested_by, reviewer_id, status) 
                VALUES (%s, %s, %s, %s)
            """, (99999, new_user_id, new_stakeholder_id, 'pending'))
            # If this does not raise, fail the assertion
            assert False, "Foreign key constraint not enforced"
        except psycopg2.IntegrityError:
            print("  ✅ Foreign key constraints are working correctly")
            conn.rollback()

        # Clean up test data
        cleanup = [
            ('notifications', new_notification_id),
            ('reviews', new_review_id),
            ('tasks', new_task_id),
            ('topics', new_topic_id),
            ('stakeholders', new_stakeholder_id),
            ('users', new_user_id)
        ]
        for table, eid in cleanup:
            cursor.execute(f"DELETE FROM {table} WHERE id = %s", (eid,))
        conn.commit()

        # Sequences check (best-effort)
        for table in ['users', 'stakeholders', 'projects', 'collections', 'topics', 'tasks', 'reviews', 'notifications']:
            try:
                cursor.execute(f"SELECT MAX(id) FROM {table}")
                max_id = cursor.fetchone()[0] or 0
                cursor.execute(f"SELECT last_value FROM {table}_id_seq")
                seq_value = cursor.fetchone()[0]
                if seq_value < max_id:
                    cursor.execute(f"SELECT setval('{table}_id_seq', (SELECT MAX(id) FROM {table}))")
                    conn.commit()
            except Exception:
                # ignore sequence issues in testing environment
                pass

        conn.close()
        # test passes if no exception raised
    except Exception:
        # Raise to surface the error to pytest
        raise

def show_current_data_counts():
    """Show current data counts"""
    print("\n📊 Current data in database:")
    
    try:
        try:
            import psycopg2
        except Exception:
            print("psycopg2 not installed; cannot show current data counts")
            return

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
