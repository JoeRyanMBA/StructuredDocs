"""
Migration script to add email_delivery_unavailable column to reviews table
Run this script to update your production PostgreSQL database
"""
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def run_migration():
    """Add email_delivery_unavailable column to reviews table"""
    from backend.app import create_app
    from backend.models import db
    
    app = create_app()
    
    with app.app_context():
        try:
            # Check if column already exists
            result = db.session.execute(db.text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='reviews' 
                AND column_name='email_delivery_unavailable'
            """))
            
            if result.fetchone():
                print("✅ Column 'email_delivery_unavailable' already exists in reviews table")
                return
            
            print("🔧 Adding 'email_delivery_unavailable' column to reviews table...")
            
            # Add the column
            db.session.execute(db.text("""
                ALTER TABLE reviews 
                ADD COLUMN email_delivery_unavailable BOOLEAN NOT NULL DEFAULT FALSE
            """))
            
            db.session.commit()
            print("✅ Successfully added 'email_delivery_unavailable' column to reviews table")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Migration failed: {e}")
            raise

if __name__ == '__main__':
    print("=" * 80)
    print("MIGRATION: Add email_delivery_unavailable to reviews table")
    print("=" * 80)
    run_migration()
    print("=" * 80)
    print("Migration complete!")
    print("=" * 80)
