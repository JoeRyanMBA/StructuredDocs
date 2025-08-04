from flask import Blueprint, request, jsonify, current_app, make_response
from werkzeug.utils import secure_filename
from models import db, ImportDocument, ImportItem, ImportImage, Topic
from utils.image_handler import ImageHandler
import re
from docx import Document
import io
import subprocess
import tempfile
import os
import uuid

imports = Blueprint('imports', __name__, url_prefix='/api/import')
SOURCES = ('word', 'markdown')


def _convert_word_to_markdown(file_content, import_doc_id):
    """Convert Word document to Markdown using pandoc with proper image handling"""
    try:
        # Create unique temporary directory for this import
        temp_base_dir = tempfile.mkdtemp(prefix=f'import_{import_doc_id}_')
        temp_media_dir = os.path.join(temp_base_dir, 'media')
        
        # Create temporary files for input and output
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False, dir=temp_base_dir) as temp_input:
            temp_input.write(file_content)
            temp_input_path = temp_input.name
        
        with tempfile.NamedTemporaryFile(suffix='.md', delete=False, dir=temp_base_dir) as temp_output:
            temp_output_path = temp_output.name
        
        try:
            # Use pandoc to convert Word to Markdown with better list handling
            cmd = [
                'pandoc',
                '--from', 'docx',
                '--to', 'markdown',
                '--wrap', 'none',  # Don't wrap lines
                '--extract-media', temp_media_dir,  # Extract images to our temp media dir
                '--markdown-headings=atx',  # Use ATX-style headings (#)
                '--list-tables',  # Use pipe tables for better compatibility
                '--strip-comments',  # Remove HTML comments
                temp_input_path,
                '-o', temp_output_path
            ]
            
            print(f"PANDOC: Running command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                print(f"PANDOC ERROR: {result.stderr}")
                raise Exception(f"Pandoc conversion failed: {result.stderr}")
            
            # Read the converted Markdown
            with open(temp_output_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            print(f"PANDOC SUCCESS: Converted {len(file_content)} bytes to {len(markdown_content)} chars of Markdown")
            
            # Initialize image handler
            image_handler = ImageHandler(import_doc_id)
            
            # Extract and store images permanently
            updated_markdown, stored_images = image_handler.extract_and_store_images(
                temp_media_dir, markdown_content
            )
            
            # Store image metadata in database
            for image_info in stored_images:
                import_image = ImportImage(
                    document_id=import_doc_id,
                    filename=image_info['filename'],
                    original_name=image_info['original_name'],
                    public_url=image_info['public_url'],
                    backend_path=image_info['backend_path'],
                    frontend_path=image_info['frontend_path'],
                    width=image_info['width'],
                    height=image_info['height'],
                    format=image_info['format'],
                    file_size=image_info['file_size'],
                    mime_type=image_info['mime_type']
                )
                db.session.add(import_image)
            
            print(f"IMAGE PROCESSING: Stored {len(stored_images)} images")
            
            # Post-process the markdown to fix issues
            updated_markdown = _post_process_markdown(updated_markdown)
            
            # Additional cleaning for HTML comments and formatting issues
            updated_markdown = _clean_markdown_content(updated_markdown)
            
            # Validate image references
            validation_issues = image_handler.validate_markdown_images(updated_markdown)
            if validation_issues:
                for issue in validation_issues:
                    print(f"IMAGE VALIDATION: {issue['message']}")
            
            # Clean up temporary directory
            image_handler.cleanup_temp_images(temp_base_dir)
            
            return updated_markdown
            
        finally:
            # Clean up temporary files
            try:
                os.unlink(temp_input_path)
                os.unlink(temp_output_path)
            except OSError:
                pass  # Files might already be deleted
                
    except subprocess.TimeoutExpired:
        print("PANDOC ERROR: Conversion timed out")
        raise Exception("Word to Markdown conversion timed out")
    except Exception as e:
        print(f"PANDOC ERROR: {str(e)}")
        raise Exception(f"Failed to convert Word to Markdown: {str(e)}")


def _post_process_markdown(markdown_content):
    """Post-process markdown to fix nested lists and handle margin notes"""
    lines = markdown_content.split('\n')
    processed_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Handle HTML comment blocks that contain nested lists
        if line.strip() == '```{=html}' and i + 1 < len(lines):
            # Look for the closing block
            j = i + 1
            html_content = []
            while j < len(lines) and lines[j].strip() != '```':
                html_content.append(lines[j])
                j += 1
            
            if j < len(lines):  # Found closing ```
                # Process the HTML content to extract nested lists
                html_text = '\n'.join(html_content)
                converted_list = _convert_html_list_to_markdown(html_text)
                if converted_list:
                    processed_lines.extend(converted_list.split('\n'))
                else:
                    # If we can't convert, keep the original but clean it up
                    processed_lines.extend(html_content)
                i = j + 1  # Skip past the closing ```
            else:
                # No closing found, keep as is
                processed_lines.append(line)
                i += 1
        
        # Remove standalone HTML comments that appear between list items
        elif line.strip() == '<!-- -->' or line.strip() == '<!---->':
            # Skip this line entirely
            i += 1
        
        # Handle margin notes (look for specific patterns that might indicate margin notes)
        elif 'margin' in line.lower() or line.strip().startswith('> '):
            # Convert margin note style to markdown note
            content = line.strip()
            if content.startswith('> '):
                content = content[2:].strip()
            elif 'margin' in content.lower():
                # Remove any margin-related formatting
                content = re.sub(r'\*\*?margin\s*note\*\*?:?\s*', '', content, flags=re.IGNORECASE)
                content = content.strip()
            
            if content:
                processed_lines.append(f"**Important:** {content}")
            i += 1
        
        else:
            processed_lines.append(line)
            i += 1
    
    # Clean up any remaining HTML comments in the processed content
    cleaned_content = '\n'.join(processed_lines)
    cleaned_content = re.sub(r'<!--\s*-->', '', cleaned_content)
    cleaned_content = re.sub(r'<!---->', '', cleaned_content)
    
    # Remove excessive blank lines (more than 2 consecutive)
    cleaned_content = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned_content)
    
    return cleaned_content


def _convert_html_list_to_markdown(html_content):
    """Convert HTML list content to proper markdown lists"""
    # Remove HTML comments
    html_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)
    
    # Convert <ul> and <li> tags to markdown
    # This is a simple conversion - for complex nested lists you might need a proper HTML parser
    html_content = re.sub(r'<ul[^>]*>', '', html_content)
    html_content = re.sub(r'</ul>', '', html_content)
    html_content = re.sub(r'<ol[^>]*>', '', html_content)
    html_content = re.sub(r'</ol>', '', html_content)
    
    lines = html_content.split('\n')
    markdown_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Convert <li> tags to markdown list items
        if line.startswith('<li>') and line.endswith('</li>'):
            content = line[4:-5].strip()  # Remove <li> and </li>
            # Determine nesting level based on leading whitespace in original
            # For now, just use simple bullet points
            markdown_lines.append(f"- {content}")
        elif '<li>' in line:
            # Handle multi-line or partial li tags
            content = re.sub(r'</?li[^>]*>', '', line).strip()
            if content:
                markdown_lines.append(f"- {content}")
    
    return '\n'.join(markdown_lines) if markdown_lines else None


