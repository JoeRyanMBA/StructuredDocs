from flask import Blueprint, request, jsonify, current_app, make_response
from werkzeug.utils import secure_filename
from backend.models import db, ImportDocument, ImportItem, Topic
import re

imports = Blueprint('imports', __name__, url_prefix='/api/import')
SOURCES = ('word', 'markdown')


def _parse_and_store(file, imp_doc, source):
    """Extract heading‐1s and content blocks into ImportItem rows."""
    file.stream.seek(0)

    if source == 'word':
        # For Word documents, we'll skip this for now
        return
    else:
        raw = file.read().decode('utf-8')
        
        # Promote headers: convert H2, H3, etc. to H1
        lines = []
        for line in raw.splitlines():
            if line.strip().startswith('#'):
                # Count the number of # characters
                hash_count = len(line) - len(line.lstrip('#'))
                if hash_count > 1:
                    # Promote to H1: replace multiple # with single #
                    content = line.lstrip('#').strip()
                    line = f"# {content}"
                    print(f"PROMOTED: '{line.strip()}' (was H{hash_count})")
            lines.append(line)
        
        paras = [('md', line) for line in lines]

    items, buffer, order, current_title = [], [], 0, None
    print(f"PARSING: source={source}, lines={len(paras)}")

    def commit_buffer():
        nonlocal order, current_title, buffer
        if current_title:
            content = '\n'.join(buffer).strip()
            items.append((order, current_title, content))
            print(f"COMMITTED: order={order}, title='{current_title}', content_len={len(content)}")
            order += 1
            buffer = []

    for style, text in paras:
        is_h1 = (
            source == 'word' and style.startswith('Heading 1')
        ) or (
            source == 'markdown' and text.strip().startswith('#') and not text.strip().startswith('##')
        )
        print(f"LINE: '{text}' -> H1={is_h1}")
        if is_h1:
            commit_buffer()
            current_title = (
                text.strip() if source == 'word'
                else text.strip().lstrip('#').strip()
            )
            print(f"NEW_TITLE: '{current_title}'")
        else:
            buffer.append(text)

    commit_buffer()
    print(f"FINAL: {len(items)} items created")

    for order, title, content in items:
        db.session.add(ImportItem(
            document_id=imp_doc.id,
            heading_order=order,
            title=title,
            content=content
        ))


def _upload_file(source):
    print(f"UPLOAD: Starting upload with source={source}")
    file = request.files.get('file')
    if not file or source not in SOURCES:
        print(f"UPLOAD: Missing file or invalid source. file={file}, source={source}")
        return jsonify({'error': 'Missing file or invalid source'}), 400

    try:
        imp_doc = ImportDocument(
            filename=secure_filename(file.filename),
            source_type=source
        )
        db.session.add(imp_doc)
        db.session.flush()  # get imp_doc.id
        print(f"UPLOAD: Created ImportDocument with ID={imp_doc.id}")

        _parse_and_store(file, imp_doc, source)
        db.session.commit()
        print(f"UPLOAD: Committed to database")
        return jsonify(imp_doc.to_dict(include_items=True)), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Upload failed")
        print(f"UPLOAD: Exception occurred: {e}")
        return jsonify({'error': str(e)}), 500


@imports.route('/upload', methods=['POST'])
def upload_generic():
    return _upload_file(request.form.get('source', '').lower())


@imports.route('/markdown', methods=['POST'])
def upload_markdown():
    return _upload_file('markdown')


@imports.route('/history', methods=['GET'])
def get_import_history():
    """Get list of all import documents with their status"""
    try:
        current_app.logger.info("Fetching import history...")
        docs = ImportDocument.query.order_by(ImportDocument.created_at.desc()).all()
        current_app.logger.info(f"Found {len(docs)} import documents")
        
        result = []
        for i, doc in enumerate(docs):
            try:
                current_app.logger.info(f"Processing doc {i+1}: ID={doc.id}, filename={doc.filename}")
                doc_dict = doc.to_dict(include_items=False)
                result.append(doc_dict)
                current_app.logger.info(f"Successfully processed doc {doc.id}")
            except Exception as e:
                current_app.logger.error(f"Error processing doc {doc.id}: {str(e)}")
                # Continue with other documents instead of failing completely
                continue
                
        current_app.logger.info(f"Returning {len(result)} documents")
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching import history: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': f'Failed to fetch import history: {str(e)}'}), 500


@imports.route('/staging/<int:doc_id>', methods=['GET'])
def get_staging(doc_id):
    doc = ImportDocument.query.get_or_404(doc_id)
    return jsonify(doc.to_dict(include_items=True)), 200


@imports.route('/staging/<int:doc_id>/sme_approve', methods=['POST'])
def sme_approve(doc_id):
    """Approve an import document by SME"""
    try:
        doc = ImportDocument.query.get_or_404(doc_id)
        doc.status = 'approved'  # Changed from 'sme_approved' to 'approved'
        db.session.commit()
        current_app.logger.info(f"Import document {doc_id} approved by SME")
        return jsonify({'message': 'Import approved successfully'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error approving import {doc_id}: {str(e)}")
        return jsonify({'error': 'Failed to approve import'}), 500


@imports.route('/staging/<int:doc_id>/commit', methods=['POST'])
def commit_import(doc_id):
    """Commit an approved import to create actual topics"""
    try:
        doc = ImportDocument.query.get_or_404(doc_id)
        if doc.status != 'approved':  # Changed from 'sme_approved' to 'approved'
            return jsonify({'error': 'Import must be approved before commit'}), 400
        
        # Create topics from import items
        for item in doc.items:
            topic = Topic(
                title=item.title,
                content=item.content,
                heading_order=item.heading_order
            )
            db.session.add(topic)
        
        # Note: Keep status as 'approved' since 'committed' is not in the enum
        db.session.commit()
        current_app.logger.info(f"Import document {doc_id} committed successfully")
        return jsonify({'message': 'Import committed successfully'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error committing import {doc_id}: {str(e)}")
        return jsonify({'error': 'Failed to commit import'}), 500


@imports.route('/staging/<int:doc_id>/reject', methods=['POST'])
def reject_import(doc_id):
    """Reject an import document"""
    try:
        doc = ImportDocument.query.get_or_404(doc_id)
        doc.status = 'rejected'
        db.session.commit()
        current_app.logger.info(f"Import document {doc_id} rejected")
        return jsonify({'message': 'Import rejected successfully'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error rejecting import {doc_id}: {str(e)}")
        return jsonify({'error': 'Failed to reject import'}), 500
