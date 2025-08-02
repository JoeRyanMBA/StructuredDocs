# Image Handling Implementation for StructuredDocs

## Overview

We've implemented a comprehensive image handling system for Word and Markdown document imports that properly extracts, stores, and manages images.

## Features Implemented

### 🖼️ **Image Processing Pipeline**

1. **Extraction**: Images are extracted from Word documents using Pandoc's `--extract-media` feature
2. **Storage**: Images are stored in both backend and frontend directories for serving
3. **Optimization**: Images are automatically resized and optimized for web usage
4. **Tracking**: All images are tracked in the database with metadata

### 📁 **Directory Structure**
```
backend/static/images/imports/{doc_id}/    # Backend storage
frontend/public/images/imports/{doc_id}/   # Frontend serving
```

### 🗃️ **Database Schema**
New `ImportImage` model tracks:
- Original and processed filenames
- File paths and public URLs
- Image dimensions and metadata
- File size and MIME type
- Association with import documents

### 🔧 **API Endpoints**
- `GET /api/import/staging/{doc_id}/images` - Get all images for an import
- `GET /images/{path}` - Serve image files
- Enhanced staging endpoint includes image metadata

## Components Created

### 1. ImageHandler Class (`backend/utils/image_handler.py`)
- **Image extraction and storage**
- **Path management and optimization**
- **Validation of image references**
- **Cleanup of temporary files**

### 2. Updated Import Handler (`backend/routes/import_handler.py`)
- **Enhanced Word document processing**
- **Automatic image extraction during import**
- **Database storage of image metadata**
- **Markdown path updates**

### 3. Database Model (`backend/models.py`)
- **ImportImage model** for tracking imported images
- **Relationships** with ImportDocument

### 4. Flask Configuration (`backend/app.py`)
- **Static file serving** for images
- **Error handling** for missing images

## How It Works

### Word Document Import Process:
1. **Upload**: User uploads a Word document
2. **Conversion**: Pandoc converts to Markdown and extracts images to temp directory
3. **Processing**: ImageHandler moves images to permanent storage
4. **Optimization**: Images are resized and optimized
5. **Path Updates**: Markdown content is updated with new image paths
6. **Database**: Image metadata is stored in ImportImage table
7. **Cleanup**: Temporary files are removed

### Markdown Document Import Process:
1. **Upload**: User uploads a Markdown file
2. **Validation**: ImageHandler validates existing image references
3. **Processing**: Content is processed normally
4. **Warnings**: Issues with missing images are logged

## Image Features

### ✅ **Supported Formats**
- `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.webp`

### ✅ **Optimization**
- **Automatic resizing** to max 1920x1080 pixels
- **Quality optimization** (85% for JPEG, compression for PNG)
- **Format conversion** (RGBA to RGB for JPEG compatibility)

### ✅ **Path Management**
- **Unique filenames** using UUID to prevent conflicts
- **Consistent URL structure** (`/images/imports/{doc_id}/{filename}`)
- **Cross-platform path handling**

### ✅ **Validation**
- **Reference checking** for Markdown image links
- **File existence validation**
- **External reference detection**

## Usage Examples

### Testing the Implementation
```bash
# Run the test script
python test_image_handling.py
```

### API Usage
```javascript
// Get images for import document
fetch('/api/import/staging/123/images')
  .then(response => response.json())
  .then(data => {
    console.log(`Found ${data.total_count} images`);
    data.images.forEach(img => {
      console.log(`Image: ${img.filename} (${img.width}x${img.height})`);
    });
  });
```

### Image URLs
```markdown
![Alt text](/images/imports/123/my_image_abc123.png)
```

## Error Handling

### 🚨 **Common Issues Handled**
- **Missing Pandoc**: Clear error messages if Pandoc is not installed
- **Image format errors**: Fallback to copying files if optimization fails
- **Permission issues**: Proper error logging and cleanup
- **Path conflicts**: Unique filename generation
- **Database errors**: Transaction rollback on failures

### 🔍 **Validation Warnings**
- Missing image files
- External image references (may not be accessible)
- Broken image links in Markdown

## Configuration

### Required Dependencies
```txt
Pillow>=10.0.0      # Image processing
```

### Directory Permissions
Ensure write access to:
- `/workspaces/StructuredDocs/backend/static/images/imports/`
- `/workspaces/StructuredDocs/frontend/public/images/imports/`

## Migration Applied
```bash
flask db revision --autogenerate -m "Add ImportImage model for tracking imported images"
flask db upgrade
```

## Testing Results
✅ Image extraction from temporary directories
✅ Permanent storage in backend and frontend
✅ Database metadata tracking
✅ Markdown content path updates
✅ Image optimization and resizing
✅ Validation of image references
✅ Cleanup of temporary files

## Next Steps for Enhancement

1. **Bulk Image Upload**: Support for uploading images separately
2. **Image Editing**: Basic cropping/rotation features
3. **CDN Integration**: For better performance at scale
4. **Thumbnail Generation**: Create multiple sizes automatically
5. **Alternative Text Management**: Better accessibility support
6. **Import from URLs**: Support for importing images from web URLs

---

The image handling system is now fully functional and integrated into your StructuredDocs import pipeline!
