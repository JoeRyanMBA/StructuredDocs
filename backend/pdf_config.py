"""
PDF Formatting Configuration
Centralized configuration for PDF export styling
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet


def hex_to_color(hex_string):
    """Convert hex color string to ReportLab Color object
    
    Args:
        hex_string (str): Hex color like '#FF5733', '#ff5733', or 'FF5733'
    
    Returns:
        colors.Color: ReportLab Color object
    """
    # Remove # if present
    hex_string = hex_string.lstrip('#')
    
    # Convert hex to RGB values (0-1 range)
    r = int(hex_string[0:2], 16) / 255.0
    g = int(hex_string[2:4], 16) / 255.0
    b = int(hex_string[4:6], 16) / 255.0
    
    return colors.Color(r, g, b)

class PDFConfig:
    """Centralized PDF formatting configuration"""
    
    # Page Layout
    PAGE_SIZE = letter  # Options: A4, letter, legal (changed from A4 to letter)
    MARGINS = {
        'top': 72,     # 1 inch
        'bottom': 18,  # 0.25 inch
        'left': 72,    # 1 inch  
        'right': 72    # 1 inch
    }
    
    # Corporate Colors (customize these with your organization's palette)
    COLORS = {
        # Replace these hex values with your brand colors
        'primary': hex_to_color('#112e51'),      # e.g., '#1E3A8A'
        'secondary': hex_to_color('#FF5622'),  # e.g., '#059669'
        'accent': hex_to_color('#008392'),        # e.g., '#DC2626'
        
        # Functional colors
        'text': hex_to_color('#000000'),                     # Dark gray for readability
        'heading': hex_to_color('#112e51'),                  # Nearly black for headings
        'subheading': hex_to_color('#444444'),               # Medium gray

        # Heading level colors (customize these for different heading levels)
        'h1_color': hex_to_color('#112e51'),     # H1 color - dark blue
        'h2_color': hex_to_color('#9B2743'),     # H2 color - orange/red
        'h3_color': hex_to_color('#000000'),     # H3 color - teal
        'h4_color': hex_to_color('#205493'),     # H4 color - dark gray
        'h5_color': hex_to_color('#666666'),     # H5+ color - medium gray

        # Background colors
        'light_bg': hex_to_color('#F9FAFB'),                 # Very light gray
        'highlight': hex_to_color('#FEF3C7'),                # Yellow highlight
        'border': hex_to_color('#D1D5DB'),                   # Border gray
    }
    
    # Typography
    FONTS = {
        'title': 'Helvetica-Bold',
        'heading': 'Helvetica-Bold', 
        'body': 'Times-Roman',
        'caption': 'Helvetica-Oblique',
        'code': 'Courier'
    }
    
    FONT_SIZES = {
        'title': 24,
        'subtitle': 16,
        'h1': 18,
        'h2': 18,  # Increased to 18 to match H1 size
        'h3': 13,
        'h4': 11,
        'body': 11,
        'caption': 9,
        'toc': 11
    }
    
    # Spacing
    SPACING = {
        'title_after': 30,
        'subtitle_after': 20,
        'heading_before': 10,
        'heading_after': 12,
        'paragraph_after': 12,
        'section_after': 16,
        'toc_item': 6
    }
    
    # Indentation
    INDENTS = {
        'content_per_level': 15,  # Indent for nested content
        'toc_per_level': 12,      # Reduced indent for TOC levels (was 20)
        'list_indent': 20         # Indent for list items
    }

    @classmethod
    def get_base_styles(cls):
        """Get ReportLab base styles"""
        return getSampleStyleSheet()
    
    @classmethod
    def create_title_style(cls, base_styles):
        """Create title page style"""
        return ParagraphStyle(
            'CustomTitle',
            parent=base_styles['Heading1'],
            fontName=cls.FONTS['title'],
            fontSize=cls.FONT_SIZES['title'],
            leading=cls.FONT_SIZES['title'] * 1.3,  # Set line height for wrapped titles
            spaceAfter=cls.SPACING['title_after'],
            alignment=TA_CENTER,
            textColor=cls.COLORS['primary']
        )
    
    @classmethod
    def create_subtitle_style(cls, base_styles):
        """Create subtitle style"""
        return ParagraphStyle(
            'CustomSubtitle',
            parent=base_styles['Normal'],
            fontName=cls.FONTS['heading'],  # Changed from 'caption' to 'heading' for consistency
            fontSize=cls.FONT_SIZES['subtitle'],
            leading=cls.FONT_SIZES['subtitle'] * 1.3,  # Set line height for wrapped subtitles
            spaceAfter=cls.SPACING['subtitle_after'],
            alignment=TA_CENTER,
            textColor=cls.COLORS['secondary']
        )
    
    @classmethod
    def create_heading_style(cls, base_styles, level=0):
        """Create heading style for specified level"""
        font_sizes = [
            cls.FONT_SIZES['h1'],
            cls.FONT_SIZES['h2'], 
            cls.FONT_SIZES['h3'],
            cls.FONT_SIZES['h4']
        ]
        
        # Define colors for each heading level
        heading_colors = [
            cls.COLORS['h1_color'],   # Level 0 (H1)
            cls.COLORS['h2_color'],   # Level 1 (H2)
            cls.COLORS['h3_color'],   # Level 2 (H3)
            cls.COLORS['h4_color'],   # Level 3 (H4)
        ]
        
        font_size = font_sizes[min(level, len(font_sizes)-1)]
        if level >= len(font_sizes):
            font_size = max(10, cls.FONT_SIZES['h4'] - (level - 3))
        
        # Select color for this heading level
        if level < len(heading_colors):
            heading_color = heading_colors[level]
        else:
            heading_color = cls.COLORS['h5_color']  # Use H5+ color for deeper levels
        
        return ParagraphStyle(
            f'CustomHeading{level}',
            parent=base_styles['Normal'],  # Changed from 'Heading2' to avoid italic inheritance
            fontName=cls.FONTS['heading'],  # Explicitly set to 'Helvetica-Bold' (non-italic)
            fontSize=font_size,
            leading=font_size * 1.3,  # Set line height to 1.3x font size for proper spacing
            spaceAfter=cls.SPACING['heading_after'],
            spaceBefore=cls.SPACING['heading_before'],
            textColor=heading_color,  # Use level-specific color
            keepWithNext=1
        )
    
    @classmethod  
    def create_content_style(cls, base_styles, level=0):
        """Create content style with optional indentation"""
        indent = max(0, (level - 1) * cls.INDENTS['content_per_level'])
        
        return ParagraphStyle(
            f'CustomContent{level}',
            parent=base_styles['Normal'],
            fontName=cls.FONTS['body'],
            fontSize=cls.FONT_SIZES['body'],
            spaceAfter=cls.SPACING['paragraph_after'],
            alignment=TA_JUSTIFY,
            leftIndent=indent,
            rightIndent=0,
            textColor=cls.COLORS['text']
        )

    @classmethod
    def create_bullet_style(cls, base_styles, level=0):
        """Create bullet list item style with hanging indent"""
        from reportlab.pdfbase.pdfmetrics import stringWidth
        base_indent = max(0, (level - 1) * cls.INDENTS['content_per_level'])
        # Measure the exact rendered width of the bullet prefix so wrapped lines
        # align precisely with the text that follows the bullet.
        bullet_hang = stringWidth('•  ', cls.FONTS['body'], cls.FONT_SIZES['body'])

        return ParagraphStyle(
            f'BulletItem{level}',
            parent=base_styles['Normal'],
            fontName=cls.FONTS['body'],
            fontSize=cls.FONT_SIZES['body'],
            spaceAfter=3,
            alignment=TA_LEFT,
            leftIndent=base_indent + bullet_hang,
            firstLineIndent=-bullet_hang,
            rightIndent=0,
            textColor=cls.COLORS['text']
        )

    @classmethod
    def create_numbered_style(cls, base_styles, level=0):
        """Create numbered list item style with hanging indent"""
        from reportlab.pdfbase.pdfmetrics import stringWidth
        base_indent = max(0, (level - 1) * cls.INDENTS['content_per_level'])
        # Measure the exact rendered width of a single-digit number prefix so
        # wrapped lines align precisely with the text that follows the number.
        num_hang = stringWidth('1.  ', cls.FONTS['body'], cls.FONT_SIZES['body'])

        return ParagraphStyle(
            f'NumberedItem{level}',
            parent=base_styles['Normal'],
            fontName=cls.FONTS['body'],
            fontSize=cls.FONT_SIZES['body'],
            spaceAfter=3,
            alignment=TA_LEFT,
            leftIndent=base_indent + num_hang,
            firstLineIndent=-num_hang,
            rightIndent=0,
            textColor=cls.COLORS['text']
        )
    
    @classmethod
    def create_toc_style(cls, base_styles, level=0):
        """Create Table of Contents style"""
        if level == 0:
            # First level: bold text, no underline
            return ParagraphStyle(
                f'TOCLevel{level}',
                parent=base_styles['Normal'],
                fontName=cls.FONTS['heading'],
                fontSize=cls.FONT_SIZES['toc'],
                leftIndent=0,
                spaceAfter=cls.SPACING['toc_item'] + 2,
                textColor=cls.COLORS['heading'],
                keepWithNext=1
            )
        else:
            # Nested levels: regular body text
            return ParagraphStyle(
                f'TOCLevel{level}',
                parent=base_styles['Normal'],
                fontName=cls.FONTS['body'],
                fontSize=max(9, cls.FONT_SIZES['toc'] - (level * 0.5)),
                leftIndent=level * cls.INDENTS['toc_per_level'],
                spaceAfter=cls.SPACING['toc_item'],
                textColor=cls.COLORS['text']
            )
    
    @classmethod
    def create_toc_entry_with_leader(cls, title, page_num, level=0):
        """Create TOC entry with dotted leader to page number"""
        if level == 0:
            # First level: title with page number, underlined
            return f'<u>{title}</u><seq template="%(page)d" id="toc_page">{page_num}</seq>'
        else:
            # Nested levels: title with dotted leader to page number
            dots_needed = max(1, (60 - len(title) - len(str(page_num))) // 2)
            dots = '.' * dots_needed
            return f'{title} {dots} {page_num}'

# Alternative configurations for different use cases
class CorporateConfig(PDFConfig):
    """Corporate/formal document configuration"""
    COLORS = {
        'primary': colors.Color(0.0, 0.2, 0.4),      # Dark blue
        'secondary': colors.Color(0.3, 0.3, 0.3),    # Dark gray
        'accent': colors.Color(0.6, 0.1, 0.1),       # Dark red
        'text': colors.black,
        'heading': colors.Color(0.0, 0.2, 0.4),      # Same as primary
        'subheading': colors.Color(0.3, 0.3, 0.3),   # Same as secondary
        
        # Corporate heading level colors
        'h1_color': colors.Color(0.0, 0.2, 0.4),     # Dark blue - primary
        'h2_color': colors.Color(0.3, 0.3, 0.3),     # Dark gray - secondary
        'h3_color': colors.Color(0.6, 0.1, 0.1),     # Dark red - accent
        'h4_color': colors.Color(0.1, 0.1, 0.1),     # Very dark gray
        'h5_color': colors.Color(0.4, 0.4, 0.4),     # Medium gray
        
        'light_bg': colors.Color(0.95, 0.95, 0.95),
        'highlight': colors.Color(0.95, 0.95, 0.8),
        'border': colors.Color(0.8, 0.8, 0.8)
    }
    
    FONT_SIZES = {
        'title': 22,
        'subtitle': 11,
        'h1': 17,  # Increased to maintain hierarchy over H2
        'h2': 16,  # Increased for better prominence
        'h3': 12,
        'h4': 11,
        'body': 10,
        'caption': 8,
        'toc': 10
    }


class OrganizationConfig(PDFConfig):
    """Custom organization color palette configuration
    
    Example showing how to implement your organization's brand colors
    Replace these hex values with your actual brand colors
    """
    
    # Your Organization's Color Palette
    COLORS = {
        # Replace these hex values with your brand colors
        'primary': hex_to_color('#112e51'),      # e.g., '#1E3A8A'
        'secondary': hex_to_color('#FF5622'),  # e.g., '#059669'
        'accent': hex_to_color('#008392'),        # e.g., '#DC2626'
        
        # Functional colors
        'text': hex_to_color('#000000'),                     # Dark gray for readability
        'heading': hex_to_color('#112e51'),                  # Nearly black for headings
        'subheading': hex_to_color('#444444'),               # Medium gray

        # Organization heading level colors (customize these with your brand colors)
        'h1_color': hex_to_color('#112e51'),     # H1 color - primary brand
        'h2_color': hex_to_color('#FF5622'),     # H2 color - secondary brand  
        'h3_color': hex_to_color('#008392'),     # H3 color - accent brand
        'h4_color': hex_to_color('#444444'),     # H4 color - dark gray
        'h5_color': hex_to_color('#666666'),     # H5+ color - medium gray

        # Background colors
        'light_bg': hex_to_color('#F9FAFB'),                 # Very light gray
        'highlight': hex_to_color('#FEF3C7'),                # Yellow highlight
        'border': hex_to_color('#D1D5DB'),                   # Border gray
    }
    
    # Typography with brand colors
    FONTS = {
        'title': 'Helvetica-Bold',
        'heading': 'Helvetica-Bold', 
        'body': 'Times-Roman',
        'caption': 'Helvetica-Oblique',
        'code': 'Courier-Bold'  # Bold code for better visibility
    }


class AcademicConfig(PDFConfig):
    """Academic paper configuration"""
    FONT_SIZES = {
        'title': 20,
        'subtitle': 12,
        'h1': 17,  # Increased to maintain hierarchy over H2
        'h2': 16,  # Increased for better prominence
        'h3': 12,
        'h4': 11,
        'body': 12,  # Larger body text for readability
        'caption': 10,
        'toc': 11
    }
    
    SPACING = {
        'title_after': 40,
        'subtitle_after': 25,
        'heading_before': 12,
        'heading_after': 15,
        'paragraph_after': 15,  # More spacing between paragraphs
        'section_after': 20,
        'toc_item': 8
    }

class CompactConfig(PDFConfig):
    """Compact formatting for dense documents"""
    FONT_SIZES = {
        'title': 20,
        'subtitle': 10,
        'h1': 15,
        'h2': 15,  # Increased to 15 to match H1 for better hierarchy
        'h3': 11,
        'h4': 10,
        'body': 9,
        'caption': 8,
        'toc': 9
    }
    
    SPACING = {
        'title_after': 20,
        'subtitle_after': 15,
        'heading_before': 8,
        'heading_after': 8,
        'paragraph_after': 8,
        'section_after': 12,
        'toc_item': 4
    }
