from flask import Blueprint, request, jsonify, current_app, make_response
from werkzeug.utils import secure_filename
from ..models import db, ImportDocument, ImportItem, ImportImage, Topic
from ..utils.image_handler import ImageHandler
import re
from docx import Document
import io
import subprocess
import tempfile
import os
import uuid

import_bp = Blueprint('import_handler', __name__, url_prefix='/api/import')
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
            
            # Fix progressive list indentation issues from Word conversion
            updated_markdown = _fix_list_indentation(updated_markdown)
            print(f"LIST INDENTATION: Fixed progressive indentation issues")
            
            # Remove all blank lines from Word document content
            updated_markdown = _remove_all_blank_lines(updated_markdown)
            print(f"BLANK LINE REMOVAL: Removed all blank lines from Word document content")
            
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
    except FileNotFoundError:
        print("PANDOC ERROR: Pandoc not found")
        raise Exception("Pandoc is not installed. Please contact your system administrator to install pandoc for Word document conversion.")
    except subprocess.CalledProcessError as e:
        print(f"PANDOC ERROR: Process failed with code {e.returncode}: {e.stderr}")
        raise Exception(f"Pandoc conversion failed: {e.stderr}")
    except Exception as e:
        print(f"PANDOC ERROR: {str(e)}")
        # Check if it's a pandoc not found error
        if "pandoc" in str(e).lower() and ("not found" in str(e).lower() or "command not found" in str(e).lower()):
            raise Exception("Pandoc is not installed. Please contact your system administrator to install pandoc for Word document conversion.")
        raise Exception(f"Failed to convert Word to Markdown: {str(e)}")


def _post_process_markdown(markdown_content):
    """Post-process markdown to fix nested lists and handle margin notes while preserving blank lines"""
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
                    # Replace the entire HTML fenced block with converted markdown
                    processed_lines.extend(converted_list.split('\n'))
                else:
                    # Could not convert; keep original fenced block
                    processed_lines.append(lines[i])
                    processed_lines.extend(html_content)
                    processed_lines.append('```')
                # Skip past the closing fence
                i = j + 1
                continue
            else:
                # No closing fence found; keep the line as-is
                processed_lines.append(line)
                i += 1
                continue
        
        # Default: keep line
        processed_lines.append(line)
        i += 1

    # Join back the processed lines; further cleaning handled by other steps
    return '\n'.join(processed_lines)


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


def _fix_list_indentation(content):
    """Fix progressive list indentation issues from Word document conversion"""
    if not content or not content.strip():
        return content
    
    lines = content.split('\n')
    fixed_lines = []
    
    # Track the current indentation context
    current_list_type = None  # 'bullet' or 'numbered'
    indentation_stack = []  # Track indentation levels
    
    for line in lines:
        original_line = line
        stripped = line.strip()
        
        # Check if this is a list item (bullet or numbered)
        bullet_match = re.match(r'^(\s*)[-*+]\s+(.*)$', line)
        numbered_match = re.match(r'^(\s*)(\d+\.)\s+(.*)$', line)
        
        if bullet_match:
            leading_spaces = bullet_match.group(1)
            content_text = bullet_match.group(2)
            space_count = len(leading_spaces)
            
            # Determine indentation level (0, 1, 2, or 3 max)
            if space_count == 0:
                level = 0
            elif space_count <= 3:
                level = 1
            elif space_count <= 7:
                level = 2
            else:
                level = 3  # Cap at 3 levels
            
            # Apply consistent indentation
            indent = "  " * level  # 2 spaces per level
            fixed_line = f"{indent}- {content_text}"
            fixed_lines.append(fixed_line)
            
        elif numbered_match:
            leading_spaces = numbered_match.group(1)
            number_part = numbered_match.group(2)
            content_text = numbered_match.group(3)
            space_count = len(leading_spaces)
            
            # Determine indentation level (0, 1, 2, or 3 max)
            if space_count == 0:
                level = 0
            elif space_count <= 3:
                level = 1
            elif space_count <= 7:
                level = 2
            else:
                level = 3  # Cap at 3 levels
            
            # Apply consistent indentation
            indent = "  " * level  # 2 spaces per level
            fixed_line = f"{indent}{number_part} {content_text}"
            fixed_lines.append(fixed_line)
            
        else:
            # Not a list item, keep as is
            fixed_lines.append(original_line)
    
    return '\n'.join(fixed_lines)


