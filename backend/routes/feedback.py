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
        reports = FeedbackReport.query.order_by(FeedbackReport.created_at.desc()).limit(200).all()
        return jsonify([r.to_dict() for r in reports])
    except Exception as e:
        return jsonify({'error': str(e)}), 500
