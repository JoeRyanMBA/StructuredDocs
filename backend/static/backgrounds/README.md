# Background Images Directory

This directory contains background images that can be used for PDF title pages.
The background fills the title page edge to edge without changing the margins
for text or other pages. If the image and page have different aspect ratios,
the image is scaled proportionally and cropped around the center. Match the
page's aspect ratio to keep the entire image visible.

Under **Export Branding Settings**, set **PDF Cover Text Alignment** to
**Center** to center the title and subtitle horizontally, with or without a
background image. **Right** preserves the original layout. Save the settings
to change the default, or save the current branding as a template to set the
alignment for publications using that template without changing the default.

**PDF Cover Text Vertical Alignment** controls where the title and subtitle
sit on the page. **Top** preserves the original layout. **Center** centers
them together vertically, independently of their horizontal alignment.

**PDF Cover Text Color** sets the color of both the title and subtitle. Enter
a six-digit hex color (for example, `#112E51`), or leave it blank to use white
on covers with a background image and the default text colors on plain covers.
You can save the color as a default or as part of a branding template.

**PDF Cover Logo Placement** moves the cover logo to the left, center, or
right at the top or bottom of the page. **Bottom Left** preserves the
existing layout. Bottom Center and Bottom Right place the logo just above
the cover footer text. Save the placement as a default or as part of a
branding template. It does not move the footer logo on later pages.

The Export Branding Settings uploader validates image contents, not just file
extensions. Existing files that contain placeholder text or corrupt image data
cannot produce thumbnails; re-upload the original image and select the new asset.
Preview failures are shown on the asset card without removing the file or changing
saved branding settings.
SVG uploads containing XML entity declarations are rejected.

## Usage

Reference these images in PDF export URLs:

```

/api/publications/{id}/export/pdf?background_image=filename.png

```

## Supported Formats

- PNG (recommended for logos with transparency)

- JPG/JPEG

- GIF

- BMP

## Image Guidelines

- **Resolution**: 300 DPI for print quality

- **Letter Size**: 2550 x 3300 pixels

- **A4 Size**: 2480 x 3508 pixels

- **Design**: Use subtle, light backgrounds that won't interfere with text readability

## Examples

Place your background images here:

- `company-logo.png` - Corporate branding

- `watermark.jpg` - Light watermark

- `university-seal.png` - Academic institution logo

- `abstract-pattern.png` - Decorative background

The system automatically adds a semi-transparent overlay to ensure text remains readable over any background image.
