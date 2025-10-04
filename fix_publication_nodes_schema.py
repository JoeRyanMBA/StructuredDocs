#!/usr/bin/env python3
"""
Fix publication_nodes schema by adding missing columns
This script will add title_snapshot and content_snapshot columns to publication_nodes table
"""

import os
import sys
sys.path.append('/workspaces/StructuredDocs')
sys.path.append('/workspaces/StructuredDocs/backend')

from backend.models import db, Publication, PublicationNode, Topic
from backend.app import create_app
from sqlalchemy import text

def fix_schema():
    """Add missing columns to publication_nodes table"""
    app = create_app()
    with app.app_context():
        try:
            # Check if we're using SQLite (local) or PostgreSQL (production)
            engine = db.engine
            dialect = engine.dialect.name
            
            print(f"Database dialect: {dialect}")
            
            if dialect == 'sqlite':
                # SQLite - use ALTER TABLE
                print("Adding columns to SQLite database...")
                with db.engine.connect() as conn:
                    try:
                        conn.execute(text("ALTER TABLE publication_nodes ADD COLUMN title_snapshot VARCHAR(200)"))
                        conn.commit()
                    except Exception as e:
                        if "duplicate column name" not in str(e).lower():
                            raise e
                    try:
                        conn.execute(text("ALTER TABLE publication_nodes ADD COLUMN content_snapshot TEXT"))
                        conn.commit()
                    except Exception as e:
                        if "duplicate column name" not in str(e).lower():
                            raise e
                print("✅ Columns added to SQLite database")
                
            elif dialect == 'postgresql':
                # PostgreSQL - use ALTER TABLE with IF NOT EXISTS
                print("Adding columns to PostgreSQL database...")
                try:
                    with db.engine.connect() as conn:
                        conn.execute(text("""
                            ALTER TABLE publication_nodes 
                            ADD COLUMN IF NOT EXISTS title_snapshot VARCHAR(200)
                        """))
                        conn.execute(text("""
                            ALTER TABLE publication_nodes 
                            ADD COLUMN IF NOT EXISTS content_snapshot TEXT
                        """))
                        conn.commit()
                    print("✅ Columns added to PostgreSQL database")
                except Exception as e:
                    if "already exists" in str(e).lower():
                        print("✅ Columns already exist in PostgreSQL database")
                    else:
                        raise e
            
            # Test the fix by creating a sample record
            print("Testing schema fix...")
            test_pub = Publication.query.first()
            if test_pub:
                test_topic = Topic.query.first() 
                if test_topic:
                    # Try to create a publication node
                    test_node = PublicationNode(
                        publication_id=test_pub.id,
                        topic_id=test_topic.id,
                        position=999,
                        parent_id=None,
                        title_snapshot="Test Title",
                        content_snapshot="Test Content"
                    )
                    db.session.add(test_node)
                    db.session.commit()
                    print("✅ Schema fix validated - can create PublicationNode with snapshots")
                    
                    # Clean up test record
                    db.session.delete(test_node)
                    db.session.commit()
                    print("✅ Test record cleaned up")
                else:
                    print("⚠️ No topics found for validation")
            else:
                print("⚠️ No publications found for validation")
                
        except Exception as e:
            print(f"❌ Error fixing schema: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    fix_schema()