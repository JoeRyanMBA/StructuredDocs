from flask import current_app
import re
import os
import base64
import mimetypes
import io
import json
import traceback
import tempfile
import shutil
from pathlib import Path
import requests as _http
from bs4 import BeautifulSoup
import mistune
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image, NextPageTemplate, Flowable
from reportlab.platypus.flowables import AnchorFlowable
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.platypus.frames import Frame
from reportlab.pdfgen import canvas
from backend.pdf_config import PDFConfig, CorporateConfig, AcademicConfig, CompactConfig, OrganizationConfig
from backend.utils.storage import resolve_local_storage_root
from .export_branding import get_export_branding_settings, resolve_brand_asset_path, NO_COVER_BACKGROUND_SENTINEL



def _color_hex(color) -> str:
    """Convert a ReportLab Color to a CSS hex string for use in Paragraph XML link tags."""
    try:
        r = int(color.red * 255)
        g = int(color.green * 255)
        b = int(color.blue * 255)
        return f'#{r:02x}{g:02x}{b:02x}'
    except Exception:
        return '#000000'


# ReportLab-safe text sanitization: strip unsupported tags and fix entities
def _pdf_sanitize_text(s: str) -> str:
    if not s:
        return ''
    # Normalize line endings and non-breaking spaces
    s = s.replace('\r\n', '\n').replace('\r', '\n').replace('\u00A0', ' ')
    # Remove soft hyphen characters which can break tag parsing
    try:
        s = s.replace('\u00AD', '')
    except Exception:
        pass
    # Remove script/style tags entirely
    s = re.sub(r'<\s*(script|style)[^>]*>.*?<\s*/\s*\1\s*>', '', s, flags=re.IGNORECASE|re.DOTALL)
    # Normalize <br> HTML tags to XHTML self-closing form required by ReportLab's XML parser
    s = re.sub(r'<br\s*/?>', '<br/>', s, flags=re.IGNORECASE)
    # Replace unsupported tags with their inner text (expanded list)
    # Note: ul/ol/li are intentionally excluded here — they are handled by
    # convert_markdown_to_pdf_paragraphs which converts them to markdown bullets/numbers.
    s = re.sub(
        r'</?(div|span|section|article|header|footer|aside|main'
        r'|table|thead|tbody|tfoot|tr|th|td|caption'
        r'|figure|figcaption|blockquote|hr)[^>]*>',
        '', s, flags=re.IGNORECASE
    )
    # Remove onclick/href/js URLs that ReportLab can't handle
    s = re.sub(r'href\s*=\s*"javascript:[^"]*"', '', s, flags=re.IGNORECASE)
    # Escape stray ampersands
    s = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#\d+;|#x[0-9A-Fa-f]+;)', '&amp;', s)
    # Fix common mis-nested bold/italic tags (e.g., <b><i>..</b></i> -> <b><i>..</i></b>)
    # Apply a few passes to catch nested occurrences
    for _ in range(2):
        s = re.sub(r'<b>\s*<i>(.*?)</b>\s*</i>', r'<b><i>\1</i></b>', s, flags=re.DOTALL | re.IGNORECASE)
        s = re.sub(r'<i>\s*<b>(.*?)</i>\s*</b>', r'<i><b>\1</b></i>', s, flags=re.DOTALL | re.IGNORECASE)
    # Remove Pandoc-style attribute blocks like {width=".." height=".."}
    s = re.sub(r'\{\s*(?:width|height|style|class)\s*=\s*"[^"]*"[^}]*\}', '', s)
    return s.strip()


def _format_inline_markdown_for_pdf(text: str) -> str:
    """Convert basic inline markdown syntax to ReportLab-compatible inline tags."""
    if not text:
        return ''
    formatted = str(text)
    formatted = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', formatted)
    formatted = re.sub(r'\*(.*?)\*', r'<i>\1</i>', formatted)
    formatted = re.sub(r'`(.*?)`', r'<font face="Courier">\1</font>', formatted)
    return formatted


def _resolve_local_image_path_for_pdf(src: str) -> str:
    """Resolve a web/relative image path to an absolute local file path for PDF embedding."""
    if not src:
        return ''

    source = src.strip()
    if not source:
        return ''

    # Absolute local filesystem path
    if os.path.isabs(source) and os.path.exists(source):
        return source

    # Non-local sources are handled elsewhere
    if source.startswith(('http://', 'https://', 'data:')):
        return ''

    if source.startswith('/images/'):
        rel_path = source[len('/images/'):]
    elif source.startswith('/static/images/'):
        rel_path = source[len('/static/images/'):]
    else:
        rel_path = source.lstrip('/')

    candidate_roots = []
    configured_root = (os.environ.get('IMAGE_STORAGE_ROOT') or '').strip()
    if configured_root:
        candidate_roots.append(configured_root)
    candidate_roots.append(resolve_local_storage_root())
    candidate_roots.append('/app/data/images')

    try:
        candidate_roots.append(os.path.join(current_app.config['STATIC_FOLDER'], 'images'))
    except Exception:
        pass

    try:
        root_dir = Path(__file__).resolve().parents[2]
        candidate_roots.extend([
            str(root_dir / 'frontend' / 'dist' / 'images'),
            str(root_dir / 'frontend' / 'public' / 'images'),
            str(root_dir / 'backend' / 'static' / 'images'),
        ])
    except Exception:
        pass

    for root in candidate_roots:
        if not root:
            continue
        candidate = os.path.join(root, rel_path)
        if os.path.exists(candidate):
            return candidate

    return ''


def _is_markdown_table_separator(line: str) -> bool:
    """Return True when *line* looks like a markdown table separator row."""
    if not line:
        return False
    candidate = line.strip()
    if '|' not in candidate:
        return False
    # Examples: | --- | :---: | ---: |
    return bool(re.match(r'^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$', candidate))


def _split_markdown_table_row(line: str):
    """Split a markdown table row into cell values."""
    if line is None:
        return []
    row = line.strip()
    if row.startswith('|'):
        row = row[1:]
    if row.endswith('|'):
        row = row[:-1]
    cells = [c.strip().replace('\\|', '|') for c in re.split(r'(?<!\\)\|', row)]
    return cells


def _consume_markdown_table(lines, start_index):
    """Parse a markdown table block from *lines* starting at *start_index*.

    Returns (table_rows, next_index).
    table_rows is None when no table starts at start_index.
    """
    if start_index + 1 >= len(lines):
        return None, start_index

    header_line = lines[start_index].strip()
    separator_line = lines[start_index + 1].strip()
    if '|' not in header_line or not _is_markdown_table_separator(separator_line):
        return None, start_index

    header_cells = _split_markdown_table_row(header_line)
    if not header_cells:
        return None, start_index

    table_rows = [header_cells]
    i = start_index + 2
    while i < len(lines):
        row_line = lines[i]
        stripped = row_line.strip()
        if not stripped or '|' not in stripped:
            break
        if _is_markdown_table_separator(stripped):
            i += 1
            continue
        row_cells = _split_markdown_table_row(stripped)
        if not row_cells:
            break
        # Normalize row width to match header width
        if len(row_cells) < len(header_cells):
            row_cells += [''] * (len(header_cells) - len(row_cells))
        elif len(row_cells) > len(header_cells):
            row_cells = row_cells[:len(header_cells)]
        table_rows.append(row_cells)
        i += 1

    return table_rows, i


