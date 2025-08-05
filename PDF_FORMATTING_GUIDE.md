# PDF Formatting Configuration Guide

## Overview
Your StructuredDocs application uses ReportLab for PDF generation, providing professional formatting for publications. The PDF generation is handled in `backend/routes/publications.py`.

## Current PDF Features
- ✅ Hierarchical heading structure (H1-H4+)
- ✅ Table of Contents with proper indentation
- ✅ Professional page layout (A4, 72pt margins)
- ✅ Markdown formatting support (bold, italic, code, lists)
- ✅ Multi-level content indentation
- ✅ Automatic page breaks
- ✅ Title page with publication info

## Customization Areas

### 1. Page Layout & Margins
```python
# In generate_pdf() function around line 747
doc = SimpleDocTemplate(
    buffer,
    pagesize=letter,          # Change to letter, legal, etc.
    rightMargin=72,       # Customize margins (72pt = 1 inch)
    leftMargin=72,
    topMargin=72,
    bottomMargin=18
)
```

### 2. Typography Styles
Current styles defined around line 760:

**Title Style:**
```python
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=24,          # Customize font size
    spaceAfter=30,        # Space after title
    alignment=TA_CENTER   # TA_LEFT, TA_RIGHT, TA_JUSTIFY
)
```

**Content Style:**
```python
content_style = ParagraphStyle(
    'CustomContent',
    parent=styles['Normal'],
    fontSize=11,          # Body text size
    spaceAfter=12,        # Paragraph spacing
    alignment=TA_JUSTIFY, # Text alignment
    leftIndent=0,         # Indentation
    rightIndent=0
)
```

### 3. Heading Hierarchy
Heading styles are defined around line 840 for different levels:

- **Level 0 (Main Headings)**: 18pt, H1 equivalent
- **Level 1 (Sub Headings)**: 15pt, H2 equivalent  
- **Level 2 (Minor Headings)**: 13pt, H3 equivalent
- **Level 3+ (Deep Headings)**: 11pt+, H4+ equivalent

### 4. Colors and Fonts
```python
# Import additional colors
from reportlab.lib import colors

# Example customizations:
textColor=colors.blue,        # Heading colors
fontName='Helvetica-Bold',    # Font family
backgroundColor=colors.lightgrey  # Background colors
```

### 5. Table of Contents Formatting
Around line 810, TOC styling:
```python
toc_style = ParagraphStyle(
    f'TOCLevel{level}',
    parent=content_style,
    leftIndent=level * 20,    # Indentation per level
    fontSize=11 - (level * 0.5), # Size reduction per level
    spaceAfter=6              # Spacing between entries
)
```

## Common Customization Examples

### 1. Change to Letter Size with Smaller Margins
```python
from reportlab.lib.pagesizes import letter

doc = SimpleDocDocument(
    buffer,
    pagesize=letter,      # US Letter instead of A4
    rightMargin=54,       # 0.75 inch margins
    leftMargin=54,
    topMargin=54,
    bottomMargin=54
)
```

### 2. Corporate Color Scheme
```python
# Define corporate colors
corporate_blue = colors.Color(0.0, 0.3, 0.6)  # RGB values
corporate_gray = colors.Color(0.4, 0.4, 0.4)

# Apply to headings
heading_style = ParagraphStyle(
    'CorporateHeading',
    parent=styles['Heading2'],
    fontSize=16,
    textColor=corporate_blue,
    spaceAfter=12
)
```

### 3. Custom Fonts
```python
# Register custom fonts (requires font files)
from reportlab.pdfbase import pdfutils
from reportlab.pdfbase.ttfonts import TTFont

# Register font
pdfutils.registerFont(TTFont('CustomFont', 'path/to/font.ttf'))

# Use in style
custom_style = ParagraphStyle(
    'CustomStyle',
    fontName='CustomFont',
    fontSize=12
)
```

### 4. Enhanced Table of Contents
```python
# Add page numbers (requires more complex implementation)
# Add clickable links (hyperlinks within PDF)
# Custom bullet styles per level
```

### 5. Headers and Footers
```python
# Add page headers/footers (requires custom PageTemplate)
from reportlab.platypus import PageTemplate, Frame

def add_page_number(canvas, doc):
    canvas.drawRightString(200*mm, 20*mm, f"Page {doc.page}")
```

## Advanced Formatting Options

### 1. Tables
```python
from reportlab.platypus import Table, TableStyle

# Create formatted tables for data
table = Table(data)
table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.grey),
    ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE', (0,0), (-1,0), 14),
    ('BOTTOMPADDING', (0,0), (-1,0), 12),
]))
```

### 2. Images and Graphics
```python
from reportlab.platypus import Image
from reportlab.graphics.shapes import Drawing

# Add images
story.append(Image('logo.png', width=2*inch, height=1*inch))

# Add graphics/charts
drawing = Drawing(400, 200)
# ... add shapes to drawing
story.append(drawing)
```

### 3. Conditional Formatting
```python
# Different styles based on content level
if level == 0:
    style = main_heading_style
elif content_type == 'definition':
    style = definition_style
else:
    style = normal_style
```

## Testing Your Changes

1. **Start your Flask server:**
   ```bash
   cd /workspaces/StructuredDocs
   python -m flask --app backend.app run --host=0.0.0.0 --port=5050
   ```

2. **Export a test publication:**
   ```bash
   curl "http://localhost:5050/api/publications/1/export/pdf" -o test.pdf
   ```

3. **View the PDF** to see your formatting changes.

## Best Practices

1. **Maintain hierarchy** - Keep heading levels consistent
2. **Test thoroughly** - PDF rendering can be sensitive to style changes
3. **Consider accessibility** - Use sufficient contrast and readable fonts
4. **Keep consistent spacing** - Use consistent margins and padding
5. **Handle long content** - Ensure text wraps properly across pages

## File Locations

- **Main PDF logic**: `backend/routes/publications.py` (lines 742-1026)
- **Markdown conversion**: `convert_markdown_to_pdf_paragraphs()` function
- **Style definitions**: Around lines 760-900
- **Content generation**: `add_content_nodes()` function

## Next Steps

1. Identify which formatting aspects you want to customize
2. Make small incremental changes and test each one
3. Consider creating a configuration file for easy style management
4. Add any additional ReportLab features you need

The current system provides a solid foundation that you can build upon for your specific formatting requirements.
