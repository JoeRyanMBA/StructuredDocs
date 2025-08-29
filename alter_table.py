import psycopg2

conn = psycopg2.connect('postgresql://super:Picklehead1!@JoeRyanMBA-4757.postgres.pythonanywhere-services.com:14757/structured_docs')
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
