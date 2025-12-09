#!/usr/bin/env python3
"""Apply the enum fix directly to fix the ProjectStakeholder role issue"""
import os
import sys

# Set up path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.extensions import db
from backend.app import create_app

app = create_app()

with app.app_context():
    print("🔧 Fixing ProjectStakeholder role enum...")
    
    try:
        # Create new enum type
        print("Creating new project_stakeholder_role enum...")
        db.session.execute(db.text("""
            DO $$ BEGIN
                CREATE TYPE project_stakeholder_role AS ENUM ('project_manager', 'subject_matter_expert', 'reviewer', 'stakeholder', 'sponsor');
            EXCEPTION
                WHEN duplicate_object THEN 
                    raise notice 'Type project_stakeholder_role already exists';
            END $$;
        """))
        db.session.commit()
        print("✅ Enum type created (or already exists)")
    except Exception as e:
        print(f"⚠️  Error creating enum: {e}")
        db.session.rollback()
    
    try:
        # Alter the column to use the new enum
        print("Altering project_stakeholders.role to use new enum...")
        db.session.execute(db.text("""
            ALTER TABLE project_stakeholders 
            ALTER COLUMN role TYPE project_stakeholder_role 
            USING role::text::project_stakeholder_role;
        """))
        db.session.commit()
        print("✅ Column type changed successfully")
    except Exception as e:
        print(f"❌ Error altering column: {e}")
        db.session.rollback()
        raise
    
    print("🎉 Migration complete!")