class BackgroundImageDocTemplate(BaseDocTemplate):
    """Custom document template that supports background images, headers and footers on pages"""
    
    def __init__(self, filename, background_image_path=None, publication=None, branding=None, **kwargs):
        BaseDocTemplate.__init__(self, filename, **kwargs)
        self.background_image_path = background_image_path
        self.publication = publication
        self.branding = branding or {}
        self.brand_name = self.branding.get('brand_name', 'StructuredDocs')
        self.page_count = 0  # Track page numbers across templates
        self.toc_start_page = 2  # TOC starts at page 2 (roman numerals)
        self.content_start_page = 1  # Content pages start after TOC
        
        # Position content much closer to header
        content_top_margin = 0.005 * inch  # Ultra-minimal top margin - reduced by ~24pts
        footer_space = 0.8 * inch  # Balanced footer space to prevent overlap without excessive gap
        content_height = self.height - content_top_margin - footer_space
        # Calculate Y position from bottom to position content from top
        content_y_from_bottom = self.bottomMargin + footer_space
        
        # Create frame for content with header and footer space reserved
        frame = Frame(
            self.leftMargin, content_y_from_bottom,
            self.width, content_height,
            id='normal'
        )
        
        # Create separate frame for title page with standard spacing
        title_content_top = 0.05 * inch  # Normal spacing for title page
        title_footer_space = 1.1 * inch  # Normal footer space for title page
        title_content_height = self.height - title_content_top - title_footer_space
        title_content_y = self.bottomMargin + title_footer_space
        
        title_frame = Frame(
            self.leftMargin, title_content_y,
            self.width, title_content_height,
            id='title'
        )

        # Create page templates
        title_template = PageTemplate(
            id='title_page',
            frames=[title_frame],
            onPage=self.add_title_page_with_footer
        )
        
        toc_template = PageTemplate(
            id='toc_page',
            frames=[frame],
            onPage=self.add_toc_page_with_footer
        )
        
        normal_template = PageTemplate(
            id='normal_page', 
            frames=[frame],
            onPage=self.add_normal_page_with_footer
        )
        
        self.addPageTemplates([title_template, toc_template, normal_template])
    
    def add_title_page_with_footer(self, canvas, doc):
        """Add background image and footer to title page"""
        # Add background image
        if self.background_image_path and os.path.exists(self.background_image_path):
            try:
                canvas.saveState()
                page_width, page_height = self.pagesize
                canvas.drawImage(
                    self.background_image_path,
                    0, 0,
                    width=page_width,
                    height=page_height,
                    preserveAspectRatio=True,
                    mask='auto'
                )
                canvas.restoreState()
            except Exception as e:
                current_app.logger.debug(f"Warning: Could not add background image: {e}")
        
        # Add title page footer
        self.add_title_footer(canvas, doc)
    
    def add_toc_page_with_footer(self, canvas, doc):
        """Add header and footer to TOC pages"""
        self.add_header(canvas, doc)
        self.add_toc_footer(canvas, doc)
    
    def add_normal_page_with_footer(self, canvas, doc):
        """Add header and footer to normal content pages"""
        self.add_header(canvas, doc)
        self.add_content_footer(canvas, doc)
    
    def add_title_footer(self, canvas, doc):
        """Add footer for title page with Organization logo"""
        try:
            canvas.saveState()
            page_width, page_height = self.pagesize
            
            # Logo positioning - 0.25" from left and bottom edges of page
            logo_x = 0.25 * inch  # 0.25" from left edge of page
            logo_y = 0.25 * inch  # 0.25" from bottom edge of page
            logo_width = 2.0 * inch  # Title page logo should be 2" wide
            logo_height = logo_width / 1.77  # Maintain proper 1.77:1 aspect ratio
            
            # Add Organization logo (positioned at left edge)
            title_logo_path = resolve_brand_asset_path(
                self.branding.get('pdf_title_logo', ''),
                'Title_Page_Logo.png'
            )
            if os.path.exists(title_logo_path):
                try:
                    canvas.drawImage(
                        title_logo_path,
                        logo_x, logo_y,
                        width=logo_width,
                        height=logo_height,
                        preserveAspectRatio=True,
                        mask='auto'  # Enable transparency support
                    )
                except:
                    current_app.logger.debug("Warning: Could not load title page logo")
            
            # Set font for footer text
            canvas.setFont("Helvetica", 10)
            
            # Footer text positioning - move up one row to align better with visual top of logo
            footer_text_y = logo_y + logo_height - 32  # Move text down about 14 more points
            right_margin_x = page_width - 0.5 * inch  # Use 0.5" right margin
            
            # Top row: Organization name (centered) and form number (right)
            canvas.drawCentredString(page_width / 2, footer_text_y, self.brand_name)
            
            if self.publication is not None:
                form_number = getattr(self.publication, 'form_number', f"xx.{self.publication.id:04d}")
            else:
                form_number = "xx.0000"
            form_text = f"Form: {form_number}"
            text_width = canvas.stringWidth(form_text, "Helvetica", 10)
            canvas.drawString(right_margin_x - text_width, footer_text_y, form_text)
            
            # Bottom row: "Revised:" with date - right-aligned under form number
            revised_text = f"Revised: {datetime.now().strftime('%m/%d/%Y')}"
            revised_text_width = canvas.stringWidth(revised_text, "Helvetica", 10)
            canvas.drawString(right_margin_x - revised_text_width, footer_text_y - 15, revised_text)
            
            canvas.restoreState()
        except Exception as e:
            current_app.logger.debug(f"Warning: Could not add title footer: {e}")
    
    def add_toc_footer(self, canvas, doc):
        """Add footer for TOC pages with horizontal line"""
        try:
            canvas.saveState()
            page_width, page_height = self.pagesize
            
            # Logo positioning - align with left margin and move down 0.5" to align with top of logo
            logo_x = self.leftMargin - 0.25 * inch  # Move left 0.25" from margin
            logo_y = 0.25 * inch - 6  # Position 0.25" from bottom edge, moved down 6pts
            logo_width = 1.5 * inch  # Footer logo should be 1.5" wide
            logo_height = logo_width / 1.77  # Maintain proper 1.77:1 aspect ratio
            
            # Footer text positioning - align with top of logo
            footer_text_y = logo_y + logo_height - 24  # Match standard page positioning 

            # Horizontal line positioning - directly above the text (no gap)
            line_y = footer_text_y + 18  # Position line 18pt above text for more space   
            canvas.setStrokeColor(colors.black)
            canvas.setLineWidth(0.5)
            canvas.line(self.leftMargin, line_y, page_width - self.rightMargin, line_y)
            
            # Add Organization logo
            footer_logo_path = resolve_brand_asset_path(
                self.branding.get('pdf_footer_logo', ''),
                'Footer_Logo.png'
            )
            if os.path.exists(footer_logo_path):
                try:
                    canvas.drawImage(
                        footer_logo_path,
                        logo_x, logo_y,
                        width=logo_width,
                        height=logo_height,
                        preserveAspectRatio=True,
                        mask='auto'  # Enable transparency support
                    )
                except:
                    current_app.logger.debug("Warning: Could not load footer logo")
            
            # Set font for footer text
            canvas.setFont("Helvetica", 9)
            footer_text_y = logo_y + logo_height - 24  # Match standard page positioning
            
            # Top row: Organization name (centered) and revision date (right)
            canvas.drawCentredString(page_width / 2, footer_text_y, self.brand_name)
            
            # Removed form_number, using revision date instead
            revised_text = f"Revised: {datetime.now().strftime('%m/%d/%y')}"
            right_margin_x = page_width - self.rightMargin
            text_width = canvas.stringWidth(revised_text, "Helvetica", 9)
            canvas.drawString(right_margin_x - text_width, footer_text_y, revised_text)
            
            # Bottom row: Page number in roman numerals (starts at ii) - right-aligned
            roman_page = self.int_to_roman(doc.page)
            page_text = f"Page {roman_page}"
            page_text_width = canvas.stringWidth(page_text, "Helvetica", 9)
            canvas.drawString(right_margin_x - page_text_width, footer_text_y - 12, page_text)
            
            canvas.restoreState()
        except Exception as e:
            current_app.logger.debug(f"Warning: Could not add TOC footer: {e}")

    def add_content_footer(self, canvas, doc):
        """Add footer for content pages with horizontal line"""
        try:
            canvas.saveState()
            page_width, page_height = self.pagesize
            
            # Logo positioning - align with left margin and move down 0.5" to align with top of logo
            logo_x = self.leftMargin - 0.25 * inch  # Move left 0.25" from margin
            logo_y = 0.25 * inch - 6  # Position 0.25" from bottom edge, moved down 6pts
            logo_width = 1.5 * inch  # Footer logo should be 1.5" wide
            logo_height = logo_width / 1.77  # Maintain proper 1.77:1 aspect ratio
            
            # Footer text positioning - align with top of logo
            footer_text_y = logo_y + logo_height - 24  # Move down 24 pts from original
            
            # Horizontal line positioning - directly above the text (no gap)
            line_y = footer_text_y + 18  # Position line 18pt above text for more space
            canvas.setStrokeColor(colors.black)
            canvas.setLineWidth(0.5)
            canvas.line(self.leftMargin, line_y, page_width - self.rightMargin, line_y)
            canvas.line(self.leftMargin, line_y, page_width - self.rightMargin, line_y)
            
            # Add organization logo
            footer_logo_path = resolve_brand_asset_path(
                self.branding.get('pdf_footer_logo', ''),
                'Footer_Logo.png'
            )
            if os.path.exists(footer_logo_path):
                try:
                    canvas.drawImage(
                        footer_logo_path,
                        logo_x, logo_y,
                        width=logo_width,
                        height=logo_height,
                        preserveAspectRatio=True,
                        mask='auto'  # Enable transparency support
                    )
                except:
                    current_app.logger.debug("Warning: Could not load footer logo")
            
            # Set font for footer text
            canvas.setFont("Helvetica", 9)
            
            # Footer text positioning - below the horizontal line
            footer_text_y = logo_y + logo_height - 24  # Move down 24 pts from original
            
            # Top row: Organization name (centered) and revision date (right)
            canvas.drawCentredString(page_width / 2, footer_text_y, self.brand_name)
            
            # Removed form_number, using revision date instead
            revised_text = f"Revised: {datetime.now().strftime('%m/%d/%y')}"
            right_margin_x = page_width - self.rightMargin
            text_width = canvas.stringWidth(revised_text, "Helvetica", 9)
            canvas.drawString(right_margin_x - text_width, footer_text_y, revised_text)
            
            # Bottom row: Page number in Arabic numerals - right-aligned
            page_text = f"Page {doc.page}"
            page_text_width = canvas.stringWidth(page_text, "Helvetica", 9)
            canvas.drawString(right_margin_x - page_text_width, footer_text_y - 12, page_text)
            
            canvas.restoreState()
        except Exception as e:
            current_app.logger.debug(f"Warning: Could not add content footer: {e}")
            current_app.logger.debug(f"Warning: Could not add content footer: {e}")
    
    def int_to_roman(self, num):
        """Convert integer to roman numerals"""
        val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
        syms = ["m", "cm", "d", "cd", "c", "xc", "l", "xl", "x", "ix", "v", "iv", "i"]
        roman_num = ''
        i = 0
        while num > 0:
            for _ in range(num // val[i]):
                roman_num += syms[i]
                num -= val[i]
            i += 1
        return roman_num
    
    def add_header(self, canvas, doc):
        """Add header with publication info and horizontal line"""
        if not self.publication:
            return
            
        try:
            # Save canvas state
            canvas.saveState()
            
            # Get page dimensions
            page_width, page_height = self.pagesize
            
            # Header positioning (right-aligned at right margin) - within the page bounds
            right_margin_x = page_width - self.rightMargin
            header_y = page_height - 0.5 * inch  # 0.5 inches from the top of the page
            
            # Set font for header text (0.9rem ≈ 9pt)
            canvas.setFont("Helvetica", 9)
            
            # Publication ID + Title (single line header)
            form_number = getattr(self.publication, 'form_number', f"PUB-{self.publication.id}")
            collection_name = self.publication.title or "Unknown Collection"
            header_line = f"{form_number}, {collection_name}"
            text_width = canvas.stringWidth(header_line, "Helvetica", 9)
            canvas.drawString(right_margin_x - text_width, header_y, header_line)
            
            # Horizontal line from left margin to right margin (closer to text)
            line_y = header_y - 4  # Reduced space - closer to the text
            canvas.setStrokeColor(colors.black)
            canvas.setLineWidth(0.5)
            canvas.line(self.leftMargin, line_y, right_margin_x, line_y)
            
            # Restore canvas state
            canvas.restoreState()
            
        except Exception as e:
            current_app.logger.debug(f"Warning: Could not add header: {e}")


class HeaderDocTemplate(BaseDocTemplate):
    """Document template with headers and footers for PDF documents without background images"""
    
    def __init__(self, filename, publication=None, branding=None, **kwargs):
        BaseDocTemplate.__init__(self, filename, **kwargs)
        self.publication = publication
        self.branding = branding or {}
        self.brand_name = self.branding.get('brand_name', 'StructuredDocs')
        self.page_count = 0  # Track page numbers across templates
        self.toc_start_page = 2  # TOC starts at page 2 (roman numerals)
        self.content_start_page = 1  # Content pages start after TOC
        
        # Position content much closer to header
        content_top_margin = 0.005 * inch  # Ultra-minimal top margin - reduced by ~24pts
        footer_space = 0.8 * inch  # Balanced footer space to prevent overlap without excessive gap
        content_height = self.height - content_top_margin - footer_space
        # Calculate Y position from bottom to position content from top
        content_y_from_bottom = self.bottomMargin + footer_space
        
        # Create frame for content with header and footer space reserved
        frame = Frame(
            self.leftMargin, content_y_from_bottom,
            self.width, content_height,
            id='normal'
        )
        
        # Create separate frame for title page with standard spacing
        title_content_top = 0.05 * inch  # Normal spacing for title page
        title_footer_space = 1.1 * inch  # Normal footer space for title page
        title_content_height = self.height - title_content_top - title_footer_space
        title_content_y = self.bottomMargin + title_footer_space
        
        title_frame = Frame(
            self.leftMargin, title_content_y,
            self.width, title_content_height,
            id='title'
        )

        # Create page templates
        title_template = PageTemplate(
            id='title_page',
            frames=[title_frame],
            onPage=self.add_title_page_with_footer
        )
        
        toc_template = PageTemplate(
            id='toc_page',
            frames=[frame],
            onPage=self.add_toc_page_with_footer
        )
        
        normal_template = PageTemplate(
            id='normal_page',
            frames=[frame],
            onPage=self.add_normal_page_with_footer
        )
        
        self.addPageTemplates([title_template, toc_template, normal_template])
    
    def add_title_page_with_footer(self, canvas, doc):
        """Add footer to title page (no header)"""
        self.add_title_footer(canvas, doc)
    
    def add_toc_page_with_footer(self, canvas, doc):
        """Add header and footer to TOC pages"""
        self.add_header(canvas, doc)
        self.add_toc_footer(canvas, doc)
    
    def add_normal_page_with_footer(self, canvas, doc):
        """Add header and footer to normal content pages"""
        self.add_header(canvas, doc)
        self.add_content_footer(canvas, doc)
    
    def add_title_footer(self, canvas, doc):
        """Add footer for title page with Organization logo"""
        try:
            canvas.saveState()
            page_width, page_height = self.pagesize
            
            # Logo positioning - 0.25" from left and bottom edges of page
            logo_x = 0.25 * inch  # 0.25" from left edge of page
            logo_y = 0.25 * inch  # 0.25" from bottom edge of page
            logo_width = 2.0 * inch  # Title page logo should be 2" wide
            logo_height = logo_width / 1.77  # Maintain proper 1.77:1 aspect ratio
            
            # Add Organization logo (positioned at left edge)
            title_logo_path = resolve_brand_asset_path(
                self.branding.get('pdf_title_logo', ''),
                'Title_Page_Logo.png'
            )
            if os.path.exists(title_logo_path):
                try:
                    canvas.drawImage(
                        title_logo_path,
                        logo_x, logo_y,
                        width=logo_width,
                        height=logo_height,
                        preserveAspectRatio=True,
                        mask='auto'  # Enable transparency support
                    )
                except:
                    current_app.logger.debug("Warning: Could not load title page logo")
            
            # Set font for footer text
            canvas.setFont("Helvetica", 9)
            
            # Footer text positioning - move up one row to align better with visual top of logo
            footer_text_y = logo_y + logo_height - 26  # Move text down about 14 more points
            right_margin_x = page_width - 0.5 * inch  # Use 0.5" right margin
            
            # Top row: "StructuredDocs" (centered) and revision date (right)
            canvas.drawCentredString(page_width / 2, footer_text_y, self.brand_name)
            
            form_number = getattr(self.publication, 'form_number', f"xx.{self.publication.id if self.publication else '0000':04d}")
            form_text = f"Form: {form_number}"
            text_width = canvas.stringWidth(form_text, "Helvetica", 10)
            canvas.drawString(right_margin_x - text_width, footer_text_y, form_text)
            
            # Bottom row: "Revised:" with date - right-aligned under form number
            revised_text = f"Revised: {datetime.now().strftime('%m/%d/%Y')}"
            revised_text_width = canvas.stringWidth(revised_text, "Helvetica", 10)
            canvas.drawString(right_margin_x - revised_text_width, footer_text_y - 15, revised_text)
            
            canvas.restoreState()
        except Exception as e:
            current_app.logger.debug(f"Warning: Could not add title footer: {e}")
    
    def add_toc_footer(self, canvas, doc):
        """Add footer for TOC pages with horizontal line"""
        try:
            canvas.saveState()
            page_width, page_height = self.pagesize
            # Logo positioning - align with left margin and move down 0.5" to align with top of logo
            logo_x = self.leftMargin - 0.25 * inch  # Move left 0.25" from margin
            logo_y = 0.25 * inch - 6  # Position 0.25" from bottom edge, moved down 6pts
            logo_width = 1.5 * inch  # Footer logo should be 1.5" wide
            logo_height = logo_width / 1.77  # Maintain proper 1.77:1 aspect ratio
            
            # Footer text positioning - align with top of logo
            footer_text_y = logo_y + logo_height  # Align with top of logo
            
            # Horizontal line positioning - directly above the text (no gap)
            line_y = footer_text_y + 18  # Position line 18pt above text for more space
            canvas.setStrokeColor(colors.black)
            canvas.setLineWidth(0.5)
            canvas.line(self.leftMargin, line_y, page_width - self.rightMargin, line_y)
            canvas.setLineWidth(0.5)
            canvas.line(self.leftMargin, line_y, page_width - self.rightMargin, line_y)
            
            # Add Organization logo
            footer_logo_path = resolve_brand_asset_path(
                self.branding.get('pdf_footer_logo', ''),
                'Footer_Logo.png'
            )
            if os.path.exists(footer_logo_path):
                try:
                    canvas.drawImage(
                        footer_logo_path,
                        logo_x, logo_y,
                        width=logo_width,
                        height=logo_height,
                        preserveAspectRatio=True,
                        mask='auto'  # Enable transparency support
                    )
                except:
                    current_app.logger.debug("Warning: Could not load footer logo")
            
            # Set font for footer text
            canvas.setFont("Helvetica", 9)
            
            # Footer text positioning - below the horizontal line
            footer_text_y = logo_y + logo_height - 24  # Match standard page positioning
            
            # Top row: "StructuredDocs" (centered) and revision date (right)
            canvas.drawCentredString(page_width / 2, footer_text_y, self.brand_name)
            
            # Removed form_number, using revision date instead
            revised_text = f"Revised: {datetime.now().strftime('%m/%d/%y')}"
            right_margin_x = page_width - self.rightMargin
            text_width = canvas.stringWidth(revised_text, "Helvetica", 9)
            canvas.drawString(right_margin_x - text_width, footer_text_y, revised_text)
            
            # Bottom row: Page number in roman numerals (starts at ii) - right-aligned
            roman_page = self.int_to_roman(doc.page)
            page_text = f"Page {roman_page}"
            page_text_width = canvas.stringWidth(page_text, "Helvetica", 9)
            canvas.drawString(right_margin_x - page_text_width, footer_text_y - 12, page_text)
            
            canvas.restoreState()
        except Exception as e:
            current_app.logger.debug(f"Warning: Could not add TOC footer: {e}")

    def add_content_footer(self, canvas, doc):
        """Add footer for content pages with horizontal line"""
        try:
            canvas.saveState()
            page_width, page_height = self.pagesize
            # Logo positioning - align with left margin and move down 0.5" to align with top of logo
            logo_x = self.leftMargin - 0.25 * inch  # Move left 0.25" from margin
            logo_y = 0.25 * inch - 6  # Position 0.25" from bottom edge, moved down 6pts
            logo_width = 1.5 * inch  # Footer logo should be 1.5" wide
            logo_height = logo_width / 1.77  # Maintain proper 1.77:1 aspect ratio
            
            # Footer text positioning - align with top of logo
            footer_text_y = logo_y + logo_height - 24  # Move down 24 pts from original
            
            # Horizontal line positioning - directly above the text (no gap)
            line_y = footer_text_y + 18  # Position line 18pt above text for more space
            canvas.setStrokeColor(colors.black)
            canvas.setLineWidth(0.5)
            canvas.line(self.leftMargin, line_y, page_width - self.rightMargin, line_y)
            canvas.setLineWidth(0.5)
            canvas.line(self.leftMargin, line_y, page_width - self.rightMargin, line_y)
            
            # Add Organization logo
            footer_logo_path = resolve_brand_asset_path(
                self.branding.get('pdf_footer_logo', ''),
                'Footer_Logo.png'
            )
            if os.path.exists(footer_logo_path):
                try:
                    canvas.drawImage(
                        footer_logo_path,
                        logo_x, logo_y,
                        width=logo_width,
                        height=logo_height,
                        preserveAspectRatio=True,
                        mask='auto'  # Enable transparency support
                    )
                except:
                    current_app.logger.debug("Warning: Could not load footer logo")
            
            # Set font for footer text
            canvas.setFont("Helvetica", 9)
            
            # Footer text positioning - below the horizontal line
            footer_text_y = logo_y + logo_height - 24  # Move down 24 pts from original
            
            # Top row: "StructuredDocs" (centered) and revision date (right)
            canvas.drawCentredString(page_width / 2, footer_text_y, self.brand_name)
            
            # Removed form_number, using revision date instead
            revised_text = f"Revised: {datetime.now().strftime('%m/%d/%y')}"
            right_margin_x = page_width - self.rightMargin
            text_width = canvas.stringWidth(revised_text, "Helvetica", 9)
            canvas.drawString(right_margin_x - text_width, footer_text_y, revised_text)
            
            # Bottom row: Page number in Arabic numerals - right-aligned
            page_text = f"Page {doc.page}"
            page_text_width = canvas.stringWidth(page_text, "Helvetica", 9)
            canvas.drawString(right_margin_x - page_text_width, footer_text_y - 12, page_text)
            
            canvas.restoreState()
        except Exception as e:
            current_app.logger.debug(f"Warning: Could not add content footer: {e}")
            current_app.logger.debug(f"Warning: Could not add content footer: {e}")
    
    def int_to_roman(self, num):
        """Convert integer to roman numerals"""
        val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
        syms = ["m", "cm", "d", "cd", "c", "xc", "l", "xl", "x", "ix", "v", "iv", "i"]
        roman_num = ''
        i = 0
        while num > 0:
            for _ in range(num // val[i]):
                roman_num += syms[i]
                num -= val[i]
            i += 1
        return roman_num
    
    def add_header(self, canvas, doc):
        """Add header with publication info and horizontal line"""
        current_app.logger.debug("DEBUG: HeaderDocTemplate add_header called")
        if not self.publication:
            current_app.logger.debug("DEBUG: No publication object")
            return
            
        try:
            current_app.logger.debug(f"DEBUG: Adding header for publication: {self.publication.title}")
            # Save canvas state
            canvas.saveState()
            
            # Get page dimensions
            page_width, page_height = self.pagesize
            
            # Header positioning (right-aligned at right margin) - within the page bounds
            right_margin_x = page_width - self.rightMargin
            header_y = page_height - 0.5 * inch  # 0.5 inches from the top of the page
            
            # Set font for header text (0.9rem ≈ 9pt)
            canvas.setFont("Helvetica", 9)
            
            # Publication ID + Title (single line header)
            form_number = getattr(self.publication, 'form_number', f"PUB-{self.publication.id}")
            collection_name = self.publication.title or "Unknown Collection"
            header_line = f"{form_number}, {collection_name}"
            text_width = canvas.stringWidth(header_line, "Helvetica", 9)
            canvas.drawString(right_margin_x - text_width, header_y, header_line)
            
            # Horizontal line from left margin to right margin (closer to text)
            line_y = header_y - 4  # Reduced space - closer to the text
            canvas.setStrokeColor(colors.black)
            canvas.setLineWidth(0.5)
            canvas.line(self.leftMargin, line_y, right_margin_x, line_y)
            
            # Restore canvas state
            canvas.restoreState()
            current_app.logger.debug("DEBUG: Header drawing completed successfully")
            
        except Exception as e:
            current_app.logger.debug(f"WARNING: Could not add header: {e}")
            import traceback
            traceback.print_exc()


# Pass strict_slashes here so both /api/publications and /api/publications/ match

def generate_pdf(publication, tree, config_type='default', background_image_path=None):
    """Generate PDF document from publication tree with configurable formatting and optional background image"""
    _pdf_temp_dir = tempfile.mkdtemp(prefix='sd_pdf_imgs_')

    # Ensure config_type is always defined
    if not config_type:
        config_type = 'default'

    branding = get_export_branding_settings()

    # Select configuration based on type
    if config_type == 'corporate':
        config = CorporateConfig
    elif config_type == 'academic':
        config = AcademicConfig
    elif config_type == 'compact':
        config = CompactConfig
    elif config_type == 'organization':
        config = OrganizationConfig
    else:
        config = PDFConfig

    # If no background image is specified, use the default SC Cover Background.png
    if not background_image_path:
        cover_setting = (branding.get('pdf_cover_background', '') or '').strip()
        if cover_setting == NO_COVER_BACKGROUND_SENTINEL:
            current_app.logger.debug("DEBUG: Cover background disabled by admin setting")
        else:
            default_bg_path = resolve_brand_asset_path(
                cover_setting,
                'SC Cover Background.png'
            )
            if default_bg_path and os.path.exists(default_bg_path):
                background_image_path = default_bg_path
                current_app.logger.debug(f"DEBUG: Using default background image: {background_image_path}")

    def _make_doc(buf):
        """Create a fresh doc template writing to the given buffer."""
        if background_image_path and os.path.exists(background_image_path):
            current_app.logger.debug("DEBUG: Using BackgroundImageDocTemplate")
            return BackgroundImageDocTemplate(
                buf,
                background_image_path=background_image_path,
                publication=publication,
                branding=branding,
                pagesize=config.PAGE_SIZE,
                rightMargin=config.MARGINS['right'],
                leftMargin=config.MARGINS['left'],
                topMargin=config.MARGINS['top'],
                bottomMargin=config.MARGINS['bottom']
            )
        else:
            current_app.logger.debug("DEBUG: Using HeaderDocTemplate")
            return HeaderDocTemplate(
                buf,
                publication=publication,
                branding=branding,
                pagesize=config.PAGE_SIZE,
                rightMargin=config.MARGINS['right'],
                leftMargin=config.MARGINS['left'],
                topMargin=config.MARGINS['top'],
                bottomMargin=config.MARGINS['bottom']
            )

    base_styles = config.get_base_styles()

    def _make_story(anchor_pages):
        """Build and return the complete story list.

        anchor_pages: dict mapping anchor_id → actual page number collected from a
        prior dry-run build.  Pass an empty dict on the first (measurement) pass.
        """
        story = []
    
        story.append(NextPageTemplate('title_page'))
        # Create styles using configuration
        title_style = config.create_title_style(base_styles)
        subtitle_style = config.create_subtitle_style(base_styles)
    
        # Title page content - move title down about 1" and align to right margin
        story.append(Spacer(1, 84))  # Move down ~1" (72pt)
    
        if background_image_path and os.path.exists(background_image_path):
            # For background image docs, use white text for visibility on blue background
            enhanced_title_style = ParagraphStyle(
                'EnhancedTitle',
                parent=title_style,
                textColor=colors.white,  # White text for visibility on blue background
                fontSize=title_style.fontSize + 4,  # Make title larger
                leading=title_style.fontSize + 8,
                alignment=TA_RIGHT,  # Right-align title
                leftIndent=0,  # No left indent for full right alignment
                rightIndent=-0.5 * inch,  # Position 0.5" from page edge (not margin)
            )
            enhanced_subtitle_style = ParagraphStyle(
                'EnhancedSubtitle',
                parent=subtitle_style,
                textColor=colors.white,  # White text for visibility on blue background
                fontSize=subtitle_style.fontSize + 3,
                alignment=TA_RIGHT,  # Right-align subtitle
                leftIndent=0,  # No left indent for full right alignment
                rightIndent=-0.5 * inch,  # Position 0.5" from page edge (not margin)
            )
            story.append(Paragraph(publication.title, enhanced_title_style))
            if publication.description:
                story.append(Paragraph(publication.description, enhanced_subtitle_style))
        else:
            # Regular title page without background - also right-aligned
            enhanced_title_style = ParagraphStyle(
                'EnhancedTitle',
                parent=title_style,
                alignment=TA_RIGHT,  # Right-align title
                leftIndent=0,  # No left indent for full right alignment
                rightIndent=-0.5 * inch,  # Position 0.5" from page edge (not margin)
            )
            enhanced_subtitle_style = ParagraphStyle(
                'EnhancedSubtitle',
                parent=subtitle_style,
                alignment=TA_RIGHT,  # Right-align subtitle
                leftIndent=0,  # No left indent for full right alignment
                rightIndent=-0.5 * inch,  # Position 0.5" from page edge (not margin)
            )
            story.append(Paragraph(publication.title, enhanced_title_style))
            if publication.description:
                story.append(Paragraph(publication.description, enhanced_subtitle_style))
    
        # Page break to TOC (switches to TOC page template)
        story.append(NextPageTemplate('toc_page'))
        story.append(PageBreak())
    
        # Table of contents
        # Create TOC heading with forced left alignment to overcome any ReportLab frame margins
        page_width, page_height = config.PAGE_SIZE
        total_margins = config.MARGINS['left'] + config.MARGINS['right']
        usable_width = page_width - total_margins
    
        # Create TOC heading aligned exactly to the 1-inch margin (same as TOC entries)
        toc_heading_style = ParagraphStyle(
            'TOCHeading',
            fontName=config.FONTS['heading'],
            fontSize=config.FONT_SIZES['h1'],
            textColor=config.COLORS['heading'],
            leftIndent=-6,  # Compensate for ReportLab's apparent 6pt default offset
            rightIndent=0,
            firstLineIndent=0,
            spaceBefore=0,
            spaceAfter=12,
            alignment=TA_LEFT,
            bulletIndent=0,
            listIndent=0
        )
        story.append(Paragraph("Table of Contents", toc_heading_style))
        story.append(Spacer(1, 12))
    
        # Build TOC with perfect alignment using consistent table approach
        def add_toc_entries(nodes, level=0, page_counter={'value': 1}):
            # Calculate page dimensions once for all entries
            page_width, page_height = config.PAGE_SIZE
            total_margins = config.MARGINS['left'] + config.MARGINS['right']
            usable_width = page_width - total_margins
            page_num_width = 50  # Fixed width for page numbers
            title_width = usable_width - page_num_width  # Remaining width for titles
        
            for node in nodes:
                anchor_id = f'node_{node["id"]}'
                # Use actual page number from dry-run build; fall back to rough estimate
                estimated = page_counter['value']
                page_counter['value'] += max(1, len(node.get('content', '')) // 2000)
                page_num = anchor_pages.get(anchor_id, estimated)
            
                title_text = node['title']
                font_size = config.FONT_SIZES['toc'] if level == 0 else max(9, config.FONT_SIZES['toc'] - (level * 0.5))
            
                if level == 0:
                    # Level 0: bold heading style, linked title and linked page number
                    title_style = ParagraphStyle(
                        'TOCTitle0',
                        fontName=config.FONTS['heading'],
                        fontSize=config.FONT_SIZES['toc'],
                        textColor=config.COLORS['heading'],
                        alignment=TA_LEFT,
                        leftIndent=0,
                        spaceAfter=0,
                        spaceBefore=0,
                        leading=config.FONT_SIZES['toc'] + 4,
                    )
                    page_style = ParagraphStyle(
                        'TOCPage0',
                        fontName=config.FONTS['body'],
                        fontSize=config.FONT_SIZES['toc'],
                        textColor=config.COLORS['heading'],
                        alignment=TA_RIGHT,
                        spaceAfter=0,
                        spaceBefore=0,
                        leading=config.FONT_SIZES['toc'] + 4,
                    )
                    title_para = Paragraph(f'<link href="#{anchor_id}" color="{_color_hex(config.COLORS["heading"])}">{title_text}</link>', title_style)
                    page_para = Paragraph(f'<link href="#{anchor_id}" color="{_color_hex(config.COLORS["heading"])}">{page_num}</link>', page_style)
                    toc_data = [[title_para, page_para]]
                
                    # Create table with proper margin alignment
                    toc_table = Table(toc_data, colWidths=[title_width, page_num_width])
                    toc_table.setStyle(TableStyle([
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                        ('TOPPADDING', (0, 0), (-1, -1), 2),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ]))
                
                else:
                    # Nested levels: indented entries with consistent right alignment
                    indent_width = level * config.INDENTS['toc_per_level']
                
                    title_style = ParagraphStyle(
                        f'TOCTitle{level}',
                        fontName=config.FONTS['body'],
                        fontSize=font_size,
                        textColor=config.COLORS['text'],
                        alignment=TA_LEFT,
                        leftIndent=indent_width,
                        spaceAfter=0,
                        spaceBefore=0,
                        leading=font_size + 4,
                    )
                    page_style = ParagraphStyle(
                        f'TOCPage{level}',
                        fontName=config.FONTS['body'],
                        fontSize=font_size,
                        textColor=config.COLORS['text'],
                        alignment=TA_RIGHT,
                        spaceAfter=0,
                        spaceBefore=0,
                        leading=font_size + 4,
                    )
                    link_color = _color_hex(config.COLORS['text'])
                    title_para = Paragraph(f'<link href="#{anchor_id}" color="{link_color}">{title_text}</link>', title_style)
                    page_para = Paragraph(f'<link href="#{anchor_id}" color="{link_color}">{page_num}</link>', page_style)
                    toc_data = [[title_para, page_para]]
                
                    # Use SAME column widths as level 0 to ensure page numbers align to right margin
                    toc_table = Table(toc_data, colWidths=[title_width, page_num_width])
                    toc_table.setStyle(TableStyle([
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                        ('TOPPADDING', (0, 0), (-1, -1), 2),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ]))
            
                story.append(toc_table)
            
                if node['children']:
                    add_toc_entries(node['children'], level + 1, page_counter)
    
        add_toc_entries(tree)
    
        # Switch to normal page template for content sections
        story.append(NextPageTemplate('normal_page'))
        story.append(PageBreak())
    
        # Content sections
        def add_content_nodes(nodes, level=0):
            for node in nodes:
                # Named anchor so TOC links can navigate directly to this section
                story.append(AnchorFlowable(f'node_{node["id"]}'))

                # Create proper heading hierarchy based on collection structure
                heading_text = _pdf_sanitize_text(node['title'])
            
                # Use config-based heading styles
                current_heading_style = config.create_heading_style(base_styles, level)
            
                # Guard against empty headings — ReportLab fails on whitespace-only text
                safe_heading = heading_text.strip() or '&nbsp;'
                try:
                    story.append(Paragraph(safe_heading, current_heading_style))
                except Exception:
                    story.append(Paragraph('&nbsp;', current_heading_style))
            
                # Add content with proper indentation for hierarchy
                if node['content']:
                    # Convert markdown-like content to paragraphs
                    content_paragraphs = convert_markdown_to_pdf_paragraphs(_pdf_sanitize_text(node['content']), temp_dir=_pdf_temp_dir)
                    for para in content_paragraphs:
                        if not para or not para.strip():
                            continue
                        # Standalone image sentinel — emit as a proper Image flowable so
                        # ReportLab can handle page breaks correctly (inline img in Paragraph
                        # causes overflow/overlap).
                        if para.startswith('__PDF_IMG__:'):
                            try:
                                _, img_src, img_w, img_h = para.split(':', 3)
                                story.append(Spacer(1, 4))
                                story.append(Image(img_src, width=int(img_w), height=int(img_h)))
                                story.append(Spacer(1, 4))
                            except Exception:
                                pass  # skip broken image sentinel
                            continue
                        # Table sentinel — render a ReportLab Table flowable.
                        if para.startswith('__TABLE__:'):
                            try:
                                raw_json = para[len('__TABLE__:'):]
                                table_rows = json.loads(raw_json)
                                if table_rows and isinstance(table_rows, list):
                                    normalized = []
                                    max_cols = max(len(r) for r in table_rows if isinstance(r, list))
                                    if max_cols > 0:
                                        for row in table_rows:
                                            row = row if isinstance(row, list) else ['']
                                            row = row + [''] * (max_cols - len(row))
                                            normalized.append(row)

                                        table_data = []
                                        for r_idx, row in enumerate(normalized):
                                            base_cell_style = config.create_content_style(base_styles, level)
                                            cell_style = ParagraphStyle(
                                                f'TableCell{level}_{r_idx}',
                                                parent=base_cell_style,
                                                leftIndent=0,
                                                rightIndent=0,
                                                firstLineIndent=0,
                                                spaceAfter=0,
                                                alignment=TA_LEFT,
                                            )
                                            if r_idx == 0:
                                                cell_style = ParagraphStyle(
                                                    f'TableHeader{level}',
                                                    parent=cell_style,
                                                    fontName=config.FONTS['heading'],
                                                    alignment=TA_LEFT,
                                                )
                                            table_data.append([
                                                Paragraph(_pdf_sanitize_text(_format_inline_markdown_for_pdf(str(cell) or '&nbsp;')), cell_style)
                                                for cell in row
                                            ])

                                        available_width = (
                                            config.PAGE_SIZE[0]
                                            - config.MARGINS['left']
                                            - config.MARGINS['right']
                                            - max(0, (level - 1) * config.INDENTS['content_per_level'])
                                        )
                                        col_width = max(48, available_width / max_cols)
                                        pdf_table = Table(
                                            table_data,
                                            colWidths=[col_width] * max_cols,
                                            hAlign='LEFT'
                                        )
                                        pdf_table.setStyle(TableStyle([
                                            ('GRID', (0, 0), (-1, -1), 0.5, config.COLORS['border']),
                                            ('BACKGROUND', (0, 0), (-1, 0), config.COLORS['light_bg']),
                                            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                            ('LEFTPADDING', (0, 0), (-1, -1), 2),
                                            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                                            ('TOPPADDING', (0, 0), (-1, -1), 3),
                                            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                                        ]))
                                        story.append(Spacer(1, 4))
                                        story.append(pdf_table)
                                        story.append(Spacer(1, 6))
                            except Exception:
                                current_app.logger.debug('PDF: failed to render table sentinel')
                            continue
                        # Bullet list item — use hanging-indent bullet style
                        if para.startswith('__BULLET__:'):
                            # Use &nbsp; so ReportLab's XML parser doesn't collapse the spaces
                            bullet_text = '•&nbsp;&nbsp;' + para[len('__BULLET__:'):]
                            bullet_style = config.create_bullet_style(base_styles, level)
                            try:
                                story.append(Paragraph(bullet_text, bullet_style))
                            except Exception:
                                pass
                            continue
                        # Numbered list item — use hanging-indent numbered style
                        if re.match(r'^__ORDERED__\d+__:', para):
                            m = re.match(r'^__ORDERED__(\d+)__:(.*)', para, re.DOTALL)
                            if m:
                                # Use &nbsp; so ReportLab's XML parser doesn't collapse the spaces
                                num_text = f'{m.group(1)}.&nbsp;&nbsp;{m.group(2)}'
                                num_style = config.create_numbered_style(base_styles, level)
                                try:
                                    story.append(Paragraph(num_text, num_style))
                                except Exception:
                                    pass
                            continue
                        # Create content style that matches the hierarchy level
                        level_content_style = config.create_content_style(base_styles, level)
                        try:
                            story.append(Paragraph(para, level_content_style))
                        except Exception:
                            # Log the bad paragraph text for diagnostics and skip it
                            current_app.logger.debug(
                                f"PDF: skipped unparseable paragraph text {para!r}"
                            )
                            continue
            
                # Add spacing after content
                story.append(Spacer(1, 8))
            
                # Recursively add children with increased level
                if node['children']:
                    add_content_nodes(node['children'], level + 1)
                
                    # Add extra spacing after a section with children
                    if level < 2:  # Only for top-level sections
                        story.append(Spacer(1, 16))
    
        add_content_nodes(tree)
    
        return story

    # Two-pass PDF build: pass 1 measures actual page numbers for the TOC;
    # pass 2 uses those numbers so TOC links and displayed numbers are correct.
    anchor_pages = {}

    def _capture_anchors(flowable):
        if isinstance(flowable, AnchorFlowable):
            anchor_pages[flowable._name] = dry_doc.page

    try:
        dry_buf = io.BytesIO()
        dry_doc = _make_doc(dry_buf)
        dry_doc.afterFlowable = _capture_anchors
        dry_doc.build(_make_story(anchor_pages))
    except Exception as _e:
        current_app.logger.debug(f"DEBUG: PDF dry-run pass failed (page numbers may be estimates): {_e}")

    buffer = io.BytesIO()
    doc = _make_doc(buffer)
    try:
        doc.build(_make_story(anchor_pages))
    finally:
        shutil.rmtree(_pdf_temp_dir, ignore_errors=True)
    buffer.seek(0)
    return buffer

def _download_image_for_pdf(url: str, temp_dir: str) -> str:
    """Download an external image URL to *temp_dir* and return the local path.

    Returns an empty string if the download fails or the image cannot be
    validated, so the caller can safely skip the image without crashing.
    """
    try:
        resp = _http.get(url, timeout=10, stream=True)
        if resp.status_code != 200:
            return ''
        content_type = resp.headers.get('content-type', '')
        if 'png' in content_type:
            ext = '.png'
        elif 'gif' in content_type:
            ext = '.gif'
        elif 'webp' in content_type:
            ext = '.webp'
        else:
            # Try to guess from URL, default to jpg
            url_lower = url.lower().split('?')[0]
            if url_lower.endswith('.png'):
                ext = '.png'
            elif url_lower.endswith('.gif'):
                ext = '.gif'
            elif url_lower.endswith('.webp'):
                ext = '.webp'
            else:
                ext = '.jpg'
        tmp_path = os.path.join(temp_dir, f'img_{abs(hash(url)) % 10**9}{ext}')
        with open(tmp_path, 'wb') as f:
            for chunk in resp.iter_content(8192):
                f.write(chunk)
        return tmp_path
    except Exception:
        return ''


def convert_markdown_to_pdf_paragraphs(text, temp_dir=None):
    """Convert markdown-like text to PDF paragraphs with better hierarchy support"""
    if not text:
        return [""]
    
    # Normalize line endings and strip non-breaking spaces that can confuse parser
    safe_text = text.replace('\r\n', '\n').replace('\r', '\n').replace('\u00A0', ' ')

    # Unescape Pandoc/Markdown backslash-escaped characters (e.g. \$ -> $, \* -> *)
    # Pandoc escapes $ and other chars to prevent LaTeX/Markdown interpretation
    safe_text = re.sub(r'\\([\\`*_{}\[\]()\#+\-.!$|~^])', r'\1', safe_text)

    # Pre-process HTML structural tags produced by snippet resolution (mistune output)
    # into markdown / ReportLab-compatible format before the line-by-line pass below.
    # Convert <strong>/<em> to ReportLab-supported <b>/<i>
    safe_text = re.sub(r'<strong>(.*?)</strong>', r'<b>\1</b>', safe_text, flags=re.IGNORECASE | re.DOTALL)
    safe_text = re.sub(r'<em>(.*?)</em>', r'<i>\1</i>', safe_text, flags=re.IGNORECASE | re.DOTALL)
    # Normalize HTML <br> to XHTML <br/> required by ReportLab's XML parser;
    # then convert standalone <br/> separators to blank lines so they act as paragraph breaks.
    safe_text = re.sub(r'<br\s*/?>', '\n', safe_text, flags=re.IGNORECASE)
    # Convert HTML headings (h1–h6) to markdown heading syntax
    for _lvl in range(6, 0, -1):
        safe_text = re.sub(
            r'<h' + str(_lvl) + r'[^>]*>(.*?)</h' + str(_lvl) + r'>',
            '\n' + '#' * _lvl + r' \1\n',
            safe_text, flags=re.IGNORECASE | re.DOTALL
        )
    # Convert ordered lists to numbered markdown items
    def _convert_ol_block(m):
        items = re.findall(r'<li[^>]*>(.*?)</li>', m.group(1), re.IGNORECASE | re.DOTALL)
        return '\n' + '\n'.join(f'{i + 1}. {item.strip()}' for i, item in enumerate(items)) + '\n'
    safe_text = re.sub(r'<ol[^>]*>(.*?)</ol>', _convert_ol_block, safe_text, flags=re.IGNORECASE | re.DOTALL)
    # Convert unordered lists to markdown bullet items
    def _convert_ul_block(m):
        items = re.findall(r'<li[^>]*>(.*?)</li>', m.group(1), re.IGNORECASE | re.DOTALL)
        return '\n' + '\n'.join(f'- {item.strip()}' for item in items) + '\n'
    safe_text = re.sub(r'<ul[^>]*>(.*?)</ul>', _convert_ul_block, safe_text, flags=re.IGNORECASE | re.DOTALL)
    # Strip any stray <li> tags not caught above
    safe_text = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1\n', safe_text, flags=re.IGNORECASE | re.DOTALL)
    # Strip table tags (extract text content only — ReportLab has no table flowable here)
    safe_text = re.sub(r'</?(?:table|thead|tbody|tfoot|tr|th|td|caption)[^>]*>', '\n', safe_text, flags=re.IGNORECASE)
    # Strip <p> wrappers, preserving inner content with a trailing newline
    safe_text = re.sub(r'<p[^>]*>', '', safe_text, flags=re.IGNORECASE)
    safe_text = re.sub(r'</p>', '\n', safe_text, flags=re.IGNORECASE)

    lines = safe_text.split('\n')
    paragraphs = []
    current_paragraph = []
    in_list = False
    list_items = []
    list_type = None  # 'bullet' or 'ordered'
    
    # Utility to escape ampersands that are not part of known entities
    def escape_unescaped_ampersands(s: str) -> str:
        # Replace & that are not followed by a valid entity pattern
        return re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#\d+;|#x[0-9A-Fa-f]+;)', '&amp;', s)

    def format_list_item_text(item_text: str) -> str:
        """Normalize inline markdown within list item text for ReportLab rendering."""
        if not item_text:
            return ''
        return _pdf_sanitize_text(_format_inline_markdown_for_pdf(item_text.strip()))
    
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        table_rows, next_index = _consume_markdown_table(lines, i)
        if table_rows:
            if current_paragraph:
                paragraphs.append(' '.join(current_paragraph))
                current_paragraph = []
            if in_list and list_items:
                if list_type == 'ordered':
                    for num, item in list_items:
                        paragraphs.append(f'__ORDERED__{num}__:{item}')
                else:
                    for item in list_items:
                        paragraphs.append(f'__BULLET__:{item}')
                list_items = []
                list_type = None
                in_list = False
            paragraphs.append(f'__TABLE__:{json.dumps(table_rows)}')
            i = next_index
            continue
        
        # Handle headers (these will be rendered as bold text within content)
        if stripped.startswith('#'):
            # Finish any current paragraph or list
            if current_paragraph:
                paragraphs.append(' '.join(current_paragraph))
                current_paragraph = []
            if in_list:
                # Create a proper list paragraph
                if list_type == 'ordered':
                    for num, item in list_items:
                        paragraphs.append(f'__ORDERED__{num}__:{item}')
                else:
                    for item in list_items:
                        paragraphs.append(f'__BULLET__:{item}')
                list_items = []
                list_type = None
                in_list = False
            
            # Convert markdown headers to styled headings with appropriate font sizes
            header_level = len(stripped) - len(stripped.lstrip('#'))
            header_text = stripped.lstrip('#').strip()
            if header_text:
                # Map markdown heading levels to appropriate font sizes
                # H1 (header_level=1) -> H2 style, H2 -> H3 style, etc.
                if header_level == 1:  # # Header
                    font_size = 16  # H2 equivalent size
                elif header_level == 2:  # ## Header  
                    font_size = 14  # H3 equivalent size
                elif header_level == 3:  # ### Header
                    font_size = 12  # H4 equivalent size
                else:  # #### and deeper
                    font_size = 11  # H5+ equivalent size
                
                # Use explicit font tag with size to ensure proper rendering
                paragraphs.append(f'<font face="Helvetica-Bold" size="{font_size}"><b>{header_text}</b></font>')
            
            
        # Handle bullet points and create proper lists
        elif re.match(r'^-\s+', stripped) or re.match(r'^\*\s+', stripped):
            if current_paragraph:
                paragraphs.append(' '.join(current_paragraph))
                current_paragraph = []
            if in_list and list_type == 'ordered' and list_items:
                # switching from ordered to bullet — flush ordered first
                for num, item in list_items:
                    paragraphs.append(f'__ORDERED__{num}__:{item}')
                list_items = []
            bullet_text = re.sub(r'^[-\*]\s+', '', stripped, count=1)
            bullet_text = format_list_item_text(bullet_text)
            list_items.append(bullet_text)
            list_type = 'bullet'
            in_list = True
            
        # Handle numbered lists
        elif re.match(r'^\d+\. ', stripped):
            if current_paragraph:
                paragraphs.append(' '.join(current_paragraph))
                current_paragraph = []
            if in_list and list_type == 'bullet' and list_items:
                # switching from bullet to ordered — flush bullets first
                for item in list_items:
                    paragraphs.append(f'__BULLET__:{item}')
                list_items = []
            dot_pos = stripped.index('. ')
            num = int(stripped[:dot_pos])
            numbered_text = stripped[dot_pos + 2:].strip()
            numbered_text = format_list_item_text(numbered_text)
            list_items.append((num, numbered_text))
            list_type = 'ordered'
            in_list = True
            
        # Handle empty lines (paragraph breaks)
        elif not stripped:
            if current_paragraph:
                paragraphs.append(' '.join(current_paragraph))
                current_paragraph = []
            if in_list:
                # Finish the current list
                if list_items:
                    if list_type == 'ordered':
                        for num, item in list_items:
                            paragraphs.append(f'__ORDERED__{num}__:{item}')
                    else:
                        for item in list_items:
                            paragraphs.append(f'__BULLET__:{item}')
                    list_items = []
                list_type = None
                in_list = False
                
        # Regular text
        else:
            if in_list:
                # Finish the current list first
                if list_items:
                    if list_type == 'ordered':
                        for num, item in list_items:
                            paragraphs.append(f'__ORDERED__{num}__:{item}')
                    else:
                        for item in list_items:
                            paragraphs.append(f'__BULLET__:{item}')
                    list_items = []
                list_type = None
                in_list = False
            
            # Handle basic markdown formatting within text
            formatted_line = stripped
            # Bold text
            formatted_line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', formatted_line)
            # Italic text
            formatted_line = re.sub(r'\*(.*?)\*', r'<i>\1</i>', formatted_line)
            # Code
            formatted_line = re.sub(r'`(.*?)`', r'<font face="Courier">\1</font>', formatted_line)
            
            # Handle markdown images first - convert to simple HTML
            formatted_line = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2">', formatted_line)
            
            # Clean up HTML tags that ReportLab doesn't support
            # Remove div, span, p tags but keep their content
            formatted_line = re.sub(r'</?div[^>]*>', '', formatted_line)
            formatted_line = re.sub(r'</?span[^>]*>', '', formatted_line)
            formatted_line = re.sub(r'</?p[^>]*>', '', formatted_line)
            # Convert <a href="...">text</a> to "text (url)" so the destination is
            # visible in the PDF; then strip any remaining bare <a> tags (anchors etc.)
            formatted_line = re.sub(
                r'<a\s[^>]*href="([^"]*)"[^>]*>(.*?)</a>',
                lambda m: f'{m.group(2)} ({m.group(1)})',
                formatted_line, flags=re.IGNORECASE | re.DOTALL
            )
            formatted_line = re.sub(r'</?a[^>]*>', '', formatted_line)
            
            # Handle images - ReportLab only supports specific img attributes
            if '<img' in formatted_line:
                # Remove unsupported attributes like 'alt', 'style', 'class'
                # Keep only 'src', 'width', 'height', 'valign'
                def clean_img_tag(match):
                    img_tag = match.group(0)
                    # Extract src attribute
                    src_match = re.search(r'src="([^"]*)"', img_tag)
                    src = src_match.group(1) if src_match else ""
                    
                    # Convert relative image paths to absolute paths
                    if src:
                        if src.startswith('http://') or src.startswith('https://'):
                            # Download an external image from remote object storage to a temp dir
                            if temp_dir:
                                src = _download_image_for_pdf(src, temp_dir)
                                if not src:
                                    return ''
                                # src is now an absolute local temp path; skip path conversion
                            else:
                                return ''
                        elif src.startswith('data:'):
                            # Skip data URIs as reportlab Paragraph img doesn't handle them
                            return ''
                        else:
                            resolved = _resolve_local_image_path_for_pdf(src)
                            if resolved:
                                src = resolved
                            else:
                                # If file doesn't exist in known roots, drop the image
                                return ''
                    else:
                        return ''
                    
                    # Extract width and height if present
                    width_match = re.search(r'width="([^"]*)"', img_tag)
                    height_match = re.search(r'height="([^"]*)"', img_tag)
                    
                    # Build clean img tag with only supported attributes
                    clean_attrs = []
                    if src and os.path.exists(src):
                        # Validate image and read natural dimensions for scaling
                        try:
                            from PIL import Image as PILImage
                            with open(src, 'rb') as _f:
                                pil_img = PILImage.open(_f)
                                pil_img.verify()
                            with open(src, 'rb') as _f:
                                pil_img = PILImage.open(_f)
                                natural_w, natural_h = pil_img.size
                        except Exception:
                            return ''
                        clean_attrs.append(f'src="{src}"')
                        # Constrain to fit within the content column (~400pt ≈ 5.5 inches).
                        # Use explicit width/height from the original tag if provided,
                        # otherwise scale the natural image size down as needed.
                        MAX_WIDTH = 400
                        if width_match:
                            try:
                                w = int(width_match.group(1))
                                h = int(height_match.group(1)) if height_match else int(natural_h * w / natural_w)
                            except (ValueError, ZeroDivisionError):
                                w, h = natural_w, natural_h
                        else:
                            w, h = natural_w, natural_h
                        if w > MAX_WIDTH and w > 0:
                            h = int(h * MAX_WIDTH / w)
                            w = MAX_WIDTH
                        clean_attrs.append(f'width="{w}"')
                        clean_attrs.append(f'height="{h}"')
                    if not clean_attrs:
                        return ''
                    # Return a sentinel so the caller can emit a standalone Image flowable
                    # instead of embedding inside a Paragraph (which causes overflow issues).
                    return f'__PDF_IMG__:{src}:{w}:{h}'
                
                formatted_line = re.sub(r'<img[^>]*>', clean_img_tag, formatted_line)
                # If this line contains an image sentinel, flush surrounding text and
                # emit the image as its own paragraph entry so generate_pdf can use
                # a proper Image flowable (not a Paragraph).
                img_sentinel_re = re.compile(r'__PDF_IMG__:([^:]+):(\d+):(\d+)')
                if img_sentinel_re.search(formatted_line):
                    # Flush any accumulated paragraph text first
                    if current_paragraph:
                        paragraphs.append(' '.join(current_paragraph))
                        current_paragraph = []
                    # Emit each image sentinel as a standalone entry; emit surrounding text too
                    parts = img_sentinel_re.split(formatted_line)
                    # parts: [pre, src, w, h, post, src2, w2, h2, post2, ...]
                    idx = 0
                    while idx < len(parts):
                        chunk = parts[idx].strip()
                        if chunk:
                            paragraphs.append(chunk)
                        idx += 1
                        if idx + 2 < len(parts):
                            img_src, img_w, img_h = parts[idx], parts[idx+1], parts[idx+2]
                            paragraphs.append(f'__PDF_IMG__:{img_src}:{img_w}:{img_h}')
                            idx += 3
                    formatted_line = ''  # already handled
            
            # Escape stray ampersands and clean up extra whitespace
            formatted_line = escape_unescaped_ampersands(formatted_line)
            # Final PDF sanitization pass to fix misnested tags and remove attribute blocks
            formatted_line = _pdf_sanitize_text(formatted_line)
            # Clean up extra whitespace and empty content
            formatted_line = formatted_line.strip()
            if formatted_line:  # Only add non-empty lines
                current_paragraph.append(formatted_line)

        i += 1
    
    # Add any remaining content
    if current_paragraph:
        paragraphs.append(' '.join(current_paragraph))
    if in_list and list_items:
        if list_type == 'ordered':
            for num, item in list_items:
                paragraphs.append(f'__ORDERED__{num}__:{item}')
        else:
            for item in list_items:
                paragraphs.append(f'__BULLET__:{item}')
    
    return [p for p in paragraphs if p.strip()]

def convert_image_to_base64(image_src):
    """Convert an image reference to a base64 data URL for embedding in standalone HTML.

    - Absolute http/https URLs are returned as-is (they work from any browser).
    - /images/<filename> paths and bare filenames are resolved by searching all
      known local image directories; if found, the file is embedded as base64.
    - Falls back to the original src if the image cannot be found.
    """
    try:
        # Absolute URLs work fine in a downloaded HTML file — leave them alone.
        if image_src.startswith('http://') or image_src.startswith('https://') or image_src.startswith('data:'):
            return image_src

        # Strip well-known prefixes to get the bare filename / relative path.
        if image_src.startswith('/images/'):
            rel_path = image_src[8:]
        elif image_src.startswith('/static/images/'):
            rel_path = image_src[15:]
        else:
            rel_path = image_src  # bare filename or unknown relative path

        # Search all directories the backend serves images from.
        candidate_roots = []
        try:
            candidate_roots.append(os.path.join(current_app.config['STATIC_FOLDER'], 'images'))
        except Exception:
            pass
        try:
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            candidate_roots += [
                os.path.join(root_dir, 'frontend', 'dist', 'images'),
                os.path.join(root_dir, 'frontend', 'public', 'images'),
                os.path.join(root_dir, 'backend', 'static', 'images'),
            ]
        except Exception:
            pass
        candidate_roots.append(resolve_local_storage_root())
        candidate_roots.append('/app/data/images')

        full_image_path = None
        for root in candidate_roots:
            candidate = os.path.join(root, rel_path)
            if os.path.exists(candidate):
                full_image_path = candidate
                break

        if not full_image_path:
            current_app.logger.debug(f"Warning: Image not found for '{image_src}' (searched {len(candidate_roots)} directories)")
            return image_src  # Return original — broken but at least doesn't crash

        mime_type, _ = mimetypes.guess_type(full_image_path)
        if not mime_type:
            mime_type = 'image/jpeg'

        with open(full_image_path, 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
            return f"data:{mime_type};base64,{image_data}"

    except Exception as e:
        current_app.logger.debug(f"Error converting image {image_src} to base64: {str(e)}")
        return image_src

def convert_markdown_to_html(markdown_text):
    """Basic markdown to HTML conversion for mobile display"""
    if not markdown_text:
        return "<p>No content available.</p>"
    
    html = markdown_text
    
    # Headers
    html = re.sub(r'^### (.*$)', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*$)', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.*$)', r'<h2>\1</h2>', html, flags=re.MULTILINE)  # Convert h1 to h2 since page already has h1
    
    # Bold and italic
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    
    # Code
    html = re.sub(r'`(.*?)`', r'<code>\1</code>', html)
    
    # Images - handle both markdown format and direct HTML img tags, convert to base64
    def replace_markdown_image(match):
        alt_text = match.group(1)
        image_src = match.group(2)
        base64_src = convert_image_to_base64(image_src)
        return f'<img src="{base64_src}" alt="{alt_text}" class="mobile-kb-image">'
    
    def replace_html_image(match):
        pre_attrs = match.group(1)
        image_src = match.group(2)
        post_attrs = match.group(3)
        base64_src = convert_image_to_base64(image_src)
        return f'<img{pre_attrs}src="{base64_src}"{post_attrs} class="mobile-kb-image">'
    
    html = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_markdown_image, html)
    html = re.sub(r'<img([^>]*?)src="([^"]*)"([^>]*?)>', replace_html_image, html)
    
    # Links
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', html)
    
    # Lists — handle both markdown (- / 1.) and already-HTML content from TinyMCE
    lines = html.split('\n')
    in_list = False
    list_type = None   # 'ul' or 'ol'
    result_lines = []

    # Regex to detect a line that is already an HTML tag (open or close).
    # Such lines must be passed through as-is so existing <ul>/<li> structure is preserved.
    _html_tag_re = re.compile(r'^</?[a-zA-Z][a-zA-Z0-9]*[\s>/]', re.IGNORECASE)

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        table_rows, next_index = _consume_markdown_table(lines, i)
        if table_rows:
            if in_list:
                result_lines.append(f'</{list_type}>')
                in_list = False
                list_type = None

            header = table_rows[0]
            body = table_rows[1:]
            table_html = ['<table>', '<thead>', '<tr>']
            table_html.extend([f'<th>{cell}</th>' for cell in header])
            table_html.extend(['</tr>', '</thead>'])
            if body:
                table_html.append('<tbody>')
                for row in body:
                    table_html.append('<tr>')
                    table_html.extend([f'<td>{cell}</td>' for cell in row])
                    table_html.append('</tr>')
                table_html.append('</tbody>')
            table_html.append('</table>')
            result_lines.append(''.join(table_html))
            i = next_index
            continue
        if stripped.startswith('- ') or stripped.startswith('* '):
            if not in_list:
                result_lines.append('<ul>')
                in_list = True
                list_type = 'ul'
            result_lines.append(f'<li>{stripped[2:]}</li>')
        elif re.match(r'^\d+\. ', stripped):
            if not in_list:
                result_lines.append('<ol>')
                in_list = True
                list_type = 'ol'
            result_lines.append(f'<li>{stripped[stripped.index(". ") + 2:]}</li>')
        else:
            if in_list:
                result_lines.append(f'</{list_type}>')
                in_list = False
                list_type = None
            if stripped:
                # Pass HTML block-level tags through as-is (TinyMCE content is already HTML)
                if stripped.startswith('<img') or '<img' in stripped or _html_tag_re.match(stripped):
                    result_lines.append(stripped)
                else:
                    result_lines.append(f'<p>{stripped}</p>')
            else:
                result_lines.append('')

        i += 1

    if in_list:
        result_lines.append(f'</{list_type}>')
    
    return '\n'.join(result_lines)
