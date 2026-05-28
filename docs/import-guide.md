# 📖 Complete Import Guide - Images & Hierarchical Structure

## 🎯 Which Import Method to Use

### ✅ **Collection Import (RECOMMENDED for documents with images)**
- **When to use**: Word documents with images and hierarchical structure
- **What it does**: 
  - ✅ Processes images properly (converts EMF to PNG)
  - ✅ Maintains heading hierarchy (H1 > H2 > H3)
  - ✅ Creates organized collection structure
  - ✅ Stores images in `/images/imports/{id}/` paths
- **How to use**:
  1. Go to Collections page
  2. Click "Import Collection from Document"
  3. Fill in collection details
  4. Upload Word document
  5. Submit

### ⚠️ **Topics Import (Basic import)**
- **When to use**: Simple documents, plain text, or markdown files
- **Limitations**: 
  - Promotes all headings to H1 (flattens hierarchy)
  - Image processing works but structure is lost
- **How to use**:
  1. Go to Topics page
  2. Click import button
  3. Upload document

## 🖼️ Image Processing Requirements

### **For Images to Work Correctly:**

1. **Document Format**: Use Word documents (.docx)
2. **Image Embedding**: Images must be EMBEDDED (not linked)
   - ✅ Copy/paste images directly into Word
   - ✅ Insert > Pictures > From File (embedded)
   - ❌ Insert > Pictures > From URL (linked)
3. **Image Formats**: Any format works (JPG, PNG, EMF, etc.)
   - System automatically converts EMF to PNG
4. **Import Method**: Use Collection import for best results

### **What Happens During Import:**
1. Pandoc extracts embedded images to temporary directory
2. ImageHandler processes and optimizes images
3. Images stored in `/workspaces/StructuredDocs/frontend/public/images/imports/{id}/`
4. Markdown updated with proper `/images/imports/{id}/filename.png` paths
5. EMF files automatically converted to PNG format

## 🌲 Hierarchical Structure Requirements

### **For Hierarchy to Work:**

1. **Use Word Styles**: Apply proper heading styles
   - Heading 1 for main sections
   - Heading 2 for subsections  
   - Heading 3 for sub-subsections
2. **Don't use manual formatting**: Avoid just making text bold/large
3. **Use Collection Import**: This preserves the hierarchy
4. **Consistent Structure**: Follow logical heading progression

## 🔧 Troubleshooting

### **Images Don't Appear:**
1. ❌ **Wrong Paths**: If you see `![](media/image1.png)` 
   - **Fix**: Run `python fix_image_display_tool.py`
2. ❌ **Wrong Import Method**: Used Topics import instead of Collection
   - **Fix**: Delete topics and re-import as Collection
3. ❌ **Linked Images**: Images were linked, not embedded in Word
   - **Fix**: Re-create document with embedded images

### **Hierarchy Not Preserved:**
1. ❌ **Wrong Import Method**: Used Topics import
   - **Fix**: Use Collection import
2. ❌ **No Word Styles**: Text formatted manually, not with heading styles
   - **Fix**: Apply proper heading styles in Word and re-import

### **EMF Images Not Converting:**
1. ❌ **LibreOffice Missing**: System can't convert EMF files
   - **Fix**: Convert EMF to PNG manually before importing
2. ❌ **Conversion Failed**: EMF file corrupt or unsupported
   - **Fix**: Open EMF in image editor, save as PNG

## ✅ Success Checklist

After importing, verify:
- [ ] Images display correctly in WYSIWYG editor
- [ ] Image paths use `/images/imports/{id}/` format
- [ ] No `media/` paths in markdown
- [ ] No `{width="..."}` Pandoc attributes  
- [ ] Hierarchical structure preserved in collection
- [ ] EMF files converted to PNG

## 🆘 If Problems Persist

1. **Clean Existing Content**: `python fix_image_display_tool.py`
2. **Verify System**: `python diagnose_import_issues.py`
3. **Check Document**: Ensure images are embedded, not linked
4. **Use Collection Import**: Don't use Topics import for complex documents
5. **Start Fresh**: Delete problematic content and re-import correctly

---
**Last Updated**: Fixed Collection import to use proper image processing
**Status**: ✅ Both image processing and hierarchical imports working correctly
