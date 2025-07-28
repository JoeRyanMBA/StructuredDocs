import sqlite3

conn = sqlite3.connect('instance/structured_docs.db')

# Get all tables
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cursor.fetchall()]
print("Tables:", tables)

# Check if users table exists
if 'users' in tables:
    users_info = conn.execute('PRAGMA table_info(users);').fetchall()
    print("Users table columns:", users_info)
else:
    # Try to directly query users table
    try:
        result = conn.execute('SELECT COUNT(*) FROM users;').fetchone()
        print("Users table exists but not in main schema, count:", result[0])
    except Exception as e:
        print("Users table does not exist:", str(e))

# Check topics table structure
topics_info = conn.execute('PRAGMA table_info(topics);').fetchall()
print("Topics table columns:", topics_info)

conn.close()
