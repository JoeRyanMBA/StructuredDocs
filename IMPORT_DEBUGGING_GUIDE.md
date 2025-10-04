# Import Debugging Guide

## Issue Analysis

The error "No content items could be extracted from the document" can occur for several reasons:

1. **Document has no recognizable headings**

2. **Pandoc conversion failed**

3. **Document structure is not supported**

4. **Hierarchical parsing logic has bugs**

## Debugging Steps

### Step 1: Check Document Structure

Your document should have clear headings that start with `#`:

```markdown

# Main Heading (H1)

Content goes here.

## Sub Heading (H2)

More content.

### Sub-sub Heading (H3)

Even more content.

```

### Step 2: Test with Simple Document

Create a simple test document to verify the import works:

```markdown

# Test Document

This is a simple test document.

## Section 1

Content for section 1.

## Section 2

Content for section 2.

```

### Step 3: Check Backend Logs

Look for these log messages in the backend:

- `PARSING WORD DOC: filename.docx`

- `PANDOC: Running command: ...`

- `HEADING DETECTED: ...` or `HEADING PRESERVED: ...`

- `COMMITTED: order=X, title='...', content_len=Y`

### Step 4: Verify Environment

Make sure these are available:

- `pandoc` command (for Word documents)

- `python-docx` library (fallback for Word documents)

- Temporary directory write permissions

## Fixed Issues

I've made several improvements to fix the import issues:

1. **Enhanced Hierarchical Parsing**: Fixed parent relationship calculation

2. **Better Error Handling**: Added fallback to flat parsing if hierarchical fails

3. **Improved Logging**: More detailed debug information

4. **Markdown Support**: Hierarchical parsing now works for both Word and Markdown files

## Testing the Fix

Try importing your document again. The system will now:

1. First attempt hierarchical parsing

2. If that fails, fall back to regular flat parsing

3. Provide detailed error messages if both fail

4. Show debug information in the logs

If you're still getting the error, please check:

- The document actually contains text content

- The headings are properly formatted (space after #)

- The file is not corrupted

- Backend server has proper permissions
