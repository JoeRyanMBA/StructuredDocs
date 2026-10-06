import os

import psycopg2

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://user:password@host:5432/structured_docs')

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()
try:
    # Change enum columns to VARCHAR
    cursor.execute('ALTER TABLE feedback_reports ALTER COLUMN report_type TYPE VARCHAR(32);')
    cursor.execute('ALTER TABLE feedback_reports ALTER COLUMN status TYPE VARCHAR(20);')
    conn.commit()
    print('Successfully changed enum columns to VARCHAR')
except Exception as e:
    print(f'Error: {e}')
    conn.rollback()
finally:
    cursor.close()
    conn.close()
