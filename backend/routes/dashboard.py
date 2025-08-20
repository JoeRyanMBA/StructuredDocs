from flask import Blueprint, jsonify

bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

@bp.route('/stats', methods=['GET'])
def get_stats():
    # Dummy data, replace with real queries as needed
    return jsonify({
        'projects': {'total': 10, 'active': 5},
        'collections': {'total': 20, 'new_today': 2},
        'topics': {'total': 15, 'drafts': 3},
        'reviews': {'total': 8, 'pending': 1}
    })

@bp.route('/pending-actions', methods=['GET'])
def get_pending_actions():
    # Dummy data, replace with real queries as needed
    return jsonify([
        {'id': 1, 'type': 'review', 'description': 'Review project X', 'link': '/projects/1/review'},
        {'id': 2, 'type': 'approval', 'description': 'Approve collection Y', 'link': '/collections/2/approve'}
    ])
