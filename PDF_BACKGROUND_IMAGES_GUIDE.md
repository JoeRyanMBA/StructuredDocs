# PDF Background Images Guide

## Overview
You can now add background images to the title page of your PDF publications. The background image will appear behind the title text, creating a professional and visually appealing document cover.

## Usage

### Basic Usage
Add a `background_image` parameter to your PDF export URL:

```
/api/publications/{id}/export/pdf?background_image=sample.png
```

### Combined with Format
You can combine background images with any PDF format preset:

```
/api/publications/{id}/export/pdf?format=corporate&background_image=company-logo.png
/api/publications/{id}/export/pdf?format=academic&background_image=university-seal.jpg
```

## Background Image Setup

### 1. Image Location
Place your background images in the `backend/static/backgrounds/` directory:

```
backend/
  static/
    backgrounds/
      company-logo.png
      watermark.jpg
      university-seal.png
      abstract-pattern.png
```

### 2. Supported Formats
- PNG (recommended for logos with transparency)
- JPG/JPEG
- GIF
- BMP

### 3. Image Size Recommendations
- **Resolution**: 300 DPI for print quality
- **Dimensions**: Match your page size (e.g., 8.5" x 11" for letter size)
- **Letter Size**: 2550 x 3300 pixels at 300 DPI
- **A4 Size**: 2480 x 3508 pixels at 300 DPI

## Features

### Automatic Scaling
- Images are automatically scaled to cover the entire page
- Aspect ratio is preserved to prevent distortion
- Images are positioned to cover the full page background

### Text Readability
- A semi-transparent white overlay (70% opacity) is applied over the background
- Title text is enhanced with larger font sizes and black color
- Ensures text remains readable over any background image

### Security
- Only images in the `backgrounds` directory are accessible
- File type validation ensures only image files are processed
- Invalid paths or missing files gracefully fallback to no background

## Examples

### Corporate Branding
```bash
# Add company logo watermark to corporate format
curl "/api/publications/3/export/pdf?format=corporate&background_image=company-watermark.png" -o corporate-doc.pdf
```

### Academic Publications
```bash
# Add university seal to academic format
curl "/api/publications/3/export/pdf?format=academic&background_image=university-seal.png" -o academic-paper.pdf
```

### Default with Background
```bash
# Add background to default format
curl "/api/publications/3/export/pdf?background_image=abstract-pattern.jpg" -o document.pdf
```

## Best Practices

### Image Design
1. **Subtle Backgrounds**: Use light, subtle patterns that won't interfere with text
2. **Watermarks**: Position logos/watermarks in corners or as very light overlays
3. **High Contrast**: Ensure sufficient contrast between background and text areas
4. **File Size**: Optimize images to keep PDF file sizes reasonable

### File Naming
- Use descriptive names: `company-logo.png`, `watermark-light.jpg`
- Avoid spaces: Use hyphens or underscores instead
- Keep names short but meaningful

### Testing
- Always test PDFs with background images before production use
- Verify text readability across different devices and printers
- Check file sizes to ensure reasonable download times

## Technical Implementation

### Background Rendering
The background image is rendered using ReportLab's custom page template system:

1. **Full Page Coverage**: Image covers the entire page (0,0 to page width/height)
2. **Preserve Aspect Ratio**: Images maintain proportions to prevent distortion
3. **Transparency Support**: PNG images with transparency are properly handled
4. **Text Overlay**: Semi-transparent white layer ensures text visibility

### Error Handling
- Missing images: Gracefully fallback to no background
- Invalid formats: Only allow approved image file types
- Path security: Restrict access to designated backgrounds directory

## Troubleshooting

### Image Not Appearing
1. Check file exists in `backend/static/backgrounds/` directory
2. Verify file extension is supported (.png, .jpg, .jpeg, .gif, .bmp)
3. Ensure filename in URL matches exactly (case-sensitive)

### Text Not Readable
1. Use lighter background images
2. Add more white space in image design
3. Position important elements away from text areas

### Large File Sizes
1. Optimize images before uploading
2. Use appropriate compression for JPEGs
3. Consider using vector formats for simple logos

This background image feature allows you to create professional, branded PDF documents that maintain excellent readability while showcasing your organization's visual identity.
