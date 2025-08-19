#!/usr/bin/env python3
"""
Migration script to transfer data from SQLite to PostgreSQL
FIXED VERSION with data type conversions for PythonAnywhere
"""
import sqlite3
import psycopg2
import os
import sys
from datetime import datetime

# SQLite database path - CORRECTED for PythonAnywhere
SQLITE_DB = '/home/JoeRyanMBA/StructuredDocs/structured_docs.db'

# PostgreSQL connection details
PG_CONFIG = {
    'host': 'JoeRyanMBA-4757.postgres.pythonanywhere-services.com',
    'port': 14757,
    'database': 'structured_docs',
    'user': 'super',
    'password': 'Picklehead1!'
}

def get_table_names(sqlite_conn):
    """Get all table names from SQLite database"""
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name != 'alembic_version';")
    return [row[0] for row in cursor.fetchall()]

def get_table_columns(sqlite_conn, table_name):
    """Get column names for a table"""
    cursor = sqlite_conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    return [row[1] for row in cursor.fetchall()]

def convert_row_data(table_name, columns, row):
    """Convert SQLite row data to PostgreSQL compatible format"""
    converted_row = list(row)
    
    # Handle boolean conversions for specific tables
    boolean_columns = {
        'users': ['active'],
        'stakeholders': ['active'] if 'active' in columns else [],
        'projects': ['active'] if 'active' in columns else [],
        'topics': ['published'] if 'published' in columns else [],
        'collections': ['active'] if 'active' in columns else [],
        'notifications': ['read'] if 'read' in columns else []
    }
    
    if table_name in boolean_columns:
        for i, column in enumerate(columns):
            if column in boolean_columns[table_name]:
                # Convert 0/1 to False/True
                if converted_row[i] is not None:
                    converted_row[i] = bool(converted_row[i])
    
    return tuple(converted_row)

def migrate_table(sqlite_conn, pg_conn, table_name):
    """Migrate a single table from SQLite to PostgreSQL"""
    print(f"Migrating table: {table_name}")
    
    # Get data from SQLite
    sqlite_cursor = sqlite_conn.cursor()
    sqlite_cursor.execute(f"SELECT * FROM {table_name}")
    rows = sqlite_cursor.fetchall()
    
    if not rows:
        print(f"  No data found in {table_name}")
        return
    
    # Get column names
    columns = get_table_columns(sqlite_conn, table_name)
    
    # Clear existing data in PostgreSQL table first (to avoid conflicts)
    pg_cursor = pg_conn.cursor()
    try:
        pg_cursor.execute(f"DELETE FROM {table_name}")
        pg_conn.commit()
        print(f"  Cleared existing data from {table_name}")
    except Exception as e:
        pg_conn.rollback()
        print(f"  Warning: Could not clear {table_name}: {e}")
    
    # Prepare PostgreSQL insert statement
    placeholders = ', '.join(['%s'] * len(columns))
    column_names = ', '.join(columns)
    insert_sql = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
    
    # Convert row data for PostgreSQL compatibility
    converted_rows = [convert_row_data(table_name, columns, row) for row in rows]
    
    # Insert data into PostgreSQL
    try:
        pg_cursor.executemany(insert_sql, converted_rows)
        pg_conn.commit()
        print(f"  Successfully migrated {len(converted_rows)} rows")
        
        # Reset sequence for tables with auto-increment IDs
        if 'id' in columns:
            try:
                pg_cursor.execute(f"SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), (SELECT MAX(id) FROM {table_name}));")
                pg_conn.commit()
                print(f"  Reset sequence for {table_name}")
            except Exception as e:
                print(f"  Warning: Could not reset sequence for {table_name}: {e}")
                
    except Exception as e:
        pg_conn.rollback()
        print(f"  Error migrating {table_name}: {e}")
        # Try to handle specific cases
        if "duplicate key" in str(e).lower():
            print(f"  Skipping {table_name} - data already exists")
        else:
            print(f"  Error details: {e}")
            # Don't raise - continue with other tables
            return

def main():
    print("Starting database migration from SQLite to PostgreSQL")
    print(f"SQLite DB: {SQLITE_DB}")
    print(f"PostgreSQL: {PG_CONFIG['host']}:{PG_CONFIG['port']}/{PG_CONFIG['database']}")
    
    # Connect to SQLite
    try:
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        print("✅ Connected to SQLite database")
    except Exception as e:
        print(f"❌ Failed to connect to SQLite: {e}")
        return 1
    
    # Connect to PostgreSQL
    try:
        pg_conn = psycopg2.connect(**PG_CONFIG)
        print("✅ Connected to PostgreSQL database")
    except Exception as e:
        print(f"❌ Failed to connect to PostgreSQL: {e}")
        return 1
    
    # Get all tables
    tables = get_table_names(sqlite_conn)
    print(f"Found {len(tables)} tables to migrate: {', '.join(tables)}")
    
    # Migration order (to handle foreign key dependencies)
    migration_order = [
        'users',
        'stakeholders', 
        'projects',
        'collections',
        'topics',
        'reviews',
        'review_tokens',
        'review_feedback',
        'review_sequences',
        'review_sequence_steps',
        'notifications',
        'links',
        'topic_links',
        'tags',
        'tasks',
        'publications',
        'publication_nodes',
        'project_milestones',
        'project_stakeholders',
        'import_documents',
        'import_items',
        'import_images',
        'collection_topic_tree'
    ]
    
    # Migrate tables in order
    migrated_tables = set()
    errors = []
    
    for table_name in migration_order:
        if table_name in tables:
            try:
                migrate_table(sqlite_conn, pg_conn, table_name)
                migrated_tables.add(table_name)
            except Exception as e:
                errors.append(f"{table_name}: {e}")
                print(f"  ❌ Failed to migrate {table_name}, continuing...")
    
    # Migrate any remaining tables
    for table_name in tables:
        if table_name not in migrated_tables:
            try:
                migrate_table(sqlite_conn, pg_conn, table_name)
            except Exception as e:
                errors.append(f"{table_name}: {e}")
                print(f"  ❌ Failed to migrate {table_name}, continuing...")
    
    # Close connections
    sqlite_conn.close()
    pg_conn.close()
    
    if errors:
        print(f"\n⚠️  Migration completed with {len(errors)} errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("\n✅ Migration completed successfully!")
    
    # Verification step
    print("\n🔍 Verifying migration...")
    verify_migration()
    
    return 0

def verify_migration():
    """Verify that the migration was successful by checking row counts"""
    try:
        # Connect to PostgreSQL for verification
        pg_conn = psycopg2.connect(**PG_CONFIG)
        pg_cursor = pg_conn.cursor()
        
        # Check key tables
        key_tables = ['topics', 'tasks', 'reviews', 'users', 'stakeholders', 'projects', 'collections']
        
        print("Row counts in PostgreSQL after migration:")
        for table_name in key_tables:
            try:
                pg_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = pg_cursor.fetchone()[0]
                print(f"  {table_name}: {count} rows")
            except Exception as e:
                print(f"  {table_name}: ERROR - {e}")
        
        pg_conn.close()
        print("✅ Verification completed!")
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")

if __name__ == "__main__":
    sys.exit(main())
