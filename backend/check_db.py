import sqlite3

conn = sqlite3.connect('instance/structured_docs.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cursor.fetchall()]
print("Tables:", tables)

# Check users table and data
try:
    cursor.execute("SELECT email, password FROM users WHERE email = 'admin@census.gov';")
    admin_user = cursor.fetchone()
    if admin_user:
        print(f"Admin user found - Email: {admin_user[0]}, Password hash: {admin_user[1]}")
    else:
        print("No admin@census.gov user found")
        
    # Show all users
    cursor.execute("SELECT email FROM users;")
    all_users = cursor.fetchall()
    print("All users:", [user[0] for user in all_users])
    
except Exception as e:
    print("Error querying users:", str(e))

conn.close()
