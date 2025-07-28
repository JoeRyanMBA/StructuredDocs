#!/usr/bin/env python3
"""
Project-based seeding script for demonstration purposes
Creates sample projects and stakeholders to test the enhanced review workflow
"""

import os
import sys
from datetime import datetime, timedelta

# Simple demonstration data without database dependencies
# This shows the structure that would be created when the full system is implemented

def create_demo_projects():
    """Demo projects for the enhanced review system"""
    
    projects = [
        {
            "id": 1,
            "name": "Census 2030 Survey Methodology",
            "description": "Development of comprehensive survey methodology for the 2030 Census, including sampling techniques, data collection protocols, and quality assurance procedures.",
            "status": "active",
            "start_date": "2025-01-15",
            "target_completion": "2025-12-31",
            "stakeholders": [
                {
                    "id": 1,
                    "name": "Dr. Sarah Johnson",
                    "email": "sarah.johnson@census.gov",
                    "role": "project_manager",
                    "can_review": True,
                    "notes": "Lead project manager, final approval authority"
                },
                {
                    "id": 2,
                    "name": "Prof. Michael Chen",
                    "email": "michael.chen@statistics.gov",
                    "role": "subject_matter_expert",
                    "can_review": True,
                    "notes": "Sampling methodology expert"
                },
                {
                    "id": 3,
                    "name": "Dr. Amanda Rodriguez",
                    "email": "amanda.rodriguez@census.gov",
                    "role": "reviewer",
                    "can_review": True,
                    "notes": "Quality assurance specialist"
                },
                {
                    "id": 4,
                    "name": "Jennifer Kim",
                    "email": "jennifer.kim@census.gov",
                    "role": "stakeholder",
                    "can_review": False,
                    "notes": "Administrative stakeholder"
                }
            ],
            "milestones": [
                {
                    "id": 1,
                    "title": "Sampling Framework Design",
                    "description": "Complete design of sampling framework and methodology",
                    "due_date": "2025-08-15",
                    "status": "in_progress"
                },
                {
                    "id": 2,
                    "title": "Data Collection Protocols",
                    "description": "Finalize data collection protocols and training materials",
                    "due_date": "2025-10-01",
                    "status": "pending"
                },
                {
                    "id": 3,
                    "title": "Final Documentation",
                    "description": "Complete all methodology documentation",
                    "due_date": "2025-12-15",
                    "status": "pending"
                }
            ]
        },
        {
            "id": 2,
            "name": "Labor Statistics Modernization",
            "description": "Updating labor force survey methodologies and implementing new data collection technologies for improved accuracy and efficiency.",
            "status": "planning",
            "start_date": "2025-03-01",
            "target_completion": "2026-06-30",
            "stakeholders": [
                {
                    "id": 5,
                    "name": "Robert Thompson",
                    "email": "robert.thompson@bls.gov",
                    "role": "project_manager",
                    "can_review": True,
                    "notes": "Labor statistics project lead"
                },
                {
                    "id": 6,
                    "name": "Dr. Maria Santos",
                    "email": "maria.santos@dol.gov",
                    "role": "subject_matter_expert",
                    "can_review": True,
                    "notes": "Labor economics specialist"
                },
                {
                    "id": 7,
                    "name": "James Wilson",
                    "email": "james.wilson@bls.gov",
                    "role": "reviewer",
                    "can_review": True,
                    "notes": "Technical review specialist"
                }
            ],
            "milestones": [
                {
                    "id": 4,
                    "title": "Requirements Analysis",
                    "description": "Analyze current labor statistics collection methods",
                    "due_date": "2025-04-30",
                    "status": "pending"
                },
                {
                    "id": 5,
                    "title": "Technology Implementation",
                    "description": "Implement new data collection technologies",
                    "due_date": "2025-12-31",
                    "status": "pending"
                }
            ]
        },
        {
            "id": 3,
            "name": "Economic Indicators Harmonization",
            "description": "Harmonizing economic indicator methodologies across different survey programs to ensure consistency and comparability.",
            "status": "review",
            "start_date": "2024-09-01",
            "target_completion": "2025-08-31",
            "stakeholders": [
                {
                    "id": 8,
                    "name": "Dr. Lisa Chang",
                    "email": "lisa.chang@bea.gov",
                    "role": "project_manager",
                    "can_review": True,
                    "notes": "Economic analysis project manager"
                },
                {
                    "id": 9,
                    "name": "Mark Davis",
                    "email": "mark.davis@census.gov",
                    "role": "subject_matter_expert",
                    "can_review": True,
                    "notes": "Economic indicators expert"
                },
                {
                    "id": 10,
                    "name": "Dr. Patricia White",
                    "email": "patricia.white@fed.gov",
                    "role": "reviewer",
                    "can_review": True,
                    "notes": "Federal statistical standards reviewer"
                }
            ],
            "milestones": [
                {
                    "id": 6,
                    "title": "Methodology Review",
                    "description": "Review all existing economic indicator methodologies",
                    "due_date": "2025-03-15",
                    "status": "completed"
                },
                {
                    "id": 7,
                    "title": "Harmonization Plan",
                    "description": "Develop plan for methodology harmonization",
                    "due_date": "2025-06-30",
                    "status": "in_progress"
                }
            ]
        }
    ]
    
    return projects

