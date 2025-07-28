from flask import Blueprint, request, jsonify
from datetime import datetime
from models import db, Topic, Collection, ImportDocument
from sqlalchemy import or_

reviews_bp = Blueprint('reviews', __name__, url_prefix='/api/reviews')

@reviews_bp.route('/reviewers', methods=['GET'])
def get_available_reviewers():
    """Get list of available reviewers"""
    try:
        # For now, return a hardcoded list since we don't have User model yet
        reviewers = [
            {'id': 1, 'name': 'Dr. Sarah Johnson', 'email': 'sarah.johnson@census.gov'},
            {'id': 2, 'name': 'Prof. Michael Chen', 'email': 'michael.chen@census.gov'},
            {'id': 3, 'name': 'Dr. Emily Rodriguez', 'email': 'emily.rodriguez@census.gov'},
            {'id': 4, 'name': 'James Thompson', 'email': 'james.thompson@census.gov'}
        ]
        return jsonify(reviewers)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reviews_bp.route('/topics/pending', methods=['GET'])
def get_pending_topic_reviews():
    """Get topics that need review"""
    try:
        # Get topics that are drafts or need review
        topics = Topic.query.filter(
            or_(
                Topic.status == 'draft',
                Topic.status == 'pending_review'
            )
        ).order_by(Topic.updated_at.desc()).all()
        
        result = []
        for topic in topics:
            topic_dict = topic.to_dict()
            # Add review metadata
            topic_dict['needs_review'] = True
            topic_dict['review_type'] = 'topic'
            result.append(topic_dict)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reviews_bp.route('/collections/pending', methods=['GET'])
def get_pending_collection_reviews():
    """Get collections that need review"""
    try:
        # Get collections that might need review (you may need to add review status to Collection model)
        collections = Collection.query.order_by(Collection.created_at.desc()).all()
        
        result = []
        for collection in collections:
            collection_dict = collection.to_dict()
            # Add review metadata
            collection_dict['needs_review'] = True
            collection_dict['review_type'] = 'collection'
            result.append(collection_dict)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reviews_bp.route('/imports/pending', methods=['GET'])
def get_pending_import_reviews():
    """Get import documents that need review"""
    try:
        # Get imports in review workflow
        imports = ImportDocument.query.filter(
            ImportDocument.review_step.in_(['pending', 'sme_approved'])
        ).order_by(ImportDocument.created_at.desc()).all()
        
        result = []
        for imp in imports:
            import_dict = imp.to_dict(include_items=True)
            import_dict['review_type'] = 'import'
            result.append(import_dict)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reviews_bp.route('/topic/<int:topic_id>/submit', methods=['POST'])
def submit_topic_for_review(topic_id):
    """Submit a topic for review"""
    try:
        topic = Topic.query.get_or_404(topic_id)
        data = request.get_json() or {}
        
        # Update topic status
        topic.status = 'pending_review'
        topic.updated_at = datetime.utcnow()
        
        # Store review metadata in content for now (until we have proper schema)
        review_info = {
            'notes': data.get('notes', ''),
            'assigned_reviewer_id': data.get('assigned_reviewer_id'),
            'assigned_reviewer_name': data.get('assigned_reviewer_name', ''),
            'due_date': data.get('due_date'),
            'submitted_at': datetime.utcnow().isoformat()
        }
        
        # For now, we'll store this as a comment in the topic content
        # TODO: Move to proper review fields when database is updated
        if hasattr(topic, 'review_notes'):
            topic.review_notes = str(review_info)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Topic submitted for review',
            'topic': topic.to_dict(),
            'review_info': review_info
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@reviews_bp.route('/topic/<int:topic_id>/approve', methods=['POST'])
def approve_topic(topic_id):
    """Approve a topic review"""
    try:
        topic = Topic.query.get_or_404(topic_id)
        data = request.get_json() or {}
        
        reviewer_name = data.get('reviewer', 'Unknown')
        comments = data.get('comments', '')
        
        # Update topic status
        topic.status = 'published'
        topic.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Topic approved',
            'topic': topic.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@reviews_bp.route('/topic/<int:topic_id>/reject', methods=['POST'])
def reject_topic(topic_id):
    """Reject a topic review"""
    try:
        topic = Topic.query.get_or_404(topic_id)
        data = request.get_json() or {}
        
        reviewer_name = data.get('reviewer', 'Unknown')
        comments = data.get('comments', '')
        feedback = data.get('feedback', '')
        
        # Update topic status back to draft with feedback
        topic.status = 'draft'
        topic.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Topic rejected - returned to draft',
            'topic': topic.to_dict(),
            'feedback': feedback
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@reviews_bp.route('/import/<int:import_id>/review', methods=['POST'])
def review_import(import_id):
    """Review an import document"""
    try:
        import_doc = ImportDocument.query.get_or_404(import_id)
        data = request.get_json() or {}
        
        action = data.get('action')  # 'sme_approve', 'final_approve', 'reject'
        reviewer = data.get('reviewer', 'Unknown')
        comments = data.get('comments', '')
        
        if action == 'sme_approve':
            import_doc.review_step = 'sme_approved'
        elif action == 'final_approve':
            import_doc.review_step = 'final_approved'
            import_doc.status = 'approved'
        elif action == 'reject':
            import_doc.status = 'rejected'
            import_doc.review_step = 'pending'
        
        import_doc.reviewed_at = datetime.utcnow()
        import_doc.reviewer = reviewer
        
        db.session.commit()
        
        return jsonify({
            'message': f'Import {action}d successfully',
            'import': import_doc.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@reviews_bp.route('/history', methods=['GET'])
def get_review_history():
    """Get review history across all content types"""
    try:
        # Get recent reviews from different sources
        history = []
        
        # Recent topic reviews
        reviewed_topics = Topic.query.filter(
            Topic.status.in_(['published', 'rejected'])
        ).order_by(Topic.updated_at.desc()).limit(20).all()
        
        for topic in reviewed_topics:
            history.append({
                'id': topic.id,
                'type': 'topic',
                'title': topic.title,
                'status': topic.status,
                'reviewed_at': topic.updated_at.isoformat(),
                'reviewer': 'System'  # You might want to add a reviewer field to Topic model
            })
        
        # Recent import reviews
        reviewed_imports = ImportDocument.query.filter(
            ImportDocument.reviewed_at.isnot(None)
        ).order_by(ImportDocument.reviewed_at.desc()).limit(20).all()
        
        for imp in reviewed_imports:
            history.append({
                'id': imp.id,
                'type': 'import',
                'title': imp.filename,
                'status': imp.status,
                'review_step': imp.review_step,
                'reviewed_at': imp.reviewed_at.isoformat(),
                'reviewer': imp.reviewer
            })
        
        # Sort by review date
        history.sort(key=lambda x: x['reviewed_at'], reverse=True)
        
        return jsonify(history[:50])  # Return last 50 reviews
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reviews_bp.route('/stats', methods=['GET'])
def get_review_stats():
    """Get review statistics"""
    try:
        stats = {
            'topics': {
                'pending_review': Topic.query.filter_by(status='pending_review').count(),
                'draft': Topic.query.filter_by(status='draft').count(),
                'published': Topic.query.filter_by(status='published').count()
            },
            'imports': {
                'pending': ImportDocument.query.filter_by(review_step='pending').count(),
                'sme_approved': ImportDocument.query.filter_by(review_step='sme_approved').count(),
                'final_approved': ImportDocument.query.filter_by(review_step='final_approved').count(),
                'rejected': ImportDocument.query.filter_by(status='rejected').count()
            }
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