def _remove_all_blank_lines(content):
    """Remove all blank lines from content - specifically for Word document imports"""
    if not content or not content.strip():
        return ''
    
    lines = content.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Skip any line that is empty or contains only whitespace
        if line.strip() == '':
            continue
        
        # Skip lines that are just HTML paragraph tags (including with whitespace inside)
        if re.match(r'^\s*<\s*/?p\s*/?>\s*$', line):
            continue
        
        # Skip empty HTML paragraph pairs specifically
        if re.match(r'^\s*<p></p>\s*$', line):
            continue
        
        # Skip lines with only non-breaking spaces or similar HTML entities
        if re.match(r'^\s*(&nbsp;|\s|&\w+;)*\s*$', line):
            continue
            
        # Skip empty list items
        if re.match(r'^\s*[-*+]\s*$', line):
            continue
            
        # Skip empty numbered list items
        if re.match(r'^\s*\d+\.\s*$', line):
            continue
        
        # Skip Word document artifacts
        if re.match(r'^\s*\[\s*\]\s*$', line):  # Empty checkboxes
            continue
            
        if re.match(r'^\s*\\\s*$', line):  # Stray backslashes
            continue
            
        # Skip lines with only formatting marks or tabs
        if re.match(r'^\s*[\t\r\f\v]+\s*$', line):
            continue
            
        # Skip Word table artifacts like empty table cells
        if re.match(r'^\s*\|\s*\|\s*$', line):
            continue
        
        # Skip HTML comments
        if re.match(r'^\s*<!--.*?-->\s*$', line):
            continue
        
        # Skip empty HTML tags more broadly
        if re.match(r'^\s*<\s*/?[^>]*>\s*$', line.strip()):
            continue
        
        # Keep all non-empty lines
        cleaned_lines.append(line)
    
    # Join lines without any blank lines between them
    cleaned_content = '\n'.join(cleaned_lines)
    
    # Remove leading/trailing whitespace
    cleaned_content = cleaned_content.strip()
    
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
    
    # Remove excessive blank lines (more than 2 consecutive)
    cleaned_content = re.sub(r'\n\s*\n\s*\n\s*\n+', '\n\n\n', cleaned_content)
    
    # Clean up common Word artifacts in the content
    cleaned_content = re.sub(r'\s*\n\s*\n\s*\n\s*\n+', '\n\n', cleaned_content)  # Multiple newlines
    # NOTE: Removed the aggressive single newline joining to preserve paragraph breaks
    
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
        # Parse Word document: try pandoc first, then python-docx fallback
        print(f"PARSING WORD DOC: {imp_doc.filename}")
        # Read file content for conversion attempts
        file_content = file.read()
        file.stream.seek(0)  # Reset stream for potential future reads

        lines = []
        try:
            # Primary conversion via pandoc
            markdown_content = _convert_word_to_markdown(file_content, imp_doc.id)

            # Treat as Markdown lines with H1 promotion
            for line in markdown_content.splitlines():
                if line.strip().startswith('#'):
                    hash_count = len(line) - len(line.lstrip('#'))
                    if hash_count > 1:
                        content = line.lstrip('#').strip()
                        line = f"# {content}"
                        print(f"PROMOTED: '{line.strip()}' (was H{hash_count})")
                lines.append(line)

            md_snippet = '\n'.join(lines[:10])
            print(f"MARKDOWN SNIPPET (first 10 lines):\n{md_snippet}")
            current_app.logger.info(f"Parsed Markdown snippet for {imp_doc.filename}:\n{md_snippet}")
        except Exception as e:
            # Fallback: attempt to read headings and paragraphs via python-docx
            print(f"PANDOC/CONVERSION ERROR: {e}")
            current_app.logger.error(f"Pandoc or conversion failed for {imp_doc.filename}: {e}")
            snippet = file_content[:500]
            current_app.logger.error(f"First 500 bytes of file: {snippet}")

            try:
                doc = Document(io.BytesIO(file_content))
                # Extract paragraphs and headings
                for p in doc.paragraphs:
                    text = (p.text or '').strip()
                    if not text:
                        continue
                    style_name = ''
                    try:
                        ps = getattr(p, 'style', None)
                        style_name = (getattr(ps, 'name', '') or '').lower()
                    except Exception:
                        style_name = ''
                    level = None
                    m = re.search(r'heading\s*(\d+)', style_name)
                    if m:
                        try:
                            level = int(m.group(1))
                        except ValueError:
                            level = None
                    if level == 1:
                        lines.append(f"# {text}")
                    elif level and level > 1:
                        hashes = '#' * min(level, 6)
                        lines.append(f"{hashes} {text}")
                    else:
                        lines.append(text)
                # Extract tables and convert to Markdown
                for table in doc.tables:
                    # Get all rows as lists of cell text
                    table_rows = []
                    for row in table.rows:
                        table_rows.append([cell.text.strip().replace('\n', ' ') for cell in row.cells])
                    if not table_rows:
                        continue
                    # Build Markdown pipe table
                    header = table_rows[0]
                    aligns = ['---'] * len(header)
                    md_table = ['| ' + ' | '.join(header) + ' |', '| ' + ' | '.join(aligns) + ' |']
                    for row in table_rows[1:]:
                        md_table.append('| ' + ' | '.join(row) + ' |')
                    lines.append('')
                    lines.extend(md_table)
                    lines.append('')
                md_snippet = '\n'.join(lines[:10])
                print(f"DOCX FALLBACK SNIPPET (first 10 lines):\n{md_snippet}")
                current_app.logger.info(f"DOCX fallback parsed snippet for {imp_doc.filename}:\n{md_snippet}")
            except Exception as e2:
                print(f"DOCX FALLBACK ERROR: {e2}")
                current_app.logger.error(f"DOCX fallback failed for {imp_doc.filename}: {e2}")
                lines = []

        paras = [('md', line) for line in lines]
        full_text = '\n'.join(lines)
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
        full_text = '\n'.join(lines)

    items, buffer, order, current_title = [], [], 0, None
    print(f"PARSING: source={source}, paragraphs={len(paras)}")

    def commit_buffer():
        nonlocal order, current_title, buffer
        if current_title:
            content = '\n'.join(buffer).strip()
            
            # Apply additional content cleaning
            if source == 'word':
                # For Word documents, remove ALL blank lines as requested
                content = _remove_all_blank_lines(content)
            else:
                # For Markdown documents, use the existing cleaning that preserves paragraph breaks
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
            current_buffer_has_content = bool(current_buffer_content and 
                                            not all(line.strip() == '' or line.strip().startswith('#') 
                                                   for line in current_buffer_content.split('\n')))
            
            if current_title and not current_buffer_has_content:
                # Merge this heading into the content of the previous heading
                heading_text = text.strip().lstrip('#').strip()
                buffer.append(f"## {heading_text}")  # Add as H2 in content
                print(f"MERGED_HEADING: '{heading_text}' added to content of '{current_title}' (no substantive content found)")
            else:
                # Normal case: commit previous section and start new one
                commit_buffer()
                current_title = text.strip().lstrip('#').strip()
                print(f"NEW_TITLE: '{current_title}'")
        else:
            buffer.append(text)

    commit_buffer()
    print(f"FINAL: {len(items)} items created")

    # Fallback: if no items were created, use entire content as a single item
    if not items:
        try:
            fallback_title = os.path.splitext(imp_doc.filename)[0] if getattr(imp_doc, 'filename', None) else 'Imported Document'
            fallback_content = full_text if 'full_text' in locals() else ''
            if source == 'word':
                fallback_content = _remove_all_blank_lines(fallback_content)
            else:
                fallback_content = _clean_topic_content(fallback_content)

            if fallback_content and fallback_content.strip():
                print(f"FALLBACK: Creating single item from full document. title='{fallback_title}', content_len={len(fallback_content)}")
                items.append((0, fallback_title, fallback_content))
            else:
                print("FALLBACK: Full document content is empty after cleaning; no item created")
        except Exception as e:
            print(f"FALLBACK ERROR: {e}")

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
    import_type = request.form.get('import_type', 'topics')  # Default to topics for backward compatibility
    
    if not file or source not in SOURCES:
        print(f"UPLOAD: Missing file or invalid source. file={file}, source={source}")
        return jsonify({'error': 'Missing file or invalid source'}), 400

    try:
        # Handle collection import
        if import_type == 'collection':
            return _import_as_collection(file, source)
        else:
            # Handle regular topic import (existing functionality)
            return _import_as_topics(file, source)

    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Upload failed")
        print(f"UPLOAD: Exception occurred: {e}")
        return jsonify({'error': str(e)}), 500


