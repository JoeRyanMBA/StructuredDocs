"""
Standalone migration script to add email_delivery_unavailable column
Uses psycopg2 directly without Flask dependencies
"""
import os
import psycopg2
from urllib.parse import urlparse

def get_db_connection():
    """Get database connection from DATABASE_URL environment variable"""
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        print("   Set it with: export DATABASE_URL='postgresql://user:pass@host:port/dbname'")
        return None
    
    try:
        # Parse the database URL
        result = urlparse(database_url)
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
        return conn
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return None

def run_migration():
    """Add email_delivery_unavailable column to reviews table"""
    
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Check if column already exists
        print("🔍 Checking if column exists...")
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='reviews' 
            AND column_name='email_delivery_unavailable'
        """)
        
        if cursor.fetchone():
            print("✅ Column 'email_delivery_unavailable' already exists in reviews table")
            cursor.close()
            conn.close()
            return True
        
        print("🔧 Adding 'email_delivery_unavailable' column to reviews table...")
        
        # Add the column
        cursor.execute("""
            ALTER TABLE reviews 
            ADD COLUMN email_delivery_unavailable BOOLEAN NOT NULL DEFAULT FALSE
        """)
        
        conn.commit()
        print("✅ Successfully added 'email_delivery_unavailable' column to reviews table")
        
        # Verify it was added
        cursor.execute("""
            SELECT column_name, data_type, column_default
            FROM information_schema.columns
            WHERE table_name = 'reviews'
            AND column_name = 'email_delivery_unavailable'
        """)
        
        result = cursor.fetchone()
        if result:
            print(f"✅ Verified: {result[0]} ({result[1]}, default: {result[2]})")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

if __name__ == '__main__':
    print("=" * 80)
    print("MIGRATION: Add email_delivery_unavailable to reviews table")
    print("=" * 80)
    
    success = run_migration()
    
    print("=" * 80)
    if success:
        print("✅ Migration completed successfully!")
    else:
        print("❌ Migration failed!")
    print("=" * 80)
