from flask import Blueprint, request, jsonify
from ..models import db, FeedbackReport
import json

feedback_bp = Blueprint('feedback', __name__, url_prefix='/api/feedback')


@feedback_bp.route('', methods=['POST'])
def submit_feedback():
    try:
        data = request.get_json() or {}
        report_type = data.get('type', 'other')
        page = data.get('page')
        component = data.get('component')
        user_contact = data.get('contact')
        message = data.get('message')
        metadata = data.get('metadata')

        if not message or not message.strip():
            return jsonify({'error': 'Message is required'}), 400

        # Normalize metadata to string JSON if provided
        metadata_json = None
        if metadata is not None:
            try:
                if isinstance(metadata, str):
                    # If it's valid JSON string keep as-is, else wrap as a string
                    json.loads(metadata)
                    metadata_json = metadata
                else:
                    metadata_json = json.dumps(metadata)
            except Exception:
                # Fallback to string representation
                metadata_json = str(metadata)

        fr = FeedbackReport(
            report_type=report_type,
            page=page,
            component=component,
            user_contact=user_contact,
            message=message,
            metadata_json=metadata_json
        )
        db.session.add(fr)
        db.session.commit()

        return jsonify({'success': True, 'report': fr.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@feedback_bp.route('', methods=['GET'])
def list_feedback():
    try:
        # Query params for filtering / sorting
        q = FeedbackReport.query
        report_type = request.args.get('type')
        status = request.args.get('status')
        component = request.args.get('component')
        search = request.args.get('q')
        sort = request.args.get('sort', 'created_at')
        order = request.args.get('order', 'desc').lower()
        limit = min(int(request.args.get('limit', 200)), 1000)

        if report_type:
            q = q.filter(FeedbackReport.report_type == report_type)
        if status:
            q = q.filter(FeedbackReport.status == status)
        if component:
            q = q.filter(FeedbackReport.component == component)
        if search:
            like = f"%{search}%"
            q = q.filter(FeedbackReport.message.ilike(like))

        # Sorting
        if sort not in ('created_at', 'report_type', 'status'):
            sort = 'created_at'
        sort_col = getattr(FeedbackReport, sort)
        if order == 'asc':
            q = q.order_by(sort_col.asc())
        else:
            q = q.order_by(sort_col.desc())

        reports = q.limit(limit).all()
        return jsonify([r.to_dict() for r in reports])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@feedback_bp.route('/<int:report_id>', methods=['GET'])
def get_feedback(report_id):
    try:
        r = FeedbackReport.query.get_or_404(report_id)
        return jsonify(r.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@feedback_bp.route('/<int:report_id>', methods=['PATCH'])
def update_feedback(report_id):
    try:
        data = request.get_json() or {}
        r = FeedbackReport.query.get_or_404(report_id)

        # Allow updating a small set of fields
        if 'report_type' in data:
            r.report_type = data.get('report_type')
        if 'page' in data:
            r.page = data.get('page')
        if 'component' in data:
            r.component = data.get('component')
        if 'user_contact' in data:
            r.user_contact = data.get('user_contact')
        if 'message' in data:
            r.message = data.get('message')
        if 'status' in data:
            r.status = data.get('status')
        if 'metadata' in data:
            # Accept dict or JSON string
            m = data.get('metadata')
            try:
                if isinstance(m, str):
                    # Validate JSON
                    json.loads(m)
                    r.metadata_json = m
                else:
                    r.metadata_json = json.dumps(m)
            except Exception:
                r.metadata_json = str(m)

        db.session.commit()
        return jsonify(r.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@feedback_bp.route('/<int:report_id>', methods=['DELETE'])
def delete_feedback(report_id):
    try:
        r = FeedbackReport.query.get_or_404(report_id)
        # Soft-delete: mark archived via status
        r.status = 'archived'
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# Backwards-compatible POST endpoints for hosts that block PATCH/DELETE
@feedback_bp.route('/<int:report_id>/update', methods=['POST'])
def post_update_feedback(report_id):
    try:
        data = request.get_json() or {}
        r = FeedbackReport.query.get_or_404(report_id)
        # reuse update logic
        if 'report_type' in data:
            r.report_type = data.get('report_type')
        if 'page' in data:
            r.page = data.get('page')
        if 'component' in data:
            r.component = data.get('component')
        if 'user_contact' in data:
            r.user_contact = data.get('user_contact')
        if 'message' in data:
            r.message = data.get('message')
        if 'status' in data:
            r.status = data.get('status')
        if 'metadata' in data:
            m = data.get('metadata')
            try:
                if isinstance(m, str):
                    json.loads(m)
                    r.metadata_json = m
                else:
                    r.metadata_json = json.dumps(m)
            except Exception:
                r.metadata_json = str(m)

        db.session.commit()
        return jsonify(r.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@feedback_bp.route('/<int:report_id>/archive', methods=['POST'])
def post_archive_feedback(report_id):
    try:
        r = FeedbackReport.query.get_or_404(report_id)
        r.status = 'archived'
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
