#!/usr/bin/env python3
"""
Database seeding script for StructuredDocs application
Creates sample data for testing the review workflow and other features
"""

import os
import sys
from datetime import datetime, timedelta
from app import create_app
from models import db, Topic, Collection, ImportDocument, ImportItem, Publication, PublicationNode

def seed_collections():
    """Create sample collections with hierarchical structure"""
    print("📁 Creating sample collections...")
    
    # Root collections
    now = datetime.utcnow()
    methodology = Collection(name="Survey Methodology", form_number="COLL-001", position=1, created_at=now, updated_at=now)
    demographics = Collection(name="Demographics & Population", form_number="COLL-002", position=2, created_at=now, updated_at=now)
    economics = Collection(name="Economic Statistics", form_number="COLL-003", position=3, created_at=now, updated_at=now)
    
    db.session.add_all([methodology, demographics, economics])
    db.session.flush()  # Get IDs
    
    # Sub-collections under Survey Methodology
    sampling = Collection(name="Sampling Techniques", form_number="COLL-004", parent_id=methodology.id, position=1, created_at=now, updated_at=now)
    data_collection = Collection(name="Data Collection Methods", form_number="COLL-005", parent_id=methodology.id, position=2, created_at=now, updated_at=now)
    quality_control = Collection(name="Quality Control", form_number="COLL-006", parent_id=methodology.id, position=3, created_at=now, updated_at=now)

    # Sub-collections under Demographics
    census_data = Collection(name="Census Data Analysis", form_number="COLL-007", parent_id=demographics.id, position=1, created_at=now, updated_at=now)
    population_estimates = Collection(name="Population Estimates", form_number="COLL-008", parent_id=demographics.id, position=2, created_at=now, updated_at=now)

    # Sub-collections under Economics
    employment = Collection(name="Employment Statistics", form_number="COLL-009", parent_id=economics.id, position=1, created_at=now, updated_at=now)
    income_poverty = Collection(name="Income & Poverty", form_number="COLL-010", parent_id=economics.id, position=2, created_at=now, updated_at=now)
    
    db.session.add_all([
        sampling, data_collection, quality_control,
        census_data, population_estimates,
        employment, income_poverty
    ])
    
    return {
        'methodology': methodology,
        'demographics': demographics,
        'economics': economics,
        'sampling': sampling,
        'data_collection': data_collection,
        'quality_control': quality_control,
        'census_data': census_data,
        'population_estimates': population_estimates,
        'employment': employment,
        'income_poverty': income_poverty
    }

