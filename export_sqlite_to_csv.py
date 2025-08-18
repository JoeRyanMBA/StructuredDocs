#!/usr/bin/env python3
"""
Export SQLite data to CSV files for manual PostgreSQL import
"""
import sqlite3
import csv
import os

# SQLite database path
SQLITE_DB = '/workspaces/StructuredDocs/instance/structured_docs.db'
EXPORT_DIR = '/workspaces/StructuredDocs/csv_export'

def export_table_to_csv(conn, table_name, export_dir):
    """Export a single table to CSV"""
    print(f"Exporting table: {table_name}")
    
    cursor = conn.cursor()
    
    # Get column names
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    
    # Get data
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    # Write to CSV
    csv_file = os.path.join(export_dir, f"{table_name}.csv")
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(columns)  # Header
        writer.writerows(rows)    # Data
    
    print(f"  Exported {len(rows)} rows to {csv_file}")
    return len(rows)

def main():
    print("Exporting SQLite data to CSV files")
    
    # Create export directory
    os.makedirs(EXPORT_DIR, exist_ok=True)
    
    # Connect to SQLite
    try:
        conn = sqlite3.connect(SQLITE_DB)
        print("✅ Connected to SQLite database")
    except Exception as e:
        print(f"❌ Failed to connect to SQLite: {e}")
        return 1
    
    # Get all tables
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name != 'alembic_version';")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"Found {len(tables)} tables: {', '.join(tables)}")
    
    total_rows = 0
    # Export each table
    for table_name in sorted(tables):
        try:
            rows_exported = export_table_to_csv(conn, table_name, EXPORT_DIR)
            total_rows += rows_exported
        except Exception as e:
            print(f"❌ Error exporting {table_name}: {e}")
    
    conn.close()
    
    print(f"\n✅ Export completed!")
    print(f"📁 CSV files saved to: {EXPORT_DIR}")
    print(f"📊 Total rows exported: {total_rows}")
    
    # Generate import script
    import_script = os.path.join(EXPORT_DIR, 'import_to_postgresql.sql')
    with open(import_script, 'w') as f:
        f.write("-- PostgreSQL import script\n")
        f.write("-- Run this on PythonAnywhere's PostgreSQL console\n\n")
        
        for table_name in sorted(tables):
            f.write(f"\\copy {table_name} FROM '{table_name}.csv' DELIMITER ',' CSV HEADER;\n")
        
        f.write("\n-- Verify data\n")
        for table_name in sorted(tables):
            f.write(f"SELECT '{table_name}' as table_name, COUNT(*) as row_count FROM {table_name};\n")
    
    print(f"📝 Import script saved to: {import_script}")
    return 0

if __name__ == "__main__":
    exit(main())
