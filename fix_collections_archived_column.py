#!/usr/bin/env python3
"""
Fix missing 'archived' column in collections table for PostgreSQL production database.
This script is safe to run multiple times.

Usage:
1. Set your Digital Ocean DATABASE_URL environment variable
2. Run: python fix_collections_archived_column.py

Or pass the database URL directly:
python fix_collections_archived_column.py --database-url "postgresql://user:pass@host:port/dbname"
"""

import os
import sys
import argparse
import psycopg2
from urllib.parse import urlparse

def parse_database_url(database_url):
    """Parse DATABASE_URL into connection parameters"""
    if not database_url:
        raise ValueError("DATABASE_URL is required")
    
    parsed = urlparse(database_url)
    return {
        'host': parsed.hostname,
        'port': parsed.port or 5432,
        'database': parsed.path[1:] if parsed.path else None,
        'user': parsed.username,
        'password': parsed.password
    }

def add_archived_column(database_url):
    """Add archived column to collections table if it doesn't exist"""
    print(f"🔗 Connecting to database...")
    
    conn = None
    cursor = None
    
    try:
        conn_params = parse_database_url(database_url)
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        print("✅ Connected to PostgreSQL database")
        
        # Check if archived column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'collections' 
            AND column_name = 'archived'
        """)
        
        if cursor.fetchone():
            print("ℹ️ 'archived' column already exists in collections table")
            return True
        
        print("➕ Adding 'archived' column to collections table...")
        
        # Add the archived column with default value FALSE
        cursor.execute("""
            ALTER TABLE collections 
            ADD COLUMN archived BOOLEAN NOT NULL DEFAULT FALSE
        """)
        
        conn.commit()
        print("✅ Successfully added 'archived' column to collections table")
        
        # Verify the column was added
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'collections' 
            AND column_name = 'archived'
        """)
        
        result = cursor.fetchone()
        if result:
            print(f"✅ Verified: archived column created with type {result[1]}, nullable: {result[2]}, default: {result[3]}")
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        if conn:
            conn.rollback()
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
        print("🔌 Database connection closed")

def main():
    parser = argparse.ArgumentParser(description='Add archived column to collections table')
    parser.add_argument('--database-url', 
                       default=os.environ.get('DATABASE_URL'),
                       help='PostgreSQL database URL (defaults to DATABASE_URL env var)')
    
    args = parser.parse_args()
    
    if not args.database_url:
        print("❌ ERROR: DATABASE_URL is required")
        print("Set it as an environment variable or pass --database-url")
        print("Example: python fix_collections_archived_column.py --database-url 'postgresql://user:pass@host:port/dbname'")
        sys.exit(1)
    
    print("🚀 Starting collections table migration...")
    print(f"🎯 Target database: {args.database_url.split('@')[1] if '@' in args.database_url else 'hidden'}")
    
    success = add_archived_column(args.database_url)
    
    if success:
        print("🎉 Migration completed successfully!")
        print("Your Word document import should now work correctly.")
    else:
        print("❌ Migration failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()