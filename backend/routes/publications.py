from flask import Blueprint, Flask, request, jsonify, render_template_string, make_response, current_app
from ..models import db, Publication, PublicationNode, Topic
from datetime import datetime
import re
import os
import base64
import mimetypes
import io
import json
import traceback
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image, NextPageTemplate, Flowable
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.platypus.frames import Frame
from reportlab.pdfgen import canvas
from backend.pdf_config import PDFConfig, CorporateConfig, AcademicConfig, CompactConfig, OrganizationConfig


class BackgroundImageDocTemplate(BaseDocTemplate):
    """Custom document template that supports background images, headers and footers on pages"""
    
    def __init__(self, filename, background_image_path=None, publication=None, **kwargs):
        BaseDocTemplate.__init__(self, filename, **kwargs)
        self.background_image_path = background_image_path
        self.publication = publication
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
                print(f"Warning: Could not add background image: {e}")
        
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
        """Add footer for title page with Census logo"""
        try:
            canvas.saveState()
            page_width, page_height = self.pagesize
            
            # Logo positioning - 0.25" from left and bottom edges of page
            logo_x = 0.25 * inch  # 0.25" from left edge of page
            logo_y = 0.25 * inch  # 0.25" from bottom edge of page
            logo_width = 2.0 * inch  # Title page logo should be 2" wide
            logo_height = logo_width / 1.77  # Maintain proper 1.77:1 aspect ratio
            
            # Add Census logo (positioned at left edge)
            title_logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'backgrounds', 'Title_Page_Logo.png')
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
                    print("Warning: Could not load title page logo")
            
            # Set font for footer text
            canvas.setFont("Helvetica", 10)
            
            # Footer text positioning - move up one row to align better with visual top of logo
            footer_text_y = logo_y + logo_height - 32  # Move text down about 14 more points
            right_margin_x = page_width - 0.5 * inch  # Use 0.5" right margin
            
            # Top row: "U.S. Census Bureau" (centered) and revision date (right)
            canvas.drawCentredString(page_width / 2, footer_text_y, "U.S. Census Bureau")
            
            form_number = getattr(self.publication, 'form_number', f"xx.{self.publication.id:04d}")
            form_text = f"Form: {form_number}"
            text_width = canvas.stringWidth(form_text, "Helvetica", 10)
            canvas.drawString(right_margin_x - text_width, footer_text_y, form_text)
            
            # Bottom row: "Revised:" with date - right-aligned under form number
            revised_text = f"Revised: {datetime.now().strftime('%m/%d/%Y')}"
            revised_text_width = canvas.stringWidth(revised_text, "Helvetica", 10)
            canvas.drawString(right_margin_x - revised_text_width, footer_text_y - 15, revised_text)
            
            canvas.restoreState()
        except Exception as e:
            print(f"Warning: Could not add title footer: {e}")
    
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
            
            # Add Census logo
            footer_logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'backgrounds', 'Footer_Logo.png')
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
                    print("Warning: Could not load footer logo")
            
            # Set font for footer text
            canvas.setFont("Helvetica", 9)
            footer_text_y = logo_y + logo_height - 24  # Match standard page positioning
            
            # Top row: "U.S. Census Bureau" (centered) and revision date (right)
            canvas.drawCentredString(page_width / 2, footer_text_y, "U.S. Census Bureau")
            
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
            print(f"Warning: Could not add TOC footer: {e}")

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
            
            # Add Census logo
            footer_logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'backgrounds', 'Footer_Logo.png')
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
                    print("Warning: Could not load footer logo")
            
            # Set font for footer text
            canvas.setFont("Helvetica", 9)
            
            # Footer text positioning - below the horizontal line
            footer_text_y = logo_y + logo_height - 24  # Move down 24 pts from original
            
            # Top row: "U.S. Census Bureau" (centered) and revision date (right)
            canvas.drawCentredString(page_width / 2, footer_text_y, "U.S. Census Bureau")
            
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
            print(f"Warning: Could not add content footer: {e}")
            print(f"Warning: Could not add content footer: {e}")
    
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
            print(f"Warning: Could not add header: {e}")


