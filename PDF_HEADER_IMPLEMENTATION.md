# PDF Header Implementation Summary

## Overview
Added headers to all PDF export pages that display the Form Number, Collection Name, generation date, and a horizontal separator line.

## Implementation Details

### Header Components
1. **First Line**: Form Number, Collection Name (e.g., "SC-50, Office Manual")
2. **Second Line**: Generation date (e.g., "Generated: August 7, 2025")
3. **Horizontal Line**: Spans from left margin to right margin

### Header Positioning
- **Alignment**: Right-aligned at the right margin
- **Location**: Above the content area with 0.8 inch reserved space
- **Font**: Helvetica, 10pt for text
- **Line**: 0.5pt black horizontal line

### Technical Implementation

#### Custom Document Templates
1. **HeaderDocTemplate**: For standard PDFs without background images
2. **BackgroundImageDocTemplate**: Enhanced to include headers with background image support

#### Key Changes Made
1. **Modified BackgroundImageDocTemplate**:
   - Added publication parameter to constructor
   - Added add_header() method for header rendering
   - Updated both title and normal page templates to include headers
   - Reserved space for headers by adjusting content frame height

2. **Created HeaderDocTemplate**:
   - New class specifically for PDFs without background images
   - Implements same header functionality as BackgroundImageDocTemplate
   - Single page template with header support

3. **Updated generate_pdf() function**:
   - Pass publication object to both document templates
   - Use HeaderDocTemplate instead of SimpleDocTemplate for non-background PDFs

#### Header Rendering Logic
```python
def add_header(self, canvas, doc):
    # Extract form number and collection name from publication
    form_number = self.publication.form_number or "Unknown"
    collection_name = self.publication.title or "Unknown Collection"
    
    # Right-align header text at right margin
    # Draw two lines of text with proper spacing
    # Add horizontal line separator
```

## Testing Results
- ✅ Headers appear on all pages of generated PDFs
- ✅ Works with all format types (default, corporate, academic, compact)
- ✅ Compatible with background image functionality
- ✅ Proper spacing between header and content
- ✅ Right-aligned formatting as requested
- ✅ Dynamic content based on publication data (form_number and title)
- ✅ Headers positioned correctly within page bounds (0.5" from top)

## Bug Fixes Applied
- **Fixed header positioning**: Changed from `page_height - topMargin + 0.3 * inch` to `page_height - 0.5 * inch` to ensure headers appear within visible page area
- **Fixed content frame positioning**: Adjusted frame bottom position to `bottomMargin + header_space` to reserve proper space for headers

## Usage
Headers are automatically included in all PDF exports:
- `/api/publications/{id}/export/pdf?format=default`
- `/api/publications/{id}/export/pdf?format=corporate`
- `/api/publications/{id}/export/pdf?format=academic&background_image=sample.png`

## Files Modified
- `backend/routes/publications.py`: Added header functionality to document templates
