#!/usr/bin/env python3
"""
Simple script to add archived column to collections table.
This script reads the DATABASE_URL from environment variables automatically.
Safe to run on Digital Ocean App Platform.

Usage on Digital Ocean:
1. Go to your App in Digital Ocean Dashboard
2. Click "Console" tab
3. Run: python add_archived_column.py
"""

import os
import sys

def add_archived_column():
    """Add archived column to collections table using Flask app context"""
    
    # Set required environment variables
    os.environ.setdefault('ENABLE_BLUEPRINTS', 'users,topics,projects,publications,links,notifications,reviews,import,organize,publish')
    
    try:
        # Import after setting environment
        from backend.app import create_app
        from backend.extensions import db
        
        print("🚀 Creating Flask app...")
        app = create_app()
        
        with app.app_context():
            print("🔍 Checking database connection...")
            
            # Check if we can connect to the database
            try:
                db.session.execute(db.text('SELECT 1'))
                print("✅ Database connection successful")
            except Exception as e:
                print(f"❌ Database connection failed: {e}")
                return False
            
            # Check if archived column exists
            print("🔍 Checking if 'archived' column exists in collections table...")
            
            inspector = db.inspect(db.engine)
            try:
                collections_columns = [c['name'] for c in inspector.get_columns('collections')]
                print(f"📋 Current collections table columns: {collections_columns}")
                
                if 'archived' in collections_columns:
                    print("ℹ️ 'archived' column already exists in collections table")
                    print("✅ No action needed - your Word import should work!")
                    return True
                
                print("➕ Adding 'archived' column to collections table...")
                
                # Add the column using SQLAlchemy text for safety
                db.session.execute(db.text("ALTER TABLE collections ADD COLUMN archived BOOLEAN NOT NULL DEFAULT FALSE"))
                db.session.commit()
                
                print("✅ Successfully added 'archived' column to collections table")
                
                # Verify the column was added
                updated_columns = [c['name'] for c in inspector.get_columns('collections')]
                if 'archived' in updated_columns:
                    print("✅ Verified: 'archived' column is now present")
                    print("🎉 Your Word document import should now work!")
                    return True
                else:
                    print("⚠️ Column may have been added but verification failed")
                    return False
                
            except Exception as e:
                print(f"❌ Error during column operations: {e}")
                return False
                
    except ImportError as e:
        print(f"❌ Failed to import required modules: {e}")
        print("💡 Make sure you're running this on your Digital Ocean app where dependencies are installed")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔧 StructuredDocs Database Column Fix")
    print("📍 Adding 'archived' column to collections table...")
    print()
    
    # Check if DATABASE_URL is available (should be automatic on Digital Ocean)
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Don't print the full URL for security
        host_part = database_url.split('@')[1].split('/')[0] if '@' in database_url else 'hidden'
        print(f"🎯 Target database: {host_part}")
    else:
        print("⚠️ DATABASE_URL not found in environment variables")
        print("💡 This script should be run on your Digital Ocean app where DATABASE_URL is automatically set")
    
    success = add_archived_column()
    
    if success:
        print()
        print("🎉 SUCCESS! Migration completed.")
        print("✅ Your Word document import should now work correctly.")
        print("🔄 Try importing your Word document again.")
    else:
        print()
        print("❌ Migration failed!")
        print("💡 You may need to run this as an admin or check your database permissions.")
        sys.exit(1)

if __name__ == "__main__":
    main()