#!/usr/bin/env python3
"""
Test script to demonstrate reusable link management in StructuredDocs
"""

import sys
sys.path.insert(0, '/workspaces/StructuredDocs/backend')

from backend.app import create_app
from backend.models import db, Link, Topic, TopicLink

def test_link_management():
    """Test the Link and TopicLink functionality"""
    app = create_app()
    
    with app.app_context():
        print("🔗 Testing Link Management System...")
        
        # Create some test links
        links_data = [
            {
                'title': 'Form AB-123: Employee Onboarding',
                'url': 'https://company.com/forms/ab-123',
                'description': 'Standard form for new employee onboarding process',
                'reference_code': 'AB-123',
                'link_type': 'form',
                'is_internal': True,
                'created_by': 'admin'
            },
            {
                'title': 'Safety Policy Document',
                'url': 'https://company.com/policies/safety-001',
                'description': 'Comprehensive workplace safety guidelines',
                'reference_code': 'POL-SAFETY-001',
                'link_type': 'policy',
                'is_internal': True,
                'created_by': 'admin'
            },
            {
                'title': 'External Regulation Reference',
                'url': 'https://osha.gov/regulations/standard-1910',
                'description': 'OSHA safety standards',
                'reference_code': 'OSHA-1910',
                'link_type': 'regulation',
                'is_internal': False,
                'created_by': 'admin'
            }
        ]
        
        # Create links
        created_links = []
        for link_data in links_data:
            link = Link(**link_data)
            db.session.add(link)
            created_links.append(link)
        
        db.session.commit()
        print(f"✅ Created {len(created_links)} test links")
        
        # Create test topics
        topics_data = [
            {
                'title': 'Employee Onboarding Process',
                'content': 'This topic covers the complete employee onboarding workflow.',
                'status': 'draft'
            },
            {
                'title': 'Workplace Safety Guidelines',
                'content': 'Essential safety protocols for all employees.',
                'status': 'published'
            }
        ]
        
        created_topics = []
        for topic_data in topics_data:
            topic = Topic(**topic_data)
            db.session.add(topic)
            created_topics.append(topic)
        
        db.session.commit()
        print(f"✅ Created {len(created_topics)} test topics")
        
        # Link topics to reusable links
        topic_links_data = [
            # Employee Onboarding topic uses form AB-123
            {
                'topic': created_topics[0],
                'link': created_links[0],  # AB-123 form
                'context': 'Required form for all new hires',
                'position': 1
            },
            # Safety topic uses safety policy and OSHA regulation
            {
                'topic': created_topics[1],
                'link': created_links[1],  # Safety Policy
                'context': 'Internal company safety policy',
                'position': 1
            },
            {
                'topic': created_topics[1],
                'link': created_links[2],  # OSHA regulation
                'context': 'Federal safety requirements',
                'position': 2
            },
            # Onboarding topic also references safety policy
            {
                'topic': created_topics[0],
                'link': created_links[1],  # Safety Policy (reused!)
                'context': 'Safety briefing during onboarding',
                'position': 2
            }
        ]
        
        created_topic_links = []
        for tl_data in topic_links_data:
            topic_link = TopicLink(
                topic_id=tl_data['topic'].id,
                link_id=tl_data['link'].id,
                context=tl_data['context'],
                position=tl_data['position']
            )
            db.session.add(topic_link)
            created_topic_links.append(topic_link)
        
        db.session.commit()
        print(f"✅ Created {len(created_topic_links)} topic-link relationships")
        
        # Demonstrate link reuse
        print("\n📊 Link Usage Analysis:")
        print("=" * 50)
        
        for link in created_links:
            usage_count = len(link.topic_links)
            print(f"🔗 {link.title} ({link.reference_code})")
            print(f"   Type: {link.link_type}")
            print(f"   Used in {usage_count} topics:")
            
            for tl in link.topic_links:
                print(f"   - {tl.topic.title}: {tl.context}")
            print()
        
        # Show topic with their links
        print("\n📄 Topics and Their Links:")
        print("=" * 50)
        
        for topic in created_topics:
            topic_data = topic.to_dict(include_links=True)
            print(f"📄 {topic_data['title']}")
            print(f"   Status: {topic_data['status']}")
            print(f"   Links ({topic_data['links_count']}):")
            
            for link_rel in topic_data['links']:
                link = Link.query.get(link_rel['link_id'])
                print(f"   - {link.title} ({link.reference_code})")
                print(f"     Context: {link_rel['context']}")
                print(f"     URL: {link.url}")
            print()
        
        # Test finding links by reference code
        print("\n🔍 Finding Links by Reference Code:")
        print("=" * 50)
        
        test_refs = ['AB-123', 'POL-SAFETY-001', 'OSHA-1910']
        for ref_code in test_refs:
            link = Link.query.filter_by(reference_code=ref_code).first()
            if link:
                print(f"✅ Found: {ref_code} -> {link.title}")
                print(f"   Used in {len(link.topic_links)} topics")
            else:
                print(f"❌ Not found: {ref_code}")
        
        # Test searching links
        print("\n🔍 Link Search Examples:")
        print("=" * 50)
        
        # Search by title
        safety_links = Link.query.filter(Link.title.ilike('%safety%')).all()
        print(f"Links containing 'safety': {len(safety_links)}")
        for link in safety_links:
            print(f"  - {link.title}")
        
        # Search by type
        form_links = Link.query.filter_by(link_type='form').all()
        print(f"Form links: {len(form_links)}")
        for link in form_links:
            print(f"  - {link.title} ({link.reference_code})")
        
        # Clean up test data
        print("\n🧹 Cleaning up test data...")
        
        # Delete topic links (will cascade)
        TopicLink.query.filter(TopicLink.topic_id.in_([t.id for t in created_topics])).delete()
        
        # Delete topics
        for topic in created_topics:
            db.session.delete(topic)
        
        # Delete links
        for link in created_links:
            db.session.delete(link)
        
        db.session.commit()
        print("✅ Test data cleaned up")
        
        print("\n🎉 Link Management System Test Complete!")
        print("\nKey Features Demonstrated:")
        print("✅ Creating reusable link objects")
        print("✅ Linking topics to reusable links with context")
        print("✅ Link reuse across multiple topics")
        print("✅ Reference code tracking (e.g., AB-123)")
        print("✅ Link categorization by type")
        print("✅ Usage tracking and analytics")
        print("✅ Search functionality")

