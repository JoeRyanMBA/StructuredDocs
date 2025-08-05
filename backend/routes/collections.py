from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
from models import db, Collection, collection_topic_tree, Publication, PublicationNode

collections_bp = Blueprint('collections', __name__, url_prefix='/api/collections')

@collections_bp.route('', methods=['GET'])
@collections_bp.route('/', methods=['GET'])
def list_collections():
    print(f"🔄 Collections GET request received")
    try:
        roots = Collection.query.filter_by(parent_id=None)\
                  .order_by(Collection.position).all()
        tree = [c.to_dict() for c in roots]
        print(f"✅ Returning {len(tree)} collections")
        return jsonify(tree), 200
    except Exception as e:
        print(f"❌ Error in list_collections: {e}")
        return jsonify({"error": str(e)}), 500

@collections_bp.route('/stats', methods=['GET'])
def get_collections_stats():
    """Get statistics for collections dashboard"""
    try:
        # Get all collections (including children)
        all_collections = Collection.query.all()
        root_collections = Collection.query.filter_by(parent_id=None).all()
        
        total_collections = len(all_collections)
        # Since Collection doesn't have status field, assume all are active
        active_collections = total_collections
        
        # Calculate total topics across all collections
        total_topics = sum(len(c.topics) for c in all_collections)
        
        # Since Collection doesn't have created_at, set new this week to 0
        new_this_week = 0
        
        # Calculate average topics per collection
        avg_topics = round(total_topics / total_collections) if total_collections > 0 else 0
        
        stats = {
            'total': total_collections,
            'active': active_collections,
            'totalTopics': total_topics,
            'newThisWeek': new_this_week,
            'avgTopics': avg_topics,
            'rootCollections': len(root_collections),
            'debug': {
                'all_collections_count': len(all_collections),
                'root_collections_count': len(root_collections),
                'topics_per_collection': [(c.name, len(c.topics)) for c in all_collections]
            }
        }
        
        print(f"📊 Collections stats: {stats}")
        return jsonify(stats), 200
        
    except Exception as e:
        print(f"❌ Error calculating collections stats: {e}")
        return jsonify({"error": str(e)}), 500