def seed_topics(collections):
    """Create sample topics in various statuses"""
    print("📄 Creating sample topics...")
    
    topics_data = [
        # Draft topics (can be sent for review)
        {
            'title': 'Random Sampling Methodology for Large Scale Surveys',
            'content': '''# Random Sampling Methodology

## Overview
This document outlines the standard procedures for implementing random sampling in large-scale demographic surveys.

## Key Principles
- **Simple Random Sampling**: Every member of the population has an equal chance of selection
- **Stratified Sampling**: Population is divided into strata before sampling
- **Cluster Sampling**: Natural groupings are used as sampling units

## Implementation Steps
1. Define the target population
2. Create a sampling frame
3. Determine sample size using power analysis
4. Execute randomization procedure
5. Document selection process

## Quality Assurance
- Verify randomization algorithms
- Check for selection bias
- Monitor response rates
- Validate sample representativeness

## References
- Cochran, W.G. (1977). Sampling Techniques
- Lohr, S.L. (2019). Sampling: Design and Analysis''',
            'status': 'draft',
            'collection': 'sampling'
        },
        {
            'title': 'Computer-Assisted Personal Interviewing (CAPI) Best Practices',
            'content': '''# CAPI Best Practices

## Introduction
Computer-Assisted Personal Interviewing (CAPI) has revolutionized data collection in demographic surveys.

## Equipment Requirements
- Tablet devices with minimum 8GB RAM
- Survey software with offline capability
- Backup power solutions
- Secure data transmission protocols

## Interviewer Training
### Technical Training
- Software navigation
- Data validation procedures
- Troubleshooting common issues

### Survey Administration
- Professional interviewing techniques
- Handling sensitive questions
- Managing respondent concerns

## Data Quality Measures
- Real-time validation checks
- Consistency verification
- Automated skip patterns
- Response time monitoring''',
            'status': 'draft',
            'collection': 'data_collection'
        },
        {
            'title': 'Statistical Disclosure Control in Census Publications',
            'content': '''# Statistical Disclosure Control

## Purpose
Protecting individual privacy while maintaining data utility in census publications.

## Methods
- Cell suppression for small counts
- Data swapping techniques
- Adding statistical noise
- Top/bottom coding

## Implementation Guidelines
- Minimum cell size thresholds
- Secondary suppression rules
- Consistency across products
- Documentation requirements''',
            'status': 'draft',
            'collection': 'census_data'
        },
        
        # Published topics
        {
            'title': 'Quality Control Procedures for Survey Data',
            'content': '''# Quality Control Procedures

## Data Validation Framework
Comprehensive procedures for ensuring data quality throughout the survey lifecycle.

## Pre-Collection Validation
- Questionnaire testing
- System validation
- Interviewer certification

## During Collection
- Real-time monitoring
- Progress tracking
- Quality indicators

## Post-Collection
- Data cleaning procedures
- Outlier detection
- Consistency checks
- Final validation''',
            'status': 'published',
            'collection': 'quality_control'
        },
        {
            'title': 'Population Estimation Methodology',
            'content': '''# Population Estimation Methodology

## Cohort-Component Method
The primary method for producing population estimates.

## Data Sources
- Birth certificates
- Death certificates  
- Immigration records
- Emigration estimates
- Internal migration data

## Calculation Process
1. Start with base population (Census)
2. Add births
3. Subtract deaths
4. Add net international migration
5. Add net domestic migration

## Validation
- Compare with administrative records
- Analyze age-sex distributions
- Review historical trends''',
            'status': 'published',
            'collection': 'population_estimates'
        },
        
        # Topics in pending review (using current schema)
        {
            'title': 'Labor Force Participation Rate Calculation',
            'content': '''# Labor Force Participation Rate

## Definition
The labor force participation rate represents the proportion of the working-age population that is economically active.

## Formula
LFPR = (Labor Force / Working-Age Population) × 100

Where:
- Labor Force = Employed + Unemployed
- Working-Age Population = Population aged 16+

## Data Collection
- Current Population Survey (CPS)
- Monthly collection
- Sample size: ~60,000 households

## Seasonal Adjustment
- X-13ARIMA-SEATS method
- Holiday adjustments
- Extreme value detection

## Publication Schedule
- Monthly release
- First Friday of each month
- Preliminary and revised estimates''',
            'status': 'draft',  # Changed from pending_review since that status may not exist yet
            'collection': 'employment'
        },
        
        # More draft topics for testing review workflow
        {
            'title': 'Income Distribution Analysis Methods',
            'content': '''# Income Distribution Analysis

## Overview
Methods for analyzing income distribution patterns in survey data.

## Key Metrics
- Median household income
- Income percentiles
- Gini coefficient
- Income inequality measures

## Data Sources
- American Community Survey
- Current Population Survey
- Survey of Income and Program Participation

## Methodology
- Data collection procedures
- Sample weighting
- Missing data imputation
- Variance estimation''',
            'status': 'draft',
            'collection': 'income_poverty'
        },
        
        # Archived topic
        {
            'title': 'Legacy Survey Processing Methods (Archived)',
            'content': '''# Legacy Survey Processing

## Historical Context
This document describes survey processing methods used prior to 2020.

## Paper-Based Systems
- Manual data entry
- Physical questionnaire storage
- Batch processing procedures

## Note
This methodology has been superseded by digital processing systems.
Retained for historical reference only.''',
            'status': 'archived',
            'collection': 'data_collection'
        }
    ]
    
    created_topics = []
    for topic_data in topics_data:
        # Only use fields that exist in current schema
        topic = Topic(
            title=topic_data['title'],
            content=topic_data['content'],
            status=topic_data['status']
        )
        created_topics.append(topic)
        db.session.add(topic)
    
    db.session.flush()  # Get topic IDs
    
    # Associate topics with collections
    from models import collection_topic_tree
    for i, topic_data in enumerate(topics_data):
        collection = collections[topic_data['collection']]
        db.session.execute(
            collection_topic_tree.insert().values(
                collection_id=collection.id,
                topic_id=created_topics[i].id,
                parent_topic_id=None,
                position=i + 1
            )
        )
    
    return created_topics