def show_api_examples():
    """Show examples of how to use the API endpoints"""
    print("\n🔌 API Usage Examples:")
    print("=" * 50)
    
    examples = [
        {
            'description': 'Create a new reusable link',
            'method': 'POST',
            'url': '/api/links',
            'body': {
                'title': 'Form AB-123: Employee Onboarding',
                'url': 'https://company.com/forms/ab-123',
                'description': 'Standard form for new employee onboarding',
                'reference_code': 'AB-123',
                'link_type': 'form',
                'is_internal': True
            }
        },
        {
            'description': 'Get all links with usage information',
            'method': 'GET',
            'url': '/api/links?include_usage=true',
            'body': None
        },
        {
            'description': 'Search for form links',
            'method': 'GET',
            'url': '/api/links?type=form',
            'body': None
        },
        {
            'description': 'Find link by reference code',
            'method': 'GET',
            'url': '/api/links?reference_code=AB-123',
            'body': None
        },
        {
            'description': 'Add link to a topic',
            'method': 'POST',
            'url': '/api/links/123/topics',
            'body': {
                'topic_id': 456,
                'context': 'Required form for onboarding process',
                'position': 1
            }
        },
        {
            'description': 'Get all links for a topic',
            'method': 'GET',
            'url': '/api/topics/456?include_links=true',
            'body': None
        },
        {
            'description': 'Search topic content for potential link references',
            'method': 'POST',
            'url': '/api/links/search-references',
            'body': {
                'content': 'Please complete form AB-123 and review policy DOC-456'
            }
        }
    ]
    
    for example in examples:
        print(f"📝 {example['description']}")
        print(f"   {example['method']} {example['url']}")
        if example['body']:
            print(f"   Body: {example['body']}")
        print()

if __name__ == '__main__':
    test_link_management()
    show_api_examples()
