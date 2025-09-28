#!/usr/bin/env python3
"""Diagnostic script to check current database and API state."""

import os
import sys

import psycopg2

# PostgreSQL connection details
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://user:password@host:5432/structured_docs')

def check_database_state():
    """Check what's actually in the database"""
    print("🔍 Checking current database state...")
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Check row counts
        tables = ['topics', 'tasks', 'reviews', 'users', 'stakeholders', 'projects', 'collections', 'notifications']
        
        print("Current data in PostgreSQL:")
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  {table}: {count} rows")
                
                # Show a few sample records for key tables
                if table == 'topics' and count > 0:
                    cursor.execute("SELECT id, title FROM topics LIMIT 3")
                    topics = cursor.fetchall()
                    print("    Sample topics:")
                    for topic in topics:
                        print(f"      ID {topic[0]}: {topic[1]}")
                
                if table == 'notifications' and count > 0:
                    cursor.execute("SELECT id, title, message, date, created_at FROM notifications LIMIT 3")
                    notifications = cursor.fetchall()
                    print("    Sample notifications:")
                    for notif in notifications:
                        print(f"      ID {notif[0]}: '{notif[1]}' - '{notif[2]}' (date: {notif[3]}, created_at: {notif[4]})")
                        
            except Exception as e:
                print(f"  {table}: ERROR - {e}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False

def test_api_endpoints():
    """Test if we can import and call the API functions"""
    print("\n🧪 Testing API endpoint functions...")
    
    try:
        # Test importing the app
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)

        from backend.app import create_app
        
        app = create_app()
        
        with app.app_context():
            # Test topics API function directly
            print("Testing topics API...")
            try:
                from backend.models import Topic
                topics = Topic.query.limit(5).all()
                print(f"  ✅ Found {len(topics)} topics in database")
                for topic in topics:
                    print(f"    ID {topic.id}: {topic.title}")
            except Exception as e:
                print(f"  ❌ Topics API test failed: {e}")
            
            # Test notifications API function directly  
            print("Testing notifications API...")
            try:
                from backend.models import Notification
                notifications = Notification.query.all()
                print(f"  ✅ Found {len(notifications)} notifications in database")
                for notif in notifications:
                    # Check what fields are available
                    print(f"    ID {notif.id}: message='{notif.message}'")
                    print(f"      Available fields: {dir(notif)}")
                    # Try different date field names
                    date_fields = ['date', 'created_at', 'timestamp', 'notification_date']
                    for field in date_fields:
                        if hasattr(notif, field):
                            value = getattr(notif, field)
                            print(f"      {field}: {value}")
            except Exception as e:
                print(f"  ❌ Notifications API test failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🚨 DIAGNOSTIC: Current State Check")
    print("=" * 40)
    
    # Check database first
    if not check_database_state():
        print("\n❌ Database issues found - migration may not have completed")
        return 1
    
    # Test API functions
    if not test_api_endpoints():
        print("\n❌ API issues found - app may not be properly deployed")
        return 1
    
    print("\n✅ Diagnostic complete!")
    print("\nIf you're still seeing 'Failed to Load Topics':")
    print("1. Confirm the latest backend code is deployed.")
    print("2. Restart the backend service on your server or container platform.")
    print("3. Check browser console and server logs for API errors.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
