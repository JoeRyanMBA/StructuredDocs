#!/usr/bin/env python3
"""
Seed the database with sample stakeholders
"""

import json
import sys
import os
from datetime import datetime

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import Flask and create app manually to avoid import issues
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Create Flask app
app = Flask(__name__)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'postgresql://super:Picklehead1!@JoeRyanMBA-4757.postgres.pythonanywhere-services.com:14757/structured_docs'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Import models after db is configured
from models import Stakeholder, Project, ProjectStakeholder, ProjectMilestone

def seed_stakeholders():
    """Create sample stakeholders in the database"""
    
    # Sample stakeholders with varied backgrounds
    stakeholders_data = [
        {
            "name": "Dr. Sarah Johnson",
            "email": "sarah.johnson@census.gov",
            "title": "Senior Project Manager",
            "organization": "U.S. Census Bureau",
            "department": "Data Collection Operations",
            "phone": "(301) 555-0101",
            "expertise_areas": json.dumps(["Project Management", "Data Collection", "Survey Design", "Quality Assurance"]),
            "bio": "15+ years experience managing large-scale census and survey operations. Specializes in multi-year project coordination and stakeholder management."
        },
        {
            "name": "Prof. Michael Chen",
            "email": "michael.chen@statistics.gov",
            "title": "Chief Statistician",
            "organization": "Bureau of Labor Statistics",
            "department": "Statistical Methods Division",
            "phone": "(202) 555-0102",
            "expertise_areas": json.dumps(["Statistical Methodology", "Sampling Theory", "Labor Economics", "Survey Analysis"]),
            "bio": "PhD in Statistics with 20+ years in federal statistical agencies. Expert in complex survey design and statistical inference."
        },
        {
            "name": "Dr. Amanda Rodriguez",
            "email": "amanda.rodriguez@census.gov",
            "title": "Quality Assurance Specialist",
            "organization": "U.S. Census Bureau",
            "department": "Quality Assurance Division",
            "phone": "(301) 555-0103",
            "expertise_areas": json.dumps(["Quality Control", "Data Validation", "Process Improvement", "Statistical Quality"]),
            "bio": "Specialist in survey quality assurance and data validation processes. Leads quality control initiatives across multiple Census programs."
        },
        {
            "name": "James Wilson",
            "email": "james.wilson@commerce.gov",
            "title": "Program Director",
            "organization": "Department of Commerce",
            "department": "Strategic Planning",
            "phone": "(202) 555-0104",
            "expertise_areas": json.dumps(["Strategic Planning", "Program Management", "Policy Development", "Stakeholder Relations"]),
            "bio": "Senior executive with expertise in federal program development and strategic planning. Oversees multiple statistical initiatives."
        },
        {
            "name": "Dr. Lisa Park",
            "email": "lisa.park@nist.gov",
            "title": "Research Economist",
            "organization": "National Institute of Standards and Technology",
            "department": "Economic Analysis Office",
            "phone": "(301) 555-0105",
            "expertise_areas": json.dumps(["Economic Analysis", "Research Methods", "Data Science", "Predictive Modeling"]),
            "bio": "PhD in Economics with focus on federal data programs. Conducts research on economic indicators and measurement standards."
        },
        {
            "name": "David Kim",
            "email": "david.kim@treasury.gov",
            "title": "Senior Policy Analyst",
            "organization": "Department of Treasury",
            "department": "Office of Economic Policy",
            "phone": "(202) 555-0106",
            "expertise_areas": json.dumps(["Economic Policy", "Fiscal Analysis", "Data Integration", "Report Writing"]),
            "bio": "Policy analyst specializing in economic data integration and fiscal impact analysis. Regular contributor to economic reports."
        },
        {
            "name": "Dr. Jennifer Martinez",
            "email": "jennifer.martinez@ed.gov",
            "title": "Education Research Director",
            "organization": "Department of Education",
            "department": "Institute of Education Sciences",
            "phone": "(202) 555-0107",
            "expertise_areas": json.dumps(["Education Research", "Survey Design", "Longitudinal Studies", "Student Assessment"]),
            "bio": "Leading researcher in education statistics and assessment. Manages national education data collection programs."
        },
        {
            "name": "Robert Thompson",
            "email": "robert.thompson@hhs.gov",
            "title": "Health Survey Coordinator",
            "organization": "Department of Health and Human Services",
            "department": "National Center for Health Statistics",
            "phone": "(301) 555-0108",
            "expertise_areas": json.dumps(["Health Surveys", "Epidemiology", "Public Health Data", "Survey Operations"]),
            "bio": "Coordinates national health surveys and surveillance systems. Expert in health data collection and public health statistics."
        },
        {
            "name": "Dr. Angela White",
            "email": "angela.white@usda.gov",
            "title": "Agricultural Economist",
            "organization": "U.S. Department of Agriculture",
            "department": "Economic Research Service",
            "phone": "(202) 555-0109",
            "expertise_areas": json.dumps(["Agricultural Economics", "Rural Statistics", "Farm Surveys", "Economic Modeling"]),
            "bio": "Economist specializing in agricultural data and rural economic analysis. Leads farm and ranch survey initiatives."
        },
        {
            "name": "Mark Davis",
            "email": "mark.davis@dol.gov",
            "title": "Labor Statistics Analyst",
            "organization": "Department of Labor",
            "department": "Bureau of Labor Statistics",
            "phone": "(202) 555-0110",
            "expertise_areas": json.dumps(["Labor Statistics", "Employment Data", "Wage Analysis", "Workforce Studies"]),
            "bio": "Analyst focused on employment and wage statistics. Contributes to monthly employment reports and workforce analysis."
        },
        {
            "name": "Dr. Karen Garcia",
            "email": "karen.garcia@epa.gov",
            "title": "Environmental Data Scientist",
            "organization": "Environmental Protection Agency",
            "department": "Office of Research and Development",
            "phone": "(202) 555-0111",
            "expertise_areas": json.dumps(["Environmental Data", "Air Quality", "Water Quality", "Climate Statistics"]),
            "bio": "Data scientist specializing in environmental monitoring and reporting. Expert in environmental indicator development."
        },
        {
            "name": "Thomas Anderson",
            "email": "thomas.anderson@gsa.gov",
            "title": "IT Project Manager",
            "organization": "General Services Administration",
            "department": "Office of Government-wide Policy",
            "phone": "(202) 555-0112",
            "expertise_areas": json.dumps(["IT Project Management", "System Integration", "Data Architecture", "Digital Services"]),
            "bio": "Technology project manager with expertise in government IT systems and data architecture. Leads digital transformation initiatives."
        }
    ]

    print("🌱 Seeding stakeholders...")
    
    # Create stakeholders
    created_count = 0
    for stakeholder_data in stakeholders_data:
        # Check if stakeholder already exists
        existing = Stakeholder.query.filter_by(email=stakeholder_data['email']).first()
        if not existing:
            stakeholder = Stakeholder(**stakeholder_data)
            db.session.add(stakeholder)
            created_count += 1
            print(f"  ✅ Created: {stakeholder_data['name']} ({stakeholder_data['email']})")
        else:
            print(f"  ⏭️  Exists: {stakeholder_data['name']} ({stakeholder_data['email']})")

    # Commit stakeholders
    try:
        db.session.commit()
        print(f"\n✅ Successfully created {created_count} new stakeholders!")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creating stakeholders: {e}")
        return

    # Create a sample project with stakeholders
    print("\n🚀 Creating sample project with stakeholders...")
    
    # Check if sample project exists
    sample_project = Project.query.filter_by(name="Census 2030 Modernization Initiative").first()
    if not sample_project:
        # Create project
        sample_project = Project(
            name="Census 2030 Modernization Initiative",
            description="Comprehensive modernization of census data collection and processing systems for the 2030 Census. This multi-year initiative includes survey methodology updates, technology infrastructure improvements, and enhanced data quality processes.",
            status="active",
            start_date=datetime(2025, 1, 15).date(),
            target_completion=datetime(2029, 12, 31).date()
        )
        db.session.add(sample_project)
        db.session.commit()
        print(f"  ✅ Created project: {sample_project.name}")

        # Add stakeholders to project
        stakeholder_assignments = [
            ("sarah.johnson@census.gov", "project_manager", "Lead project manager with final approval authority"),
            ("michael.chen@statistics.gov", "subject_matter_expert", "Statistical methodology expert and advisor"),
            ("amanda.rodriguez@census.gov", "reviewer", "Quality assurance lead for all deliverables"),
            ("james.wilson@commerce.gov", "sponsor", "Executive sponsor and strategic oversight"),
            ("lisa.park@nist.gov", "subject_matter_expert", "Economic measurement standards consultant"),
            ("david.kim@treasury.gov", "reviewer", "Policy review and economic impact analysis")
        ]

        for email, role, notes in stakeholder_assignments:
            stakeholder = Stakeholder.query.filter_by(email=email).first()
            if stakeholder:
                project_stakeholder = ProjectStakeholder(
                    project_id=sample_project.id,
                    stakeholder_id=stakeholder.id,
                    role=role,
                    notes=notes,
                    can_review=True
                )
                db.session.add(project_stakeholder)
                print(f"    ✅ Assigned: {stakeholder.name} as {role}")

        # Add sample milestones
        milestones = [
            ("Requirements Analysis Complete", "Complete analysis of current systems and requirements for 2030 Census", datetime(2025, 6, 30).date(), "completed"),
            ("Technology Architecture Design", "Finalize technology architecture and system design specifications", datetime(2025, 9, 15).date(), "in-progress"),
            ("Pilot Testing Phase", "Conduct pilot testing of new data collection methods", datetime(2026, 3, 31).date(), "planned"),
            ("Staff Training Program", "Complete training program for all census field staff", datetime(2026, 8, 30).date(), "planned"),
            ("System Integration Testing", "Complete integration testing of all system components", datetime(2027, 12, 31).date(), "planned"),
            ("Dress Rehearsal Census", "Conduct full dress rehearsal in select areas", datetime(2028, 6, 30).date(), "planned"),
            ("Full Implementation", "Complete deployment for 2030 Census operations", datetime(2029, 12, 31).date(), "planned")
        ]

        for name, description, date, status in milestones:
            milestone = ProjectMilestone(
                project_id=sample_project.id,
                name=name,
                description=description,
                date=date,
                status=status
            )
            db.session.add(milestone)
            print(f"    ✅ Added milestone: {name}")

        try:
            db.session.commit()
            print(f"\n✅ Sample project created with {len(stakeholder_assignments)} stakeholders and {len(milestones)} milestones!")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating sample project: {e}")
    else:
        print(f"  ⏭️  Sample project already exists: {sample_project.name}")

def main():
    """Main function to run the seeding"""
    
    with app.app_context():
        print("🎯 Starting stakeholder database seeding...")
        print(f"📊 Current stakeholder count: {Stakeholder.query.count()}")
        print(f"📁 Current project count: {Project.query.count()}")
        print()
        
        seed_stakeholders()
        
        print(f"\n📊 Final stakeholder count: {Stakeholder.query.count()}")
        print(f"📁 Final project count: {Project.query.count()}")
        print("\n🎉 Stakeholder seeding complete!")

if __name__ == "__main__":
    main()