def _clean_markdown_content(content):
    """Additional cleaning for problematic patterns in converted markdown"""
    # Remove HTML comments that appear as standalone lines or inline
    content = re.sub(r'<!--\s*-->\s*\n?', '', content)
    content = re.sub(r'<!---->\s*\n?', '', content)
    
    # Fix patterns where list items are separated by HTML comments
    # Pattern: list item, HTML comment, list item -> continuous list
    lines = content.split('\n')
    cleaned_lines = []
    
    for i, line in enumerate(lines):
        # Skip HTML comment lines entirely
        if re.match(r'^\s*<!--.*?-->\s*$', line):
            continue
        
        # Skip empty paragraphs (lines with only whitespace)
        if line.strip() == '':
            # Keep one blank line but skip excessive ones
            if cleaned_lines and cleaned_lines[-1].strip() != '':
                cleaned_lines.append('')
            continue
        
        # Skip lines that are just paragraph tags or whitespace
        if re.match(r'^\s*</?p>\s*$', line):
            continue
            
        # Clean up lines that contain only HTML paragraph tags with whitespace
        line = re.sub(r'^\s*<p>\s*</p>\s*$', '', line)
        if line.strip() == '':
            continue
        
        # Remove empty markdown paragraph indicators
        if re.match(r'^\s*&nbsp;\s*$', line):
            continue
            
        # Remove lines with only whitespace characters and HTML entities
        if re.match(r'^\s*(&nbsp;|\s|&\w+;)*\s*$', line):
            continue
        
        # Keep the line
        cleaned_lines.append(line)
    
    # Join back and clean up excessive whitespace
    cleaned_content = '\n'.join(cleaned_lines)
    
    # Remove excessive blank lines (more than 2 consecutive)
    cleaned_content = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned_content)
    
    # Remove blank lines at the beginning and end
    cleaned_content = cleaned_content.strip()
    
    # Remove empty list items that might have been created
    cleaned_content = re.sub(r'^[\s]*[-*+]\s*$', '', cleaned_content, flags=re.MULTILINE)
    
    # Clean up any remaining empty paragraph patterns
    cleaned_content = re.sub(r'\n\s*<p>\s*</p>\s*\n', '\n', cleaned_content)
    cleaned_content = re.sub(r'<p>\s*</p>', '', cleaned_content)
    
    return cleaned_content


