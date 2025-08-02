#!/usr/bin/env python3
"""
Seed project data for StructuredDocs application
Creates sample projects to test task associations
"""

import sys
import os
from datetime import datetime, date

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app import create_app
from models import db, Project

def seed_projects():
    """Create sample projects that match the mock data"""
    print("🚀 Creating sample projects...")
    
    # Create projects that match the mock data from projects route
    project1 = Project(
        name="Census 2030 Survey Methodology",
        description="Development of survey methodology for 2030 Census",
        status="active",
        start_date=date(2025, 1, 15),
        target_completion=date(2025, 12, 31)
    )
    
    project2 = Project(
        name="Labor Statistics Modernization",
        description="Updating labor force survey methodologies", 
        status="planning",
        start_date=date(2025, 3, 1),
        target_completion=date(2026, 6, 30)
    )
    
    db.session.add_all([project1, project2])
    db.session.commit()
    
    print(f"✅ Created {Project.query.count()} projects:")
    for project in Project.query.all():
        print(f"  📁 {project.id}: {project.name} ({project.status})")
    
    return [project1, project2]

def main():
    """Main seeding function"""
    app = create_app()
    
    with app.app_context():
        print("🌱 Seeding project data...")
        
        # Check if projects already exist
        existing_count = Project.query.count()
        if existing_count > 0:
            print(f"⚠️  Found {existing_count} existing projects. Clearing first...")
            Project.query.delete()
            db.session.commit()
        
        # Seed projects
        projects = seed_projects()
        
        print(f"🎉 Project seeding complete! Created {len(projects)} projects.")

if __name__ == "__main__":
    main()