class HeaderDocTemplate(BaseDocTemplate):
    """Document template with headers and footers for PDF documents without background images"""
    
    def __init__(self, filename, publication=None, **kwargs):
        BaseDocTemplate.__init__(self, filename, **kwargs)
        self.publication = publication
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
        """Add footer for title page with Census logo"""
        try:
            canvas.saveState()
            page_width, page_height = self.pagesize
            
            # Logo positioning - 0.25" from left and bottom edges of page
            logo_x = 0.25 * inch  # 0.25" from left edge of page
            logo_y = 0.25 * inch  # 0.25" from bottom edge of page
            logo_width = 2.0 * inch  # Title page logo should be 2" wide
            logo_height = logo_width / 1.77  # Maintain proper 1.77:1 aspect ratio
            
            # Add Census logo (positioned at left edge)
            title_logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'backgrounds', 'Title_Page_Logo.png')
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
                    print("Warning: Could not load title page logo")
            
            # Set font for footer text
            canvas.setFont("Helvetica", 9)
            
            # Footer text positioning - move up one row to align better with visual top of logo
            footer_text_y = logo_y + logo_height - 26  # Move text down about 14 more points
            right_margin_x = page_width - 0.5 * inch  # Use 0.5" right margin
            
            # Top row: "U.S. Census Bureau" (centered) and revision date (right)
            canvas.drawCentredString(page_width / 2, footer_text_y, "U.S. Census Bureau")
            
            form_number = getattr(self.publication, 'form_number', f"xx.{self.publication.id:04d}")
            form_text = f"Form: {form_number}"
            text_width = canvas.stringWidth(form_text, "Helvetica", 10)
            canvas.drawString(right_margin_x - text_width, footer_text_y, form_text)
            
            # Bottom row: "Revised:" with date - right-aligned under form number
            revised_text = f"Revised: {datetime.now().strftime('%m/%d/%Y')}"
            revised_text_width = canvas.stringWidth(revised_text, "Helvetica", 10)
            canvas.drawString(right_margin_x - revised_text_width, footer_text_y - 15, revised_text)
            
            canvas.restoreState()
        except Exception as e:
            print(f"Warning: Could not add title footer: {e}")
    
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
            
            # Add Census logo
            footer_logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'backgrounds', 'Footer_Logo.png')
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
                    print("Warning: Could not load footer logo")
            
            # Set font for footer text
            canvas.setFont("Helvetica", 9)
            
            # Footer text positioning - below the horizontal line
            footer_text_y = logo_y + logo_height - 24  # Match standard page positioning
            
            # Top row: "U.S. Census Bureau" (centered) and revision date (right)
            canvas.drawCentredString(page_width / 2, footer_text_y, "U.S. Census Bureau")
            
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
            print(f"Warning: Could not add TOC footer: {e}")

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
            
            # Add Census logo
            footer_logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'backgrounds', 'Footer_Logo.png')
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
                    print("Warning: Could not load footer logo")
            
            # Set font for footer text
            canvas.setFont("Helvetica", 9)
            
            # Footer text positioning - below the horizontal line
            footer_text_y = logo_y + logo_height - 24  # Move down 24 pts from original
            
            # Top row: "U.S. Census Bureau" (centered) and revision date (right)
            canvas.drawCentredString(page_width / 2, footer_text_y, "U.S. Census Bureau")
            
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
            print(f"Warning: Could not add content footer: {e}")
            print(f"Warning: Could not add content footer: {e}")
    
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
        print("DEBUG: HeaderDocTemplate add_header called")
        if not self.publication:
            print("DEBUG: No publication object")
            return
            
        try:
            print(f"DEBUG: Adding header for publication: {self.publication.title}")
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
            print("DEBUG: Header drawing completed successfully")
            
        except Exception as e:
            print(f"WARNING: Could not add header: {e}")
            import traceback
            traceback.print_exc()


# Pass strict_slashes here so both /api/publications and /api/publications/ match
pubs_bp = Blueprint(
    'publications',
    __name__,
    url_prefix='/api/publications',
)

@pubs_bp.route('', methods=['GET'])
def list_pubs():
    all_pubs = Publication.query.order_by(Publication.created_at.desc()).all()
    
    # Group publications by title and return only the latest version of each
    latest_pubs = {}
    for pub in all_pubs:
        if pub.title not in latest_pubs:
            latest_pubs[pub.title] = pub
    
    # Convert to list and maintain newest-first order
    result = [pub.to_dict() for pub in latest_pubs.values()]
    # Sort by created_at descending to maintain newest first
    result.sort(key=lambda x: x['created_at'], reverse=True)
    
    return jsonify(result), 200

@pubs_bp.route('', methods=['POST'])
def create_publication():
    """Create a new publication"""
    data = request.get_json()
    
    pub = Publication(
        title=data.get('title', 'Untitled Publication'),
        description=data.get('description', '')
    )
    
    db.session.add(pub)
    db.session.commit()
    
    return jsonify(pub.to_dict()), 201

@pubs_bp.route('/<int:pub_id>', methods=['GET'])
def get_pub(pub_id):
    p = Publication.query.get_or_404(pub_id)
    def serialize(node):
        return {
            'id': node.id,
            'topic': node.topic.to_dict(),
            'position': node.position,
            'children': sorted([serialize(c) for c in node.children],
                               key=lambda x: x['position'])
        }
    top_nodes = [n for n in p.nodes if n.parent_id is None]
    tree = sorted([serialize(n) for n in top_nodes],
                  key=lambda x: x['position'])
    return jsonify({'id': p.id, 'title': p.title, 'description': p.description, 'tree': tree}), 200

@pubs_bp.route('/<int:pub_id>/nodes', methods=['POST'])
def save_nodes(pub_id):
    payload = request.get_json()  # expect {"tree": [...]}
    PublicationNode.query.filter_by(publication_id=pub_id).delete()

    def walk(nodes, parent_id=None):
        for idx, n in enumerate(nodes):
            node = PublicationNode(
                publication_id=pub_id,
                topic_id=n['topic_id'],
                parent_id=parent_id,
                position=idx
            )
            db.session.add(node)
            db.session.flush()  # assign node.id
            if n.get('children'):
                walk(n['children'], node.id)

    walk(payload['tree'])
    db.session.commit()
    return jsonify({'message': 'saved'}), 200

