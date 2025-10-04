#!/usr/bin/env python3
"""
Debug script to investigate publication export and hierarchical import issues.
"""

import sys
import os
sys.path.insert(0, '/workspaces/StructuredDocs')
sys.path.insert(0, '/workspaces/StructuredDocs/backend')

def check_publication_export_issue():
    """Check the publication export issue"""
    
    print("🔍 Investigating Publication Export Issue")
    print("=" * 50)
    
    try:
        from backend.app import create_app
        from backend.models import db, Publication, PublicationNode, Topic
        
        app = create_app()
        with app.app_context():
            # Check if we have any publications
            publications = Publication.query.all()
            print(f"📊 Found {len(publications)} publications")
            
            if not publications:
                print("⚠️  No publications found. Creating a test publication...")
                
                # Check if we have topics
                topics = Topic.query.all()
                print(f"📊 Found {len(topics)} topics")
                
                if not topics:
                    print("⚠️  No topics found. Need to create test data.")
                    return False
                
                # Create a test publication
                pub = Publication(
                    title="Test Publication",
                    description="Test publication for debugging export issue"
                )
                db.session.add(pub)
                db.session.flush()
                
                # Add first topic as a node
                node = PublicationNode(
                    publication_id=pub.id,
                    topic_id=topics[0].id,
                    position=0,
                    title_snapshot=topics[0].title,
                    content_snapshot=topics[0].content
                )
                db.session.add(node)
                db.session.commit()
                
                print(f"✅ Created test publication with ID: {pub.id}")
                pub_id = pub.id
            else:
                pub = publications[0]
                pub_id = pub.id
                print(f"📋 Using existing publication: {pub.title} (ID: {pub_id})")
            
            # Check publication nodes
            nodes = PublicationNode.query.filter_by(publication_id=pub_id).all()
            print(f"📊 Publication has {len(nodes)} nodes")
            
            for i, node in enumerate(nodes):
                print(f"   Node {i+1}: Topic ID {node.topic_id}, Position {node.position}")
                print(f"   Title Snapshot: {node.title_snapshot}")
                print(f"   Content Length: {len(node.content_snapshot or '')}")
            
            # Test the serialization logic from the export function
            def serialize_node(node):
                try:
                    topic_data = node.topic.to_dict() if node.topic else {'title': 'Unknown', 'content': ''}
                    return {
                        'id': node.id,
                        'topic_id': node.topic_id,
                        'title': topic_data.get('title', 'Untitled'),
                        'content': topic_data.get('content', ''),
                        'position': node.position,
                        'children': sorted([serialize_node(c) for c in node.children],
                                         key=lambda x: x['position'])
                    }
                except Exception as e:
                    print(f"❌ Error serializing node {node.id}: {e}")
                    return None
            
            print("\n🔍 Testing node serialization...")
            for node in nodes:
                result = serialize_node(node)
                if result:
                    print(f"✅ Node {node.id} serialized successfully")
                else:
                    print(f"❌ Node {node.id} serialization failed")
            
            return True
            
    except Exception as e:
        print(f"❌ Error investigating publication export: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_hierarchical_import_issue():
    """Check the hierarchical import nesting issue"""
    
    print("\n🔍 Investigating Hierarchical Import Nesting")
    print("=" * 50)
    
    try:
        from backend.app import create_app
        from backend.models import db, Collection, Topic, collection_topic_tree
        
        app = create_app()
        with app.app_context():
            # Find collections created from hierarchical imports
            collections = Collection.query.all()
            print(f"📊 Found {len(collections)} collections")
            
            for collection in collections:
                if "Document Import" in collection.name or "AUTO_" in collection.form_number:
                    print(f"\n📋 Checking hierarchical collection: {collection.name}")
                    
                    # Check collection-topic relationships
                    relationships = db.session.execute(
                        collection_topic_tree.select().where(
                            collection_topic_tree.c.collection_id == collection.id
                        )
                    ).fetchall()
                    
                    print(f"   Found {len(relationships)} topic relationships")
                    
                    # Group by parent to show hierarchy
                    hierarchy = {}
                    for rel in relationships:
                        parent_id = rel.parent_topic_id
                        if parent_id not in hierarchy:
                            hierarchy[parent_id] = []
                        hierarchy[parent_id].append(rel)
                    
                    # Show root topics (parent_topic_id is None)
                    root_topics = hierarchy.get(None, [])
                    print(f"   Root topics: {len(root_topics)}")
                    
                    for rel in root_topics:
                        topic = Topic.query.get(rel.topic_id)
                        print(f"   • {topic.title} (Position: {rel.position})")
                        
                        # Show children
                        children = hierarchy.get(rel.topic_id, [])
                        for child_rel in children:
                            child_topic = Topic.query.get(child_rel.topic_id)
                            print(f"     ├─ {child_topic.title} (Position: {child_rel.position})")
                            
                            # Show grandchildren
                            grandchildren = hierarchy.get(child_rel.topic_id, [])
                            for grandchild_rel in grandchildren:
                                grandchild_topic = Topic.query.get(grandchild_rel.topic_id)
                                print(f"       └─ {grandchild_topic.title} (Position: {grandchild_rel.position})")
                    
                    if len(root_topics) == len(relationships):
                        print("   ⚠️  All topics are at root level - hierarchy may not be preserved!")
                    else:
                        print("   ✅ Hierarchy appears to be preserved")
            
            return True
            
    except Exception as e:
        print(f"❌ Error investigating hierarchical import: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔧 StructuredDocs Issue Debugging")
    print("=" * 60)
    
    # Check both issues
    export_ok = check_publication_export_issue()
    hierarchy_ok = check_hierarchical_import_issue()
    
    print(f"\n📊 Summary:")
    print(f"   Publication Export: {'✅ OK' if export_ok else '❌ Issues Found'}")
    print(f"   Hierarchical Import: {'✅ OK' if hierarchy_ok else '❌ Issues Found'}")
    
    if not export_ok or not hierarchy_ok:
        print(f"\n🛠️  Issues detected. Recommendations:")
        if not export_ok:
            print("   • Check publication node relationships and topic loading")
        if not hierarchy_ok:
            print("   • Check parent_topic_id assignment in hierarchical import")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()