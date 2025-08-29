#!/usr/bin/env python3

import sqlite3

def fix_database():
    conn = sqlite3.connect('instance/structured_docs.db')
    cursor = conn.cursor()
    
    # Check current status values
    cursor.execute('SELECT id, status FROM import_documents')
    docs = cursor.fetchall()
    print('Current documents:')
    for doc in docs:
        print(f'  Doc {doc[0]}: {doc[1]}')
    
    # Update all to staging status
    cursor.execute("UPDATE import_documents SET status = 'staging'")
    print(f'Updated {cursor.rowcount} documents to staging status')
    
    conn.commit()
    conn.close()
    print('Database fixed successfully')

if __name__ == '__main__':
    fix_database()
