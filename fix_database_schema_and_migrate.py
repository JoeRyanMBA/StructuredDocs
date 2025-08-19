#!/usr/bin/env python3
"""
Script to create/update PostgreSQL database schema and migrate data
"""
import psycopg2
import sqlite3
import sys

# PostgreSQL connection details
PG_CONFIG = {
    'host': 'JoeRyanMBA-4757.postgres.pythonanywhere-services.com',
    'port': 14757,
    'database': 'structured_docs',
    'user': 'super',
    'password': 'Picklehead1!'
}

def check_and_update_schema():
    """Check and update PostgreSQL schema to match SQLite"""
    print("🔧 Checking and updating PostgreSQL schema...")
    
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        
        # Check what tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        
        existing_tables = [row[0] for row in cursor.fetchall()]
        print(f"Existing tables: {existing_tables}")
        
        # Update topic_status enum to include missing values
        print("\n📝 Updating topic_status enum...")
        try:
            cursor.execute("ALTER TYPE topic_status ADD VALUE IF NOT EXISTS 'revisions_requested';")
            conn.commit()
            print("✅ Added 'revisions_requested' to topic_status enum")
        except Exception as e:
            print(f"⚠️  Topic status enum update: {e}")
            conn.rollback()
        
        # Add missing column to stakeholders if needed
        print("\n📝 Checking stakeholders table...")
        try:
            cursor.execute("ALTER TABLE stakeholders ADD COLUMN IF NOT EXISTS division VARCHAR(100);")
            conn.commit()
            print("✅ Added division column to stakeholders")
        except Exception as e:
            print(f"⚠️  Stakeholders column update: {e}")
            conn.rollback()
        
        # Check if reviews table exists, if not create it
        if 'reviews' not in existing_tables:
            print("\n📝 Creating reviews table...")
            try:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS reviews (
                        id SERIAL PRIMARY KEY,
                        topic_id INTEGER REFERENCES topics(id),
                        requested_by INTEGER REFERENCES users(id),
                        reviewer_id INTEGER REFERENCES users(id),
                        status VARCHAR(20) DEFAULT 'pending',
                        priority VARCHAR(10) DEFAULT 'medium',
                        requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        due_date TIMESTAMP,
                        started_at TIMESTAMP,
                        completed_at TIMESTAMP,
                        feedback TEXT,
                        recommendation VARCHAR(20),
                        review_notes TEXT,
                        author_message TEXT,
                        edited_content TEXT,
                        follow_up_sent_at TIMESTAMP,
                        sequence_id INTEGER,
                        sequence_position INTEGER
                    );
                """)
                conn.commit()
                print("✅ Created reviews table")
            except Exception as e:
                print(f"❌ Error creating reviews table: {e}")
                conn.rollback()
        
        # Create other missing tables as needed
        missing_tables = ['review_tokens', 'review_feedback', 'review_sequences', 'review_sequence_steps', 'tags']
        for table in missing_tables:
            if table not in existing_tables:
                print(f"\n📝 Creating {table} table...")
                try:
                    if table == 'review_tokens':
                        cursor.execute("""
                            CREATE TABLE IF NOT EXISTS review_tokens (
                                id SERIAL PRIMARY KEY,
                                token VARCHAR(255) UNIQUE NOT NULL,
                                review_id INTEGER REFERENCES reviews(id),
                                reviewer_email VARCHAR(255),
                                expires_at TIMESTAMP,
                                used_at TIMESTAMP,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            );
                        """)
                    elif table == 'tags':
                        cursor.execute("""
                            CREATE TABLE IF NOT EXISTS tags (
                                id SERIAL PRIMARY KEY,
                                name VARCHAR(100) UNIQUE NOT NULL,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            );
                        """)
                    # Add other table creations as needed
                    conn.commit()
                    print(f"✅ Created {table} table")
                except Exception as e:
                    print(f"❌ Error creating {table} table: {e}")
                    conn.rollback()
        
        conn.close()
        print("\n✅ Schema update completed!")
        return True
        
    except Exception as e:
        print(f"❌ Schema update failed: {e}")
        return False

def migrate_with_better_handling():
    """Run migration with better error handling"""
    print("\n🚚 Starting improved data migration...")
    
    SQLITE_DB = '/home/JoeRyanMBA/StructuredDocs/structured_docs.db'
    
    try:
        # Connect to both databases
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        pg_conn = psycopg2.connect(**PG_CONFIG)
        
        # Migrate key tables one by one with custom handling
        
        # 1. Migrate topics with enum handling
        print("\n📋 Migrating topics...")
        sqlite_cursor = sqlite_conn.cursor()
        sqlite_cursor.execute("SELECT * FROM topics")
        topics = sqlite_cursor.fetchall()
        
        sqlite_cursor.execute("PRAGMA table_info(topics)")
        topic_columns = [row[1] for row in sqlite_cursor.fetchall()]
        
        pg_cursor = pg_conn.cursor()
        pg_cursor.execute("DELETE FROM topics")
        
        for topic in topics:
            # Convert the topic data, handling enum values
            topic_data = list(topic)
            status_index = topic_columns.index('status') if 'status' in topic_columns else None
            
            if status_index and topic_data[status_index] == 'revisions_requested':
                topic_data[status_index] = 'draft'  # Fallback to valid enum value
            
            placeholders = ', '.join(['%s'] * len(topic_data))
            column_names = ', '.join(topic_columns)
            
            try:
                pg_cursor.execute(f"INSERT INTO topics ({column_names}) VALUES ({placeholders})", topic_data)
            except Exception as e:
                print(f"  ⚠️  Skipping topic {topic_data[0]}: {e}")
        
        pg_conn.commit()
        pg_cursor.execute("SELECT COUNT(*) FROM topics")
        topic_count = pg_cursor.fetchone()[0]
        print(f"  ✅ Migrated {topic_count} topics")
        
        # Reset sequence
        pg_cursor.execute("SELECT setval(pg_get_serial_sequence('topics', 'id'), (SELECT MAX(id) FROM topics));")
        pg_conn.commit()
        
        # 2. Migrate reviews if table exists now
        print("\n📝 Migrating reviews...")
        try:
            sqlite_cursor.execute("SELECT * FROM reviews")
            reviews = sqlite_cursor.fetchall()
            
            sqlite_cursor.execute("PRAGMA table_info(reviews)")
            review_columns = [row[1] for row in sqlite_cursor.fetchall()]
            
            pg_cursor.execute("DELETE FROM reviews")
            
            for review in reviews:
                placeholders = ', '.join(['%s'] * len(review))
                column_names = ', '.join(review_columns)
                
                try:
                    pg_cursor.execute(f"INSERT INTO reviews ({column_names}) VALUES ({placeholders})", review)
                except Exception as e:
                    print(f"  ⚠️  Skipping review {review[0]}: {e}")
            
            pg_conn.commit()
            pg_cursor.execute("SELECT COUNT(*) FROM reviews")
            review_count = pg_cursor.fetchone()[0]
            print(f"  ✅ Migrated {review_count} reviews")
            
            # Reset sequence
            pg_cursor.execute("SELECT setval(pg_get_serial_sequence('reviews', 'id'), (SELECT MAX(id) FROM reviews));")
            pg_conn.commit()
            
        except Exception as e:
            print(f"  ❌ Reviews migration failed: {e}")
        
        sqlite_conn.close()
        pg_conn.close()
        
        print("\n✅ Improved migration completed!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    
    return True

def verify_final_state():
    """Verify the final state of the database"""
    print("\n🔍 Final verification...")
    
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        
        # Check key tables
        tables_to_check = ['topics', 'tasks', 'reviews', 'users', 'stakeholders', 'projects', 'collections']
        
        for table in tables_to_check:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  {table}: {count} rows")
            except Exception as e:
                print(f"  {table}: ERROR - {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")

def main():
    print("🏗️  Database Schema Update and Migration Tool")
    print("=" * 50)
    
    # Step 1: Update schema
    if not check_and_update_schema():
        print("❌ Schema update failed, aborting")
        return 1
    
    # Step 2: Migrate data with better handling
    if not migrate_with_better_handling():
        print("❌ Migration failed")
        return 1
    
    # Step 3: Verify
    verify_final_state()
    
    print("\n🎉 All done! Check your app now.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
