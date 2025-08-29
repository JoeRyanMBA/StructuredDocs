import psycopg2

conn = psycopg2.connect('postgresql://super:Picklehead1!@JoeRyanMBA-4757.postgres.pythonanywhere-services.com:14757/structured_docs')
cursor = conn.cursor()
cursor.execute('SELECT enumtypid, enumlabel FROM pg_enum ORDER BY enumtypid, enumsortorder;')
enums = cursor.fetchall()
print('All enum values in database:')
for enum in enums:
    print(f'  {enum}')
cursor.close()
conn.close()