def seed_import_documents():
    """Create sample import documents for testing review workflow"""
    print("📥 Creating sample import documents...")
    
    imports_data = [
        {
            'filename': 'survey_methodology_guide.docx',
            'source_type': 'word',
            'status': 'staging',
            'review_step': 'pending',
            'items': [
                {
                    'title': 'Introduction to Survey Design',
                    'content': 'Overview of survey methodology principles and best practices.'
                },
                {
                    'title': 'Sampling Frame Construction',
                    'content': 'Guidelines for building comprehensive sampling frames.'
                },
                {
                    'title': 'Response Rate Optimization',
                    'content': 'Strategies for maximizing survey response rates.'
                }
            ]
        },
        {
            'filename': 'data_quality_standards.md',
            'source_type': 'markdown',
            'status': 'approved',
            'review_step': 'final_approved',
            'reviewer': 'Dr. Sarah Johnson',
            'items': [
                {
                    'title': 'Data Validation Rules',
                    'content': 'Comprehensive validation rules for survey data.'
                },
                {
                    'title': 'Error Detection Methods',
                    'content': 'Automated and manual error detection procedures.'
                }
            ]
        },
        {
            'filename': 'census_processing_workflow.docx',
            'source_type': 'word',
            'status': 'staging',
            'review_step': 'sme_approved',
            'reviewer': 'Prof. Michael Chen',
            'items': [
                {
                    'title': 'Data Processing Pipeline',
                    'content': 'Step-by-step census data processing workflow.'
                },
                {
                    'title': 'Quality Assurance Checkpoints',
                    'content': 'Critical quality control points in the processing pipeline.'
                }
            ]
        }
    ]
    
    created_imports = []
    for import_data in imports_data:
        import_doc = ImportDocument(
            filename=import_data['filename'],
            source_type=import_data['source_type'],
            status=import_data['status'],
            review_step=import_data['review_step'],
            reviewer=import_data.get('reviewer'),
            reviewed_at=datetime.utcnow() - timedelta(days=2) if import_data.get('reviewer') else None
        )
        created_imports.append(import_doc)
        db.session.add(import_doc)
        db.session.flush()
        
        # Add import items
        for item_data in import_data['items']:
            item = ImportItem(
                document_id=import_doc.id,
                heading_order=len(import_doc.items) + 1,
                title=item_data['title'],
                content=item_data['content']
            )
            db.session.add(item)
    
    return created_imports

def seed_publications():
    """Create sample publications"""
    print("📚 Creating sample publications...")
    
    pub1 = Publication(
        title="Survey Methodology Handbook 2025",
        description="Comprehensive guide to modern survey methodology practices"
    )
    
    pub2 = Publication(
        title="Data Quality Standards Manual",
        description="Standards and procedures for maintaining data quality"
    )
    
    db.session.add_all([pub1, pub2])
    db.session.flush()
    
    return [pub1, pub2]

def main():
    """Main seeding function"""
    print("🌱 Starting database seeding...")
    
    app = create_app()
    
    from models import User
    from werkzeug.security import generate_password_hash
    with app.app_context():
        try:
            # Clear existing data (optional - comment out if you want to keep existing data)
            print("🧹 Clearing existing data...")
            db.session.execute(db.text("DELETE FROM collection_topic_tree"))
            PublicationNode.query.delete()
            Publication.query.delete()
            ImportItem.query.delete()
            ImportDocument.query.delete()
            Topic.query.delete()
            Collection.query.delete()
            User.query.delete()

            # Create default admin user only
            print("👤 Creating default admin user...")
            admin_user = User(
                name="Admin User",
                email="admin@example.com",
                password_hash=generate_password_hash("admin123"),
                role="admin",
                active=True
            )
            db.session.add(admin_user)

            # Commit only the admin user
            db.session.commit()

            print("\n✅ Database seeding completed successfully!")
            print("� Created 1 admin user (admin@example.com)")
            print("No collections, topics, import documents, or publications were seeded.")

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error during seeding: {e}")
            raise

if __name__ == "__main__":
    main()
