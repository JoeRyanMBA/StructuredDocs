# Add this function at the top of backend/routes/collections.py after imports

def create_publication_node_safe(**kwargs):
    """Create PublicationNode with backwards compatibility for missing snapshot columns"""
    try:
        return PublicationNode(**kwargs)
    except Exception as e:
        if 'title_snapshot' in str(e) or 'content_snapshot' in str(e):
            print(f"🎯 PUBLISH: Snapshot columns not available, creating without snapshots: {e}")
            # Remove snapshot fields and create basic node
            safe_kwargs = {k: v for k, v in kwargs.items() 
                          if k not in ['title_snapshot', 'content_snapshot']}
            return PublicationNode(**safe_kwargs)
        else:
            raise  # Re-raise if it's a different error