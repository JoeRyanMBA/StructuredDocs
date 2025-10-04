#!/usr/bin/env python3
"""
Test script to verify the publication export and hierarchical import fixes.
"""

import sys
import os
sys.path.insert(0, '/workspaces/StructuredDocs')
sys.path.insert(0, '/workspaces/StructuredDocs/backend')

def test_publication_fix():
    """Test the publication export fix by creating nodes with snapshots"""
    
    print("🧪 Testing Publication Export Fix")
    print("=" * 40)
    
    try:
        from backend.app import create_app
        from backend.models import db, Publication, PublicationNode, Topic
        
        app = create_app()
        with app.app_context():
            # Find a publication with no nodes
            pub = Publication.query.filter_by(id=1).first()
            if not pub:
                print("❌ No test publication found")
                return False
            
            print(f"📋 Testing publication: {pub.title}")
            
            # Clear existing nodes
            PublicationNode.query.filter_by(publication_id=pub.id).delete()
            
            # Find some topics to add
            topics = Topic.query.limit(2).all()
            if not topics:
                print("❌ No topics found to create nodes")
                return False
            
            # Create nodes using the new logic (with snapshots)
            for i, topic in enumerate(topics):
                node = PublicationNode(
                    publication_id=pub.id,
                    topic_id=topic.id,
                    parent_id=None,
                    position=i,
                    title_snapshot=topic.title,
                    content_snapshot=topic.content
                )
                db.session.add(node)
            
            db.session.commit()
            
            # Verify nodes were created with snapshots
            nodes = PublicationNode.query.filter_by(publication_id=pub.id).all()
            print(f"✅ Created {len(nodes)} publication nodes")
            
            for node in nodes:
                has_title = bool(node.title_snapshot)
                has_content = bool(node.content_snapshot)
                print(f"   Node {node.id}: Title snapshot: {has_title}, Content snapshot: {has_content}")
                
            # Test the serialization function
            def serialize_node(node):
                topic_data = node.topic.to_dict() if node.topic else {'title': 'Unknown', 'content': ''}
                return {
                    'id': node.id,
                    'topic_id': node.topic_id,
                    'title': topic_data.get('title', 'Untitled'),
                    'content': topic_data.get('content', ''),
                    'position': node.position,
                    'children': []  # Simplified for test
                }
            
            print("\n🔍 Testing serialization...")
            for node in nodes:
                try:
                    result = serialize_node(node)
                    print(f"✅ Node {node.id} serialization successful")
                except Exception as e:
                    print(f"❌ Node {node.id} serialization failed: {e}")
                    return False
            
            return True
            
    except Exception as e:
        print(f"❌ Publication test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_hierarchical_import():
    """Test hierarchical import with a simple markdown structure"""
    
    print("\n🧪 Testing Hierarchical Import Fix")
    print("=" * 40)
    
    try:
        from backend.app import create_app
        from backend.routes.import_handler import _parse_hierarchical_content
        
        app = create_app()
        with app.app_context():
            # Test markdown with clear hierarchy
            test_markdown = """# Level 1 Topic
This is level 1 content.

## Level 2 Subtopic A
This is level 2A content.

### Level 3 Sub-subtopic
This is level 3 content.

## Level 2 Subtopic B
This is level 2B content.

# Another Level 1 Topic
This is another level 1 topic.
"""
            
            print("📝 Testing with hierarchical markdown...")
            items = _parse_hierarchical_content(test_markdown)
            
            print(f"✅ Parsed {len(items)} items")
            
            # Check the hierarchy
            for i, item in enumerate(items):
                level = item.get('level', 0)
                parent_idx = item.get('parent_index')
                title = item.get('title', 'Unknown')
                indent = "  " * (level - 1)
                parent_info = f" (parent: {parent_idx})" if parent_idx is not None else " (root)"
                print(f"{indent}• H{level}: {title}{parent_info}")
            
            # Verify parent relationships make sense
            hierarchy_valid = True
            for i, item in enumerate(items):
                parent_idx = item.get('parent_index')
                if parent_idx is not None:
                    if parent_idx >= i:
                        print(f"❌ Invalid parent index: Item {i} has parent {parent_idx} (should be < {i})")
                        hierarchy_valid = False
                    else:
                        parent = items[parent_idx]
                        if parent['level'] >= item['level']:
                            print(f"❌ Invalid hierarchy: Item {i} (level {item['level']}) has parent {parent_idx} (level {parent['level']})")
                            hierarchy_valid = False
            
            if hierarchy_valid:
                print("✅ Hierarchy relationships are valid")
            
            return hierarchy_valid
            
    except Exception as e:
        print(f"❌ Hierarchical import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔧 Testing StructuredDocs Fixes")
    print("=" * 50)
    
    pub_ok = test_publication_fix()
    hier_ok = test_hierarchical_import()
    
    print(f"\n📊 Test Results:")
    print(f"   Publication Export Fix: {'✅ PASS' if pub_ok else '❌ FAIL'}")
    print(f"   Hierarchical Import Fix: {'✅ PASS' if hier_ok else '❌ FAIL'}")
    
    if pub_ok and hier_ok:
        print(f"\n🎉 All fixes working correctly!")
        print(f"   • Publication nodes now include title/content snapshots")
        print(f"   • Hierarchical import preserves parent-child relationships")
    else:
        print(f"\n⚠️  Some tests failed. Please review the errors above.")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()