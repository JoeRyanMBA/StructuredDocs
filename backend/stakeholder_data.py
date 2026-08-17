#!/usr/bin/env python3
"""
Seed the database with sample stakeholders - Flask command version
"""

import json
from datetime import datetime
import os

def seed_stakeholders_data():
    """Return sample stakeholder data"""
    return [
        {
            "name": "Dr. Sarah Johnson",
            "email": "sarah.johnson@example.com",
            "title": "Senior Project Manager",
            "organization": "Data Services Organization",
            "department": "Data Collection Operations",
            "phone": "(301) 555-0101",
            "expertise_areas": json.dumps(["Project Management", "Data Collection", "Survey Design", "Quality Assurance"]),
            "bio": "15+ years experience managing large-scale data and survey operations. Specializes in multi-year project coordination and stakeholder management."
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
            "email": "amanda.rodriguez@example.com",
            "title": "Quality Assurance Specialist",
            "organization": "Data Services Organization",
            "department": "Quality Assurance Division",
            "phone": "(301) 555-0103",
            "expertise_areas": json.dumps(["Quality Control", "Data Validation", "Process Improvement", "Statistical Quality"]),
            "bio": "Specialist in data quality assurance and data validation processes. Leads quality control initiatives across multiple programs."
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

print("Sample stakeholder data prepared. Ready for import via Flask shell.")