def _clean_topic_content(content):
    """Clean up topic content by removing empty paragraphs and excessive whitespace"""
    if not content or not content.strip():
        return ''
    
    lines = content.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Skip completely empty lines, but preserve intentional spacing
        if line.strip() == '':
            # Only add blank line if the previous line wasn't blank
            if cleaned_lines and cleaned_lines[-1].strip() != '':
                cleaned_lines.append('')
            continue
        
        # Remove lines that are just HTML paragraph tags
        if re.match(r'^\s*</?p>\s*$', line):
            continue
        
        # Remove lines with only non-breaking spaces or similar
        if re.match(r'^\s*(&nbsp;|\s|&\w+;)*\s*$', line):
            continue
            
        # Remove empty list items
        if re.match(r'^\s*[-*+]\s*$', line):
            continue
            
        # Remove empty numbered list items
        if re.match(r'^\s*\d+\.\s*$', line):
            continue
        
        # Remove Word document artifacts
        if re.match(r'^\s*\[\s*\]\s*$', line):  # Empty checkboxes
            continue
            
        if re.match(r'^\s*\\\s*$', line):  # Stray backslashes
            continue
            
        # Remove lines with only formatting marks or tabs
        if re.match(r'^\s*[\t\r\f\v]+\s*$', line):
            continue
            
        # Remove Word table artifacts like empty table cells
        if re.match(r'^\s*\|\s*\|\s*$', line):
            continue
        
        cleaned_lines.append(line)
    
    # Join and clean up
    cleaned_content = '\n'.join(cleaned_lines)
    
    # Remove excessive blank lines (more than 1 consecutive)
    cleaned_content = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned_content)
    
    # Clean up common Word artifacts in the content
    cleaned_content = re.sub(r'\s*\n\s*\n\s*\n+', '\n\n', cleaned_content)  # Multiple newlines
    cleaned_content = re.sub(r'(?<!\n)\n(?!\n)', ' ', cleaned_content)  # Single newlines (join wrapped lines)
    cleaned_content = re.sub(r'\n\n+', '\n\n', cleaned_content)  # Excessive double newlines
    
    # Remove leading/trailing whitespace
    cleaned_content = cleaned_content.strip()
    
    # If content is now just whitespace or empty, return empty string
    if not cleaned_content or not cleaned_content.strip():
        return ''
    
    return cleaned_content


