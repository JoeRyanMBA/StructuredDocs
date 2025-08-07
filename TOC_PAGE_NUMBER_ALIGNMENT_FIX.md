# TOC Page Number Alignment Fix

## Issue Description
The page numbers in the Table of Contents (TOC) were no longer aligned at the right margin when publishing to PDF. Nested levels (Level 1, 2, 3+) had page numbers that appeared shifted to the left instead of being consistently aligned to the right margin.

## Root Cause
The problem was in the `add_toc_entries` function in `/workspaces/StructuredDocs/backend/routes/publications.py`. The code was using different column widths for different TOC levels:

### Before (Problematic Code):
```python
# Level 1+ entries used adjusted column widths
right_indent = 20 if level == 1 else 40 if level >= 2 else 0
adjusted_title_width = title_width - right_indent
adjusted_page_width = page_num_width + right_indent

# This created tables with different total widths!
toc_table = Table(toc_data, colWidths=[adjusted_title_width, adjusted_page_width])
```

The issue was that `adjusted_page_width = page_num_width + right_indent` was **increasing** the page number column width, which pushed the page numbers further left instead of keeping them at the right margin.

## Solution
**Use identical column widths for ALL TOC levels** to ensure consistent right margin alignment.

### After (Fixed Code):
```python
# CRITICAL FIX: Use SAME column widths as level 0 to ensure page numbers align to right margin
toc_table = Table(toc_data, colWidths=[title_width, page_num_width])
toc_table.setStyle(TableStyle([
    # ... other styles ...
    ('ALIGN', (1, 0), (1, 0), 'RIGHT'),  # Page numbers right-aligned to same position as level 0
    ('RIGHTPADDING', (0, 0), (-1, -1), 0),  # No extra right padding to maintain alignment
]))
```

## Key Changes Made

1. **Consistent Column Widths**: All TOC levels now use the same `colWidths=[title_width, page_num_width]`
2. **Removed Right Indentation Logic**: Eliminated the `right_indent` calculations that were causing misalignment
3. **Simplified Padding**: Set `RIGHTPADDING` to 0 for all levels to maintain consistent alignment
4. **Preserved Visual Hierarchy**: Still use space-based left indentation for nested levels

## Visual Result

### Before (Misaligned):
```
Table of Contents

Chapter 1: Introduction                                    1
  Section 1.1: Overview                              2
    Subsection 1.1.1: Details                   3
```

### After (Properly Aligned):
```
Table of Contents

Chapter 1: Introduction                                    1
  Section 1.1: Overview                                    2
    Subsection 1.1.1: Details                             3
```

## Technical Details

### Table Structure
- **Title Column Width**: `usable_width - 50` points
- **Page Number Column Width**: `50` points (fixed)
- **Total Table Width**: `usable_width` (consistent across all levels)

### Alignment Settings
- **Title Alignment**: `LEFT` with space-based indentation for hierarchy
- **Page Number Alignment**: `RIGHT` (aligned to the same right margin for all levels)
- **Padding**: Consistent negative left padding (-18pt) to align with document margin

## Testing
The fix has been tested across all PDF format presets:
- ✅ `default`: Page numbers properly right-aligned
- ✅ `corporate`: Page numbers properly right-aligned  
- ✅ `academic`: Page numbers properly right-aligned
- ✅ `compact`: Page numbers properly right-aligned
- ✅ `organization`: Page numbers properly right-aligned

## Files Modified
- `/workspaces/StructuredDocs/backend/routes/publications.py` (lines ~830-900)

## Impact
This fix ensures that all TOC page numbers are consistently aligned to the right margin, creating a professional and properly formatted table of contents across all PDF export formats.