@collections_bp.route('', methods=['PUT'])
@collections_bp.route('/', methods=['PUT'])
def update_collections():
    """
    Expect payload: an array of nested nodes:
    [
      { id, parentId, position, children:[ ... ], topics: [...] },
      …
    ]
    """
    payload = request.get_json()
    print(f"🔄 Updating collections with payload: {payload}")

    def walk(nodes):
      for node in nodes:
        col = Collection.query.get(node['id'])
        if not col:
            print(f"⚠️ Collection {node['id']} not found, skipping")
            continue
        
        # Update collection properties
        col.parent_id = node.get('parentId')
        col.position  = node.get('position', 0)
        
        # Handle topics assignment
        if 'topics' in node:
            print(f"📋 Updating topics for collection {col.id}: {node['topics']}")
            
            # Clear existing relationships for this collection
            db.session.execute(
                collection_topic_tree.delete().where(
                    collection_topic_tree.c.collection_id == col.id
                )
            )
            
            # Add new relationships with hierarchical support
            def add_topics_recursively(topics, parent_topic_id=None):
                for idx, t in enumerate(topics):
                    print(f"➕ Adding topic {t['id']} to collection {col.id} at position {idx}, parent: {parent_topic_id}")
                    db.session.execute(
                        collection_topic_tree.insert().values(
                            collection_id=col.id,
                            topic_id=t['id'],
                            position=idx,
                            parent_topic_id=parent_topic_id
                        )
                    )
                    # Recursively add child topics
                    if 'children' in t and t['children']:
                        add_topics_recursively(t['children'], t['id'])
            
            add_topics_recursively(node['topics'])
        
        # Recurse into children
        if node.get('children'):
          walk(node['children'])

    try:
        walk(payload)
        db.session.commit()
        print("✅ Collections updated successfully")
        return jsonify({'message': 'collection tree updated'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error updating collections: {e}")
        return jsonify({'error': str(e)}), 500

@collections_bp.route('', methods=['POST'])
def create_collection():
    """
    Create a new collection.
    Expects JSON payload: { "name": str, "parentId": int (optional), "position": int (optional) }
    """
    data = request.get_json()
    name = data.get('name')
    parent_id = data.get('parentId')
    position = data.get('position', 0)

    if not name:
        return jsonify({'error': 'Collection name is required'}), 400

    new_collection = Collection(name=name, parent_id=parent_id, position=position)
    db.session.add(new_collection)
    db.session.commit()
    return jsonify(new_collection.to_dict()), 201

@collections_bp.route('/<int:collection_id>/publish', methods=['POST'])
def publish_collection(collection_id):
    """
    Convert a collection to a publication for publishing.
    This creates a Publication and PublicationNode structure from the Collection.
    """
    try:
        collection = Collection.query.get_or_404(collection_id)
        
        # Check if publication already exists for this collection
        # Use a more specific approach by checking for publications with the exact title
        title_pattern = collection.name
        existing_pub = Publication.query.filter_by(title=title_pattern).first()
        
        if existing_pub:
            # Update the description to reflect current topic count
            existing_pub.description = f"Published from Collection '{collection.name}' containing {len(collection.topics)} topics"
            
            # Update the created_at timestamp to reflect the latest publication time
            existing_pub.created_at = datetime.now(timezone.utc)
            
            # Clear existing publication nodes and recreate them
            PublicationNode.query.filter_by(publication_id=existing_pub.id).delete()
            
            # Recreate publication nodes from current collection topics
            def create_publication_nodes(coll, parent_pub_node_id=None):
                nodes_created = []
                
                # Get hierarchical topic structure instead of flat topics
                hierarchical_topics = coll.to_tree()
                
                def process_topics_recursively(topics, parent_node_id):
                    for idx, topic_data in enumerate(topics):
                        # Create publication node for this topic
                        node = PublicationNode(
                            publication_id=existing_pub.id,
                            topic_id=topic_data['id'],
                            parent_id=parent_node_id,
                            position=idx
                        )
                        db.session.add(node)
                        db.session.flush()
                        nodes_created.append(node)
                        
                        # Recursively process child topics
                        if topic_data.get('children'):
                            process_topics_recursively(topic_data['children'], node.id)
                
                process_topics_recursively(hierarchical_topics, parent_pub_node_id)
                
                # Recursively handle child collections
                for child_coll in sorted(coll.children, key=lambda x: x.position):
                    child_nodes = create_publication_nodes(child_coll, parent_pub_node_id)
                    nodes_created.extend(child_nodes)
                
                return nodes_created
            
            nodes = create_publication_nodes(collection)
            db.session.commit()
            
            response_data = {
                'message': 'Publication updated with current collection content',
                'publication_id': existing_pub.id,
                'nodes_created': len(nodes),
                'redirect_url': f'/publications/{existing_pub.id}'
            }
            print(f"🔄 Updated existing publication {existing_pub.id} for collection {collection.id}")
            print(f"📝 Updated description to reflect {len(collection.topics)} topics")
            print(f"🔧 Recreated {len(nodes)} publication nodes")
            print(f"📤 Returning response: {response_data}")
            return jsonify(response_data), 200
        
        # Create a new publication from the collection
        publication = Publication(
            title=f"{collection.name}",
            description=f"Published from Collection '{collection.name}' containing {len(collection.topics)} topics"
        )
        db.session.add(publication)
        db.session.flush()  # Get the publication ID
        
        # Convert collection topics to publication nodes
        def create_publication_nodes(coll, parent_pub_node_id=None):
            nodes_created = []
            
            # Get hierarchical topic structure instead of flat topics
            hierarchical_topics = coll.to_tree()
            
            def process_topics_recursively(topics, parent_node_id):
                for idx, topic_data in enumerate(topics):
                    # Create publication node for this topic
                    node = PublicationNode(
                        publication_id=publication.id,
                        topic_id=topic_data['id'],
                        parent_id=parent_node_id,
                        position=idx
                    )
                    db.session.add(node)
                    db.session.flush()
                    nodes_created.append(node)
                    
                    # Recursively process child topics
                    if topic_data.get('children'):
                        process_topics_recursively(topic_data['children'], node.id)
            
            process_topics_recursively(hierarchical_topics, parent_pub_node_id)
            
            # Recursively handle child collections
            for child_coll in sorted(coll.children, key=lambda x: x.position):
                child_nodes = create_publication_nodes(child_coll, parent_pub_node_id)
                nodes_created.extend(child_nodes)
            
            return nodes_created
        
        nodes = create_publication_nodes(collection)
        
        db.session.commit()
        
        print(f"✅ Created publication {publication.id} from collection {collection.id} with {len(nodes)} nodes")
        
        return jsonify({
            'message': 'Collection published successfully',
            'publication_id': publication.id,
            'nodes_created': len(nodes),
            'redirect_url': f'/publications/{publication.id}'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error publishing collection {collection_id}: {e}")
        return jsonify({'error': str(e)}), 500