def create_demo_reviews():
    """Demo reviews showing project-based assignments"""
    
    reviews = [
        {
            "id": 1,
            "project_id": 1,
            "topic_id": 1,  # Random Sampling Methodology
            "assigned_stakeholder_id": 2,  # Prof. Michael Chen
            "status": "pending",
            "due_date": "2025-08-01",
            "submitted_at": "2025-07-25T10:00:00",
            "submitter_notes": "Please review the sampling methodology section for technical accuracy. Pay special attention to the stratified sampling approach."
        },
        {
            "id": 2,
            "project_id": 1,
            "topic_id": 3,  # Statistical Disclosure Control
            "assigned_stakeholder_id": 3,  # Dr. Amanda Rodriguez
            "status": "in_review",
            "due_date": "2025-07-30",
            "submitted_at": "2025-07-22T14:30:00",
            "submitter_notes": "Need review of privacy protection methods for census data."
        },
        {
            "id": 3,
            "project_id": 2,
            "topic_id": 6,  # Labor Force Participation Rate
            "assigned_stakeholder_id": 6,  # Dr. Maria Santos
            "status": "pending",
            "due_date": "2025-08-15",
            "submitted_at": "2025-07-26T09:00:00",
            "submitter_notes": "Review calculation methodology for accuracy with new data sources."
        }
    ]
    
    return reviews

def print_demo_structure():
    """Print the demo project structure"""
    
    print("🎯 PROJECT-BASED REVIEW SYSTEM DEMO STRUCTURE")
    print("=" * 60)
    
    projects = create_demo_projects()
    reviews = create_demo_reviews()
    
    for project in projects:
        print(f"\n📁 PROJECT: {project['name']}")
        print(f"   Status: {project['status'].title()}")
        print(f"   Timeline: {project['start_date']} → {project['target_completion']}")
        print(f"   Description: {project['description'][:80]}...")
        
        print(f"\n   👥 STAKEHOLDERS ({len(project['stakeholders'])}):")
        for stakeholder in project['stakeholders']:
            role_display = stakeholder['role'].replace('_', ' ').title()
            review_status = "✓ Can Review" if stakeholder['can_review'] else "✗ Cannot Review"
            print(f"      • {stakeholder['name']} - {role_display} ({review_status})")
        
        print(f"\n   🎯 MILESTONES ({len(project['milestones'])}):")
        for milestone in project['milestones']:
            status_icon = {
                'pending': '⏳',
                'in_progress': '🔄',
                'completed': '✅',
                'delayed': '⚠️'
            }.get(milestone['status'], '❓')
            print(f"      {status_icon} {milestone['title']} (Due: {milestone['due_date']})")
    
    print(f"\n📝 ACTIVE REVIEWS ({len(reviews)}):")
    print("-" * 40)
    
    for review in reviews:
        # Find project and stakeholder for context
        project = next(p for p in projects if p['id'] == review['project_id'])
        stakeholder = next(s for s in project['stakeholders'] if s['id'] == review['assigned_stakeholder_id'])
        
        status_icon = {
            'pending': '⏳',
            'in_review': '🔍',
            'approved': '✅',
            'rejected': '❌',
            'revision_requested': '🔄'
        }.get(review['status'], '❓')
        
        print(f"{status_icon} Topic #{review['topic_id']} → {stakeholder['name']}")
        print(f"   Project: {project['name']}")
        print(f"   Due: {review['due_date']} | Status: {review['status'].title()}")
        print(f"   Notes: {review['submitter_notes'][:60]}...")
        print()

if __name__ == "__main__":
    print("🌱 PROJECT-BASED REVIEW SYSTEM DEMONSTRATION")
    print("=" * 60)
    print("\nThis demonstrates the structure of the enhanced review system")
    print("where reviews are organized within project contexts with specific")
    print("stakeholders, milestones, and workflows.\n")
    
    print_demo_structure()
    
    print("\n🎯 KEY BENEFITS:")
    print("• ✅ Project-specific stakeholder management")
    print("• ✅ Context-aware review assignments")  
    print("• ✅ Milestone-driven deadlines")
    print("• ✅ Self-contained review workflows")
    print("• ✅ No external system dependencies")
    
    print("\n🔗 NEXT STEPS:")
    print("1. Navigate to http://localhost:5175/projects")
    print("2. Create new projects and add stakeholders")
    print("3. Go to Topics and test enhanced review modal")
    print("4. Select project context when submitting reviews")
    
    print("\n✨ Ready to test the project-based review workflow!")