def _import_as_topics(file, source):
    """Import document as individual topics (original functionality)"""
    imp_doc = ImportDocument(
        filename=secure_filename(file.filename),
        source_type=source
    )
    db.session.add(imp_doc)
    db.session.flush()  # get imp_doc.id
    print(f"UPLOAD: Created ImportDocument with ID={imp_doc.id}")

    _parse_and_store(file, imp_doc, source)
    
    # Check if any items were created
    items_count = ImportItem.query.filter_by(document_id=imp_doc.id).count()
    print(f"UPLOAD: Created {items_count} import items")
    
    if items_count == 0:
        db.session.rollback()
        # Try to log more details for debugging
        file_content = b""  # ensure defined even if read fails below
        try:
            file.stream.seek(0)
            file_content = file.read()
            snippet = file_content[:500]
        except Exception as e:
            snippet = f"Could not read file content: {e}"
        # Try to get a snippet of the Markdown if possible
        try:
            markdown_content = _convert_word_to_markdown(file_content, imp_doc.id) if source == 'word' else file_content.decode('utf-8')
            md_lines = markdown_content.splitlines()[:10]
            md_snippet = '\n'.join(md_lines)
        except Exception as e:
            md_snippet = f"Could not get Markdown snippet: {e}"
        error_msg = f"No content items could be extracted from {imp_doc.filename}. "
        if source == 'word':
            error_msg += "This may be due to: 1) The document has no recognizable headings, 2) Pandoc conversion failed, or 3) The document structure is not supported."
        else:
            error_msg += "This may be due to: 1) The document has no H1 headings (# Title), or 2) The file is empty or corrupted."
        error_msg += f"\nFirst 500 bytes of file: {snippet}\nMarkdown snippet (first 10 lines):\n{md_snippet}"
        print(f"UPLOAD: {error_msg}")
        current_app.logger.error(error_msg)
        return jsonify({'error': error_msg}), 422
    
    db.session.commit()
    print(f"UPLOAD: Committed to database")
    return jsonify(imp_doc.to_dict(include_items=True)), 201


