# Background Images Directory

This directory contains background images that can be used for PDF title pages.

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