@pubs_bp.route('/<int:pub_id>/export/mobile-kb', methods=['GET'])
def export_mobile_knowledge_base(pub_id):
    """Export publication as mobile-first knowledge base HTML"""
    pub = Publication.query.get_or_404(pub_id)
    
    # Build the hierarchical structure
    def serialize_node(node):
        topic_data = node.topic.to_dict() if node.topic else {'title': 'Unknown', 'content': ''}
        return {
            'id': node.id,
            'topic_id': node.topic_id,
            'title': topic_data.get('title', 'Untitled'),
            'content': topic_data.get('content', ''),
            'position': node.position,
            'children': sorted([serialize_node(c) for c in node.children],
                             key=lambda x: x['position'])
        }
    
    top_nodes = [n for n in pub.nodes if n.parent_id is None]
    tree = sorted([serialize_node(n) for n in top_nodes],
                  key=lambda x: x['position'])
    
    # Generate mobile-optimized HTML
    html_content = generate_mobile_kb_html(pub, tree)
    
    response = make_response(html_content)
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename="{pub.title}_mobile_kb.html"'
    return response

@pubs_bp.route('/<int:pub_id>/preview/mobile-kb', methods=['GET'])
def preview_mobile_knowledge_base(pub_id):
    """Preview publication as mobile-first knowledge base HTML in browser"""
    pub = Publication.query.get_or_404(pub_id)
    
    # Build the hierarchical structure (same as export)
    def serialize_node(node):
        topic_data = node.topic.to_dict() if node.topic else {'title': 'Unknown', 'content': ''}
        return {
            'id': node.id,
            'topic_id': node.topic_id,
            'title': topic_data.get('title', 'Untitled'),
            'content': topic_data.get('content', ''),
            'position': node.position,
            'children': sorted([serialize_node(c) for c in node.children],
                             key=lambda x: x['position'])
        }
    
    top_nodes = [n for n in pub.nodes if n.parent_id is None]
    tree = sorted([serialize_node(n) for n in top_nodes],
                  key=lambda x: x['position'])
    
    # Generate mobile-optimized HTML
    html_content = generate_mobile_kb_html(pub, tree)
    
    response = make_response(html_content)
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    # No attachment header - this will display directly in browser
    return response

def generate_mobile_kb_html(publication, tree):
    """Generate mobile-first HTML for knowledge base using template"""
    
    # Read the template file - get the absolute path to the root directory
    import os
    # Get the root directory (StructuredDocs)
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    template_path = os.path.join(root_dir, 'collection_mobile_kb.html')
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
    except FileNotFoundError:
        # Fallback to old inline generation if template not found
        return generate_mobile_kb_html_inline(publication, tree)
    
    # Build navigation HTML for the sidebar
    def build_nav_html(nodes, level=0, parent_path=""):
        import json
        import html as html_module
        html_content = ""
        for node in nodes:
            node_path = f"{parent_path}.{node['id']}" if parent_path else str(node['id'])
            
            # Show all levels with proper indentation
            indent = "    " * level
            # Use different icons for topics with and without children
            if node.get('children') and len(node.get('children', [])) > 0:
                icon = "📂"  # Folder icon for topics with subtopics
            else:
                icon = "📝"  # Document icon for individual topics
                
            if node.get('children') and len(node.get('children', [])) > 0:
                # Has children - clicking shows content and expands subtopics
                html_content += f'{indent}            <button class="nav-link nav-expandable" onclick="expandTopic(\'{node["id"]}\', this)">{icon} {node["title"]}<span class="nav-expand-icon">▶</span></button>\n'
                # Add hidden subtopics container
                html_content += f'{indent}            <div class="nav-subtopics" id="subtopics-{node["id"]}" style="display: none;">\n'
                # Recursively add children with indentation
                html_content += build_nav_html(node.get('children', []), level + 1, node["id"])
                html_content += f'{indent}            </div>\n'
            else:
                # No children - direct link to content
                html_content += f'{indent}            <button class="nav-link" onclick="showSection(\'section-{node["id"]}\')">{icon} {node["title"]}</button>\n'
            
        return html_content
    
    # Build the complete Topics nav section
    def build_topics_section(nodes):
        nav_html = build_nav_html(nodes)
        return f'''        <div class="nav-section">
            <div class="nav-section-title">📚 Topics</div>
            <button class="nav-link" onclick="showSection('welcome')">🏠 Home</button>
{nav_html}        </div>'''
    
    # Build content sections HTML
    def build_content_html(nodes, parent=None):
        html = ""
        for idx, node in enumerate(nodes):
            # Clean and process content
            content = node.get('content', '')
            if content:
                # Convert markdown content to HTML using proper function
                content = convert_markdown_to_html(content)
            else:
                content = '<p>No content available.</p>'

            has_children = bool(node.get('children'))
            in_this_section_html = ''
            related_content_html = ''

            # If this topic has children, add "In this section..." navigation
            if has_children:
                in_this_section = '<div class="in-this-section">\n<h2>In this section</h2>\n<ul class="section-links">\n'
                for child in node['children']:
                    in_this_section += f'<li><a href="#" onclick="showSection(\'section-{child["id"]}\'); return false;" class="section-link">📝 {child["title"]}</a></li>\n'
                in_this_section += '</ul>\n</div>\n'
                # Add the section navigation after the main content
                if content == '<p>No content available.</p>':
                    # If no content, replace with section overview
                    content = f'<p>This section contains multiple topics. Use the links below to navigate to specific content.</p>\n{in_this_section}'
                else:
                    # If there is content, append the section navigation
                    content += f'\n{in_this_section}'
                in_this_section_html = in_this_section
            else:
                # No children: add Related content section if there are siblings or children
                # Siblings: other topics at the same level (from parent)
                siblings = []
                if parent and parent.get('children'):
                    siblings = [sib for sib in parent['children'] if sib['id'] != node['id']]
                # Children: always empty here (no children)
                # But for completeness, if node.get('children'), add them
                related_links = []
                # Add siblings
                for sib in siblings:
                    related_links.append(f'<li><a href="#" onclick="showSection(\'section-{sib["id"]}\'); return false;" class="section-link">📝 {sib["title"]}</a></li>')
                    # Also add their children (lower level)
                    if sib.get('children'):
                        for child in sib['children']:
                            related_links.append(f'<li class="sub-related"><a href="#" onclick="showSection(\'section-{child["id"]}\'); return false;" class="section-link">📝 {child["title"]}</a></li>')
                # Add own children (should be none, but for completeness)
                if node.get('children'):
                    for child in node['children']:
                        related_links.append(f'<li class="sub-related"><a href="#" onclick="showSection(\'section-{child["id"]}\'); return false;" class="section-link">📝 {child["title"]}</a></li>')
                if related_links:
                    related_content_html = '<div class="related-content">\n<h2>Related content</h2>\n<ul class="section-links">\n' + '\n'.join(related_links) + '\n</ul>\n</div>\n'
                    content += f'\n{related_content_html}'

            html += f'''
        <div id="section-{node["id"]}" class="content-section">
            <h1>{node["title"]}</h1>
            {content}
        </div>
'''
            if node.get('children'):
                html += build_content_html(node['children'], parent=node)
        return html
    
    # Generate navigation and content
    topics_section_html = build_topics_section(tree)
    content_html = build_content_html(tree)
    
    # Replace placeholders in template
    # Replace the entire Topics nav section
    topics_section_pattern = r'        <div class="nav-section">\s*<div class="nav-section-title">📚 Topics</div>\s*<button class="nav-link" onclick="showSection\(\'welcome\'\)">🏠 Home</button>\s*<!-- Dynamic content will be inserted here -->\s*</div>'
    result = re.sub(topics_section_pattern, topics_section_html, template_content, flags=re.MULTILINE | re.DOTALL)
    
    result = result.replace('<!-- Dynamic content sections will be inserted here -->', content_html)
    result = result.replace('{{ date }}', datetime.now().strftime('%B %d, %Y'))
    result = result.replace('{{ publication_title }}', publication.title)
    
    # Add tree data for breadcrumb navigation
    import json
    import base64
    tree_json = json.dumps(tree)
    tree_base64 = base64.b64encode(tree_json.encode('utf-8')).decode('utf-8')
    result = result.replace('{{ tree_data }}', tree_base64)
    
    return result