def _parse_and_store(file, imp_doc, source):
    """Extract heading‐1s and content blocks into ImportItem rows."""
    file.stream.seek(0)

    if source == 'word':
        # Convert Word document to Markdown using pandoc
        print(f"PARSING WORD DOC: {imp_doc.filename}")
        try:
            # Read file content
            file_content = file.read()
            file.stream.seek(0)  # Reset stream for potential future reads
            
            # Convert to Markdown with image handling
            markdown_content = _convert_word_to_markdown(file_content, imp_doc.id)
            
            # Now parse as if it were a Markdown file
            lines = []
            for line in markdown_content.splitlines():
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
            
        except Exception as e:
            print(f"ERROR converting Word document: {e}")
            current_app.logger.error(f"Failed to convert Word document {imp_doc.filename}: {e}")
            return
    else:
        # Markdown file processing with image validation
        raw = file.read().decode('utf-8')
        
        # For markdown files, validate existing image references
        if imp_doc.id:  # Only if document is already saved
            image_handler = ImageHandler(imp_doc.id)
            validation_issues = image_handler.validate_markdown_images(raw)
            if validation_issues:
                for issue in validation_issues:
                    print(f"MARKDOWN IMAGE VALIDATION: {issue['message']}")
        
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
    print(f"PARSING: source={source}, paragraphs={len(paras)}")

    def commit_buffer():
        nonlocal order, current_title, buffer
        if current_title:
            content = '\n'.join(buffer).strip()
            
            # Apply additional content cleaning
            content = _clean_topic_content(content)
            
            # Only create an item if we have actual content (not just empty lines/whitespace)
            if content:
                items.append((order, current_title, content))
                print(f"COMMITTED: order={order}, title='{current_title}', content_len={len(content)}")
                order += 1
            else:
                print(f"SKIPPED EMPTY: title='{current_title}' (no substantive content)")
            buffer = []

    for style, text in paras:
        is_h1 = text.strip().startswith('#') and not text.strip().startswith('##')
        print(f"LINE: '{text}' -> H1={is_h1}")
        
        if is_h1:
            # Check if we have a current title but no substantive content yet
            current_buffer_content = '\n'.join(buffer).strip()
            if current_title and not current_buffer_content:
                # Merge this heading into the content of the previous heading
                heading_text = text.strip().lstrip('#').strip()
                buffer.append(f"## {heading_text}")  # Add as H2 in content
                print(f"MERGED_HEADING: '{heading_text}' added to content of '{current_title}'")
            else:
                # Normal case: commit previous section and start new one
                commit_buffer()
                current_title = text.strip().lstrip('#').strip()
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


@imports.route('/staging/<int:doc_id>/images', methods=['GET'])
def get_import_images(doc_id):
    """Get all images associated with an import document"""
    try:
        doc = ImportDocument.query.get_or_404(doc_id)
        
        # Get images from database
        db_images = ImportImage.query.filter_by(document_id=doc_id).all()
        images_data = [img.to_dict() for img in db_images]
        
        # Also get images from filesystem (in case of sync issues)
        image_handler = ImageHandler(doc_id)
        fs_images = image_handler.get_import_images()
        
        # Merge the data (database is authoritative, filesystem for verification)
        return jsonify({
            'document_id': doc_id,
            'document_filename': doc.filename,
            'images': images_data,
            'filesystem_images': fs_images,
            'total_count': len(images_data)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching images for import {doc_id}: {str(e)}")
        return jsonify({'error': f'Failed to fetch images: {str(e)}'}), 500


@imports.route('/staging/<int:doc_id>', methods=['GET'])
def get_staging(doc_id):
    doc = ImportDocument.query.get_or_404(doc_id)
    result = doc.to_dict(include_items=True)
    
    # Include image information
    images = ImportImage.query.filter_by(document_id=doc_id).all()
    result['images'] = [img.to_dict() for img in images]
    result['images_count'] = len(images)
    
    return jsonify(result), 200


@imports.route('/staging/<int:doc_id>/sme_approve', methods=['POST'])
def sme_approve(doc_id):
    """Approve an import document by SME"""
    try:
        doc = ImportDocument.query.get_or_404(doc_id)
        doc.status = 'approved'  # Changed from 'sme_approved' to 'approved'
        doc.review_step = 'sme_approved'  # Set the review step for frontend
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
        
        # Update status and review step to show final approval
        doc.review_step = 'final_approved'
        db.session.commit()
        current_app.logger.info(f"Import document {doc_id} committed successfully")
        return jsonify({'message': 'Import committed successfully'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error committing import {doc_id}: {str(e)}")
        return jsonify({'error': 'Failed to commit import'}), 500


@imports.route('/staging/<int:doc_id>/reprocess', methods=['POST'])
def reprocess_document(doc_id):
    """Reprocess an existing import document to extract items"""
    try:
        doc = ImportDocument.query.get_or_404(doc_id)
        
        # Delete existing items
        ImportItem.query.filter_by(document_id=doc_id).delete()
        
        # Since we don't have the original file, we can't reprocess
        # This would need to be enhanced to store the original file
        return jsonify({'error': 'Reprocessing requires the original file to be stored'}), 400
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error reprocessing document {doc_id}: {str(e)}")
        return jsonify({'error': f'Failed to reprocess document: {str(e)}'}), 500


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