def _import_as_collection(file, source):
    """Import document as a collection with hierarchical structure"""
    # Use package-relative import to avoid importing backend.models twice
    from ..models import Collection, Topic, collection_topic_tree, Project
    
    # Get collection details from form
    collection_name = request.form.get('collection_name', '').strip()
    collection_form_number = request.form.get('collection_form_number', '').strip()
    collection_description = request.form.get('collection_description', '').strip()
    project_id = request.form.get('project_id', '').strip()
    
    if not collection_name:
        return jsonify({'error': 'Collection name is required'}), 400
    if not collection_form_number:
        return jsonify({'error': 'Collection ID (Form Number) is required'}), 400
    if not project_id:
        return jsonify({'error': 'Project selection is required'}), 400
    
    # Validate that the project exists
    try:
        project_id = int(project_id)
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Selected project does not exist'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid project ID'}), 400
    
    # Check if form number already exists
    existing_collection = Collection.query.filter_by(form_number=collection_form_number).first()
    if existing_collection:
        return jsonify({'error': f'Collection ID "{collection_form_number}" already exists'}), 400
    
    # Create temporary import document to parse content
    temp_imp_doc = ImportDocument(
        filename=secure_filename(file.filename),
        source_type=source
    )
    db.session.add(temp_imp_doc)
    db.session.flush()  # get temp_imp_doc.id
    print(f"COLLECTION_IMPORT: Created temporary ImportDocument with ID={temp_imp_doc.id}")
    
    # Parse the document into import items
    _parse_and_store(file, temp_imp_doc, source)
    
    # Check if any items were created
    import_items = ImportItem.query.filter_by(document_id=temp_imp_doc.id).all()
    if not import_items:
        db.session.rollback()
        error_msg = f"No content items could be extracted from {temp_imp_doc.filename}. "
        if source == 'word':
            error_msg += "This may be due to: 1) The document has no recognizable headings, 2) Pandoc conversion failed, or 3) The document structure is not supported."
        else:
            error_msg += "This may be due to: 1) The document has no H1 headings (# Title), or 2) The file is empty or corrupted."
        return jsonify({'error': error_msg}), 422
    
    print(f"COLLECTION_IMPORT: Parsed {len(import_items)} items from document")
    
    # Create the collection
    collection = Collection(
        name=collection_name,
        form_number=collection_form_number,
        description=collection_description or None,
        project_id=project_id
    )
    db.session.add(collection)
    db.session.flush()  # get collection.id
    print(f"COLLECTION_IMPORT: Created collection with ID={collection.id}")
    
    # Convert import items to topics and add them to the collection
    created_topics = []
    for item in import_items:
        topic = Topic(
            title=item.title,
            content=item.content
        )
        db.session.add(topic)
        db.session.flush()  # get topic.id
        created_topics.append(topic)
        
        # Add topic to collection (maintain order from import)
        db.session.execute(
            collection_topic_tree.insert().values(
                collection_id=collection.id,
                topic_id=topic.id,
                position=item.heading_order,
                parent_topic_id=None  # All topics at the same level initially
            )
        )
    
    print(f"COLLECTION_IMPORT: Created {len(created_topics)} topics and added to collection")
    
    # Clean up the temporary import document and associated images
    # First, delete any associated import images
    ImportImage.query.filter_by(document_id=temp_imp_doc.id).delete()
    
    # Then delete the temporary import document
    db.session.delete(temp_imp_doc)
    
    # Commit everything
    db.session.commit()
    print(f"COLLECTION_IMPORT: Successfully committed collection import and cleaned up temporary data")
    
    return jsonify({
        'collection_id': collection.id,
        'collection_name': collection.name,
        'collection_form_number': collection.form_number,
        'topics_count': len(created_topics),
        'message': f'Successfully imported {len(created_topics)} topics into collection "{collection.name}"'
    }), 201