def generate_mobile_kb_html_inline(publication, tree):
    """Generate mobile-first HTML for knowledge base"""
    
    # Mobile-first CSS template
    mobile_css = """
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f8f9fa;
            padding: 0;
            margin: 0;
        }
        
        .kb-container {
            max-width: 100%;
            margin: 0 auto;
            background: white;
            min-height: 100vh;
        }
        
        .kb-header {
            background: #005a9c;
            color: white;
            padding: 1rem;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        .kb-title {
            font-size: 1.25rem;
            font-weight: 600;
            margin: 0;
        }
        
        .kb-subtitle {
            font-size: 0.875rem;
            opacity: 0.9;
            margin-top: 0.25rem;
        }
        
        .navigation {
            background: #e9ecef;
            border-bottom: 1px solid #dee2e6;
            padding: 1rem;
        }
        
        .nav-section {
            margin-bottom: 1rem;
        }
        
        .nav-section:last-child {
            margin-bottom: 0;
        }
        
        .nav-title {
            font-weight: 600;
            color: #495057;
            margin-bottom: 0.5rem;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .nav-link {
            display: block;
            padding: 0.75rem;
            color: #005a9c;
            text-decoration: none;
            background: white;
            border-radius: 6px;
            margin-bottom: 0.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            transition: all 0.2s ease;
        }
        
        .nav-link:hover {
            background: #f8f9fa;
            transform: translateY(-1px);
            box-shadow: 0 2px 6px rgba(0,0,0,0.15);
        }
        
        .nav-link:active {
            transform: translateY(0);
        }
        
        .nav-link.sub-item {
            margin-left: 1rem;
            background: #f8f9fa;
            border-left: 3px solid #005a9c;
        }
        
        .content-section {
            display: none;
            padding: 1.5rem;
            animation: fadeIn 0.3s ease-in;
        }
        
        .content-section.active {
            display: block;
        }
        
        .content-section h1,
        .content-section h2,
        .content-section h3,
        .content-section h4,
        .content-section h5,
        .content-section h6 {
            color: #112E51;
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
            line-height: 1.3;
        }
        
        .content-section h1 {
            font-size: 1.5rem;
            border-bottom: 2px solid #005a9c;
            padding-bottom: 0.5rem;
            margin-top: 0;
        }
        
        .content-section h2 {
            font-size: 1.25rem;
            color: #005a9c;
        }
        
        .content-section h3 {
            font-size: 1.1rem;
        }
        
        .content-section p {
            margin-bottom: 1rem;
            line-height: 1.7;
        }
        
        .content-section ul,
        .content-section ol {
            margin-bottom: 1rem;
            padding-left: 1.5rem;
        }
        
        .content-section li {
            margin-bottom: 0.5rem;
        }
        
        .content-section code {
            background: #f8f9fa;
            padding: 0.25rem 0.5rem;
            border-radius: 3px;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 0.875rem;
        }
        
        .content-section pre {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 6px;
            overflow-x: auto;
            margin-bottom: 1rem;
            border: 1px solid #e9ecef;
        }
        
        .content-section pre code {
            background: none;
            padding: 0;
        }
        
        .content-section blockquote {
            border-left: 4px solid #005a9c;
            padding-left: 1rem;
            margin: 1rem 0;
            font-style: italic;
            color: #6c757d;
        }
        
        .content-section table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 1rem;
            font-size: 0.9rem;
        }
        
        .content-section th,
        .content-section td {
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }
        
        .content-section th {
            background: #f8f9fa;
            font-weight: 600;
            color: #495057;
        }
        
        .back-to-nav {
            background: #6c757d;
            color: white;
            border: none;
            padding: 0.75rem 1rem;
            border-radius: 6px;
            margin-bottom: 1rem;
            cursor: pointer;
            font-size: 0.9rem;
            transition: background 0.2s ease;
        }
        
        .back-to-nav:hover {
            background: #5a6268;
        }
        
        .footer {
            background: #f8f9fa;
            padding: 1rem;
            text-align: center;
            color: #6c757d;
            font-size: 0.8rem;
            border-top: 1px solid #e9ecef;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Tablet optimizations */
        @media (min-width: 768px) {
            .kb-container {
                max-width: 800px;
            }
            
            .kb-title {
                font-size: 1.5rem;
            }
            
            .content-section {
                padding: 2rem;
            }
            
            .navigation {
                padding: 1.5rem;
            }
        }
        
        /* Desktop optimizations (still mobile-first) */
        @media (min-width: 1024px) {
            .kb-container {
                max-width: 900px;
            }
            
            .content-section h1 {
                font-size: 1.75rem;
            }
        }
        
        /* iOS Safari specific fixes */
        @supports (-webkit-touch-callout: none) {
            .kb-header {
                -webkit-backdrop-filter: blur(20px);
                backdrop-filter: blur(20px);
            }
        }
        
        /* High contrast mode support */
        @media (prefers-contrast: high) {
            .nav-link {
                border: 1px solid #000;
            }
            
            .kb-header {
                border-bottom: 2px solid #000;
            }
        }
        
        /* Dark mode support */
        @media (prefers-color-scheme: dark) {
            body {
                background: #1a1a1a;
                color: #e0e0e0;
            }
            
            .kb-container {
                background: #2d2d2d;
            }
            
            .navigation {
                background: #3a3a3a;
                border-bottom-color: #555;
            }
            
            .nav-link {
                background: #4a4a4a;
                color: #87ceeb;
            }
            
            .nav-link:hover {
                background: #5a5a5a;
            }
            
            .content-section h1,
            .content-section h2,
            .content-section h3,
            .content-section h4,
            .content-section h5,
            .content-section h6 {
                color: #f0f0f0;
            }
            
            .content-section h2 {
                color: #87ceeb;
            }
            
            .content-section code,
            .content-section pre {
                background: #3a3a3a;
                color: #e0e0e0;
            }
            
            .footer {
                background: #3a3a3a;
                color: #b0b0b0;
            }
        }
    </style>
    """
    
    # JavaScript for navigation
    mobile_js = """
    <script>
        function showSection(sectionId) {
            // Hide all sections
            const sections = document.querySelectorAll('.content-section');
            sections.forEach(section => {
                section.classList.remove('active');
            });
            
            // Show navigation if going back to nav
            const nav = document.querySelector('.navigation');
            if (sectionId === 'nav') {
                nav.style.display = 'block';
                return;
            }
            
            // Hide navigation and show selected section
            nav.style.display = 'none';
            const targetSection = document.getElementById(sectionId);
            if (targetSection) {
                targetSection.classList.add('active');
                window.scrollTo(0, 0);
            }
        }
        
        function goBackToNav() {
            showSection('nav');
        }
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            // Show navigation by default
            showSection('nav');
        });
    </script>
    """
    
    # Build navigation HTML
    def build_nav_html(nodes, level=0):
        html = ""
        for node in nodes:
            css_class = "nav-link sub-item" if level > 0 else "nav-link"
            html += f'<a href="#" class="{css_class}" onclick="showSection(\'section-{node["id"]}\')">{node["title"]}</a>\n'
            if node["children"]:
                html += build_nav_html(node["children"], level + 1)
        return html
    
    # Build content HTML
    def build_content_html(nodes):
        html = ""
        for node in nodes:
            # Convert markdown content to HTML (basic conversion)
            content_html = convert_markdown_to_html(node["content"])
            html += f'''
            <div id="section-{node["id"]}" class="content-section">
                <button class="back-to-nav" onclick="goBackToNav()">← Back to Navigation</button>
                <h1>{node["title"]}</h1>
                {content_html}
            </div>
            '''
            if node["children"]:
                html += build_content_html(node["children"])
        return html
    
    # Generate the complete HTML
    nav_html = build_nav_html(tree)
    content_html = build_content_html(tree)
    
    current_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    
    html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="apple-mobile-web-app-title" content="{publication.title}">
    <title>{publication.title} - Mobile Knowledge Base</title>
    {mobile_css}
</head>
<body>
    <div class="kb-container">
        <header class="kb-header">
            <h1 class="kb-title">{publication.title}</h1>
            <p class="kb-subtitle">Mobile Knowledge Base</p>
        </header>
        
        <nav class="navigation">
            <div class="nav-section">
                <div class="nav-title">Topics</div>
                {nav_html}
            </div>
        </nav>
        
        {content_html}
        
        <footer class="footer">
            Generated on {current_time}<br>
            Optimized for mobile devices
        </footer>
    </div>
    
    {mobile_js}
</body>
</html>'''
    
    return html_template

@pubs_bp.route('/<int:pub_id>/export/pdf', methods=['GET'])
def export_pdf(pub_id):
    """Export publication as PDF with optional formatting configuration and background image"""
    pub = Publication.query.get_or_404(pub_id)
    
    try:
        # Get format configuration from query parameter
        config_type = request.args.get('format', 'default')
        
        # Get optional background image path from query parameter
        background_image = request.args.get('background_image')
        background_image_path = None
        
        if background_image:
            # Build path to background image (assumes images are in a backgrounds folder)
            backgrounds_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'backgrounds')
            background_image_path = os.path.join(backgrounds_dir, background_image)
            
            # Security check: ensure the file exists and is an image
            if not (os.path.exists(background_image_path) and 
                   background_image.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))):
                background_image_path = None
        
        # Validate config type
        valid_configs = ['default', 'corporate', 'academic', 'compact', 'organization']
        if config_type not in valid_configs:
            config_type = 'default'
            config_type = 'default'
        
        # Build the hierarchical structure
        def serialize_node(node):
            topic_data = node.topic.to_dict() if node.topic else {'title': 'Unknown', 'content': ''}
            return {
                'id': node.id,
                'topic_id': node.topic_id,
                'title': topic_data.get('title', 'Untitled'),
                'content': topic_data.get('content', ''),
                'position': node.position,
                'children': sorted([serialize_node(c) for c in node.children],
                                 key=lambda x: x['position'])
            }
        
        top_nodes = [n for n in pub.nodes if n.parent_id is None]
        tree = sorted([serialize_node(n) for n in top_nodes],
                      key=lambda x: x['position'])
        
        # Generate PDF with specified configuration and optional background image
        pdf_buffer = generate_pdf(pub, tree, config_type, background_image_path)
        
        response = make_response(pdf_buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="{pub.title}_{config_type}.pdf"'
        
        pdf_buffer.close()
        return response
        
    except Exception as e:
        # Fallback to error message if PDF generation fails
        error_html = f"""
        <html>
        <head>
            <title>PDF Export Error - {pub.title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; }}
                .error {{ background: #f8d7da; border: 1px solid #f5c6cb; padding: 15px; border-radius: 5px; color: #721c24; }}
                .config-info {{ background: #d1ecf1; border: 1px solid #bee5eb; padding: 15px; border-radius: 5px; color: #0c5460; margin: 15px 0; }}
                .button {{ display: inline-block; margin-top: 15px; padding: 10px 20px; background: #00796B; color: white; text-decoration: none; border-radius: 3px; }}
            </style>
        </head>
        <body>
            <div class="error">
                <h2>PDF Export Error</h2>
                <p>Unable to generate PDF for "<strong>{pub.title}</strong>" with format "<strong>{config_type}</strong>".</p>
                <p>Error: {str(e)}</p>
            </div>
            <div class="config-info">
                <h3>Available PDF Formats:</h3>
                <ul>
                    <li><strong>default</strong> - Standard formatting</li>
                    <li><strong>corporate</strong> - Formal business document style</li>
                    <li><strong>academic</strong> - Academic paper formatting</li>
                    <li><strong>compact</strong> - Condensed layout for dense content</li>
                </ul>
                <p>Usage: Add <code>?format=corporate</code> to the URL</p>
                <p>Example: <code>/api/publications/{pub_id}/export/pdf?format=corporate</code></p>
                <a href="/api/publications/{pub_id}/export/mobile-kb" class="button">Export as Mobile Knowledge Base</a>
            </div>
        </body>
        </html>
        """
        
        response = make_response(error_html)
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        return response

def generate_pdf(publication, tree, config_type='default', background_image_path=None):
    """Generate PDF document from publication tree with configurable formatting and optional background image"""
    buffer = io.BytesIO()
    
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
        default_bg_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'backgrounds', 'SC Cover Background.png')
        if os.path.exists(default_bg_path):
            background_image_path = default_bg_path
            print(f"DEBUG: Using default background image: {background_image_path}")
    
    # Create PDF document with background image support
    print(f"DEBUG: Creating PDF document for publication: {publication.title}, id: {publication.id}")
    if background_image_path and os.path.exists(background_image_path):
        print("DEBUG: Using BackgroundImageDocTemplate")
        doc = BackgroundImageDocTemplate(
            buffer,
            background_image_path=background_image_path,
            publication=publication,
            pagesize=config.PAGE_SIZE,
            rightMargin=config.MARGINS['right'],
            leftMargin=config.MARGINS['left'],
            topMargin=config.MARGINS['top'],
            bottomMargin=config.MARGINS['bottom']
        )
    else:
        # Use HeaderDocTemplate for PDFs with headers but no background image
        print("DEBUG: Using HeaderDocTemplate")
        doc = HeaderDocTemplate(
            buffer,
            publication=publication,
            pagesize=config.PAGE_SIZE,
            rightMargin=config.MARGINS['right'],
            leftMargin=config.MARGINS['left'],
            topMargin=config.MARGINS['top'],
            bottomMargin=config.MARGINS['bottom']
        )
    
    # Build content
    story = []
    base_styles = config.get_base_styles()
    
    # Start with title page template
    story.append(NextPageTemplate('title_page'))
    
    # Create styles using configuration
    title_style = config.create_title_style(base_styles)
    subtitle_style = config.create_subtitle_style(base_styles)
    
    # Title page content - move title down about 1" and align to right margin
    story.append(Spacer(1, 84))  # Move down ~1" (72pt)
    
    if hasattr(doc, 'background_image_path') and doc.background_image_path:
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
            # Estimate page number (simplified - in real implementation would need actual page tracking)
            page_num = page_counter['value']
            page_counter['value'] += max(1, len(node.get('content', '')) // 2000)  # Rough page estimation
            
            title_text = node['title']
            font_size = config.FONT_SIZES['toc'] if level == 0 else max(9, config.FONT_SIZES['toc'] - (level * 0.5))
            
            if level == 0:
                # Level 0: Simple title and page number, bold styling, aligned to 1-inch margin
                toc_data = [[title_text, str(page_num)]]
                
                # Create table with proper margin alignment
                toc_table = Table(toc_data, colWidths=[title_width, page_num_width])
                toc_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (0, 0), config.FONTS['heading']),
                    ('FONTNAME', (1, 0), (1, 0), config.FONTS['body']),
                    ('FONTSIZE', (0, 0), (-1, -1), config.FONT_SIZES['toc']),
                    ('TEXTCOLOR', (0, 0), (-1, -1), config.COLORS['heading']),
                    ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                    ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 2),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),  # No padding - align to document margin
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ]))
                
            else:
                # Nested levels: Clean indented entries with consistent right alignment
                indent_width = level * config.INDENTS['toc_per_level']
                
                # Create indented title using spaces
                spaces_for_indent = " " * int(indent_width / 4)  # Space-based left indentation
                clean_title = f"{spaces_for_indent}{title_text}"
                
                toc_data = [[clean_title, str(page_num)]]
                
                # Use SAME column widths as level 0 to ensure page numbers align to right margin
                toc_table = Table(toc_data, colWidths=[title_width, page_num_width])
                toc_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (0, 0), config.FONTS['body']),
                    ('FONTNAME', (1, 0), (1, 0), config.FONTS['body']),
                    ('FONTSIZE', (0, 0), (-1, -1), font_size),
                    ('TEXTCOLOR', (0, 0), (-1, -1), config.COLORS['text']),
                    ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                    ('ALIGN', (1, 0), (1, 0), 'RIGHT'),  # Page numbers right-aligned to same position as level 0
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                    ('TOPPADDING', (0, 0), (-1, -1), 2),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),  # No padding - maintain document margin alignment
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),  # No extra right padding to maintain alignment
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
            # Create proper heading hierarchy based on collection structure
            heading_text = node['title']
            
            # Use config-based heading styles
            current_heading_style = config.create_heading_style(base_styles, level)
            
            story.append(Paragraph(heading_text, current_heading_style))
            
            # Add content with proper indentation for hierarchy
            if node['content']:
                # Convert markdown-like content to paragraphs
                content_paragraphs = convert_markdown_to_pdf_paragraphs(node['content'])
                for para in content_paragraphs:
                    # Create content style that matches the hierarchy level
                    level_content_style = config.create_content_style(base_styles, level)
                    story.append(Paragraph(para, level_content_style))
            
            # Add spacing after content
            story.append(Spacer(1, 8))
            
            # Recursively add children with increased level
            if node['children']:
                add_content_nodes(node['children'], level + 1)
                
                # Add extra spacing after a section with children
                if level < 2:  # Only for top-level sections
                    story.append(Spacer(1, 16))
    
    add_content_nodes(tree)
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def convert_markdown_to_pdf_paragraphs(text):
    """Convert markdown-like text to PDF paragraphs with better hierarchy support"""
    if not text:
        return [""]
    
    lines = text.split('\n')
    paragraphs = []
    current_paragraph = []
    in_list = False
    list_items = []
    
    for line in lines:
        stripped = line.strip()
        
        # Handle headers (these will be rendered as bold text within content)
        if stripped.startswith('#'):
            # Finish any current paragraph or list
            if current_paragraph:
                paragraphs.append(' '.join(current_paragraph))
                current_paragraph = []
            if in_list:
                # Create a proper list paragraph
                list_content = '<br/>'.join([f"• {item}" for item in list_items])
                paragraphs.append(list_content)
                list_items = []
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
        elif stripped.startswith('-') or stripped.startswith('*'):
            if current_paragraph:
                paragraphs.append(' '.join(current_paragraph))
                current_paragraph = []
            
            bullet_text = stripped[1:].strip()
            list_items.append(bullet_text)
            in_list = True
            
        # Handle numbered lists
        elif any(stripped.startswith(f"{i}. ") for i in range(1, 10)):
            if current_paragraph:
                paragraphs.append(' '.join(current_paragraph))
                current_paragraph = []
            if in_list and list_items:
                # Finish the bullet list first
                list_content = '<br/>'.join([f"• {item}" for item in list_items])
                paragraphs.append(list_content)
                list_items = []
            
            numbered_text = stripped[3:].strip()  # Remove "1. " etc.
            list_items.append(numbered_text)
            in_list = True
            
        # Handle empty lines (paragraph breaks)
        elif not stripped:
            if current_paragraph:
                paragraphs.append(' '.join(current_paragraph))
                current_paragraph = []
            if in_list:
                # Finish the current list
                if list_items:
                    list_content = '<br/>'.join([f"• {item}" for item in list_items])
                    paragraphs.append(list_content)
                    list_items = []
                in_list = False
                
        # Regular text
        else:
            if in_list:
                # Finish the current list first
                if list_items:
                    list_content = '<br/>'.join([f"• {item}" for item in list_items])
                    paragraphs.append(list_content)
                    list_items = []
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
            # Remove div, span, and other structural HTML tags but keep their content
            formatted_line = re.sub(r'</?div[^>]*>', '', formatted_line)
            formatted_line = re.sub(r'</?span[^>]*>', '', formatted_line)
            formatted_line = re.sub(r'</?p[^>]*>', '', formatted_line)  # Remove paragraph tags since we're already in a paragraph
            
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
                        if src.startswith('/images/'):
                            # Convert /images/ path to absolute path
                            image_filename = src[8:]  # Remove /images/ prefix
                            static_images_dir = os.path.join(current_app.config['STATIC_FOLDER'], 'images')
                            absolute_src = os.path.join(static_images_dir, image_filename)
                            src = absolute_src
                        elif src.startswith('/static/images/'):
                            # Convert /static/images/ path to absolute path
                            image_filename = src[15:]  # Remove /static/images/ prefix
                            static_images_dir = os.path.join(current_app.config['STATIC_FOLDER'], 'images')
                            absolute_src = os.path.join(static_images_dir, image_filename)
                            src = absolute_src
                    
                    # Extract width and height if present
                    width_match = re.search(r'width="([^"]*)"', img_tag)
                    height_match = re.search(r'height="([^"]*)"', img_tag)
                    
                    # Build clean img tag with only supported attributes
                    clean_attrs = []
                    if src:
                        clean_attrs.append(f'src="{src}"')
                    if width_match:
                        clean_attrs.append(f'width="{width_match.group(1)}"')
                    if height_match:
                        clean_attrs.append(f'height="{height_match.group(1)}"')
                    
                    return f'<img {" ".join(clean_attrs)}/>'
                
                formatted_line = re.sub(r'<img[^>]*>', clean_img_tag, formatted_line)
            
            # Clean up extra whitespace and empty content
            formatted_line = formatted_line.strip()
            if formatted_line:  # Only add non-empty lines
                current_paragraph.append(formatted_line)
    
    # Add any remaining content
    if current_paragraph:
        paragraphs.append(' '.join(current_paragraph))
    if in_list and list_items:
        list_content = '<br/>'.join([f"• {item}" for item in list_items])
        paragraphs.append(list_content)
    
    return [p for p in paragraphs if p.strip()]

def convert_image_to_base64(image_src):
    """Convert image path to base64 data URL for standalone HTML"""
    try:
        # Handle both /images/ paths and direct paths
        if image_src.startswith('/images/'):
            image_path = image_src[8:]  # Remove /images/ prefix
        else:
            image_path = image_src
            
        # Build full path to image file
        static_images_dir = os.path.join(current_app.config['STATIC_FOLDER'], 'images')
        full_image_path = os.path.join(static_images_dir, image_path)
        
        if os.path.exists(full_image_path):
            # Get mime type
            mime_type, _ = mimetypes.guess_type(full_image_path)
            if not mime_type:
                mime_type = 'image/jpeg'  # Default fallback
                
            # Read and encode image
            with open(full_image_path, 'rb') as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
                return f"data:{mime_type};base64,{image_data}"
        else:
            print(f"Warning: Image not found at {full_image_path}")
            return image_src  # Return original if file not found
            
    except Exception as e:
        print(f"Error converting image {image_src} to base64: {str(e)}")
        return image_src  # Return original on error

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
    
    # Lists
    lines = html.split('\n')
    in_list = False
    result_lines = []
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('- ') or stripped.startswith('* '):
            if not in_list:
                result_lines.append('<ul>')
                in_list = True
            result_lines.append(f'<li>{stripped[2:]}</li>')
        elif stripped.startswith(('1. ', '2. ', '3. ', '4. ', '5. ', '6. ', '7. ', '8. ', '9. ')):
            if not in_list:
                result_lines.append('<ol>')
                in_list = True
            result_lines.append(f'<li>{stripped[3:]}</li>')
        else:
            if in_list:
                result_lines.append('</ul>' if result_lines[-2].startswith('<li>') else '</ol>')
                in_list = False
            if stripped:
                # Don't wrap images in paragraphs
                if stripped.startswith('<img') or '<img' in stripped:
                    result_lines.append(stripped)
                else:
                    result_lines.append(f'<p>{stripped}</p>')
            else:
                result_lines.append('<br>')
    
    if in_list:
        result_lines.append('</ul>')
    
    return '\n'.join(result_lines)