@import_bp.route('/upload', methods=['POST'])
def upload_generic():
    return _upload_file(request.form.get('source', '').lower())


@import_bp.route('/markdown', methods=['POST'])
def upload_markdown():
    return _upload_file('markdown')


@import_bp.route('/history', methods=['GET'])
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


@import_bp.route('/staging/<int:doc_id>/images', methods=['GET'])
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


@import_bp.route('/staging/<int:doc_id>', methods=['GET'])
def get_staging(doc_id):
    doc = ImportDocument.query.get_or_404(doc_id)
    result = doc.to_dict(include_items=True)
    
    # Include image information
    images = ImportImage.query.filter_by(document_id=doc_id).all()
    result['images'] = [img.to_dict() for img in images]
    result['images_count'] = len(images)
    
    return jsonify(result), 200


@import_bp.route('/staging/<int:doc_id>/sme_approve', methods=['POST'])
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


@import_bp.route('/staging/<int:doc_id>/commit', methods=['POST'])
def commit_import(doc_id):
    """Commit an approved import to create actual topics"""
    try:
        doc = ImportDocument.query.get_or_404(doc_id)
        if doc.status != 'approved':  # Changed from 'sme_approved' to 'approved'
            return jsonify({'error': 'Import must be approved before commit'}), 400
        
        # Create topics from import items
        for item in doc.items:
            # Create topic from import item (Topic has no heading_order field)
            topic = Topic(
                title=item.title,
                content=item.content
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


@import_bp.route('/staging/<int:doc_id>/reprocess', methods=['POST'])
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


@import_bp.route('/staging/<int:doc_id>/reject', methods=['POST'])
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
