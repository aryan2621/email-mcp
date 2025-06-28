#!/usr/bin/env python3
"""
PDF MCP Tool Methods (refactored)
"""

import logging
from typing import List, Dict
from app import mcp
from .utils.main import create_enhanced_pdf_with_all_components
from .manipulation import merge_pdfs_util, split_pdf_util, pdf_info_util

logger = logging.getLogger('advanced-pdf-mcp')

@mcp.tool()
def create_pdf_with_components(
    filename: str,
    title: str = "",
    headings_content: List[Dict] = None,
    colored_content: List[Dict] = None,
    watermark_config: Dict = None,
    signature_config: Dict = None,
    tables_config: List[Dict] = None,
    images_config: List[Dict] = None,
    formatted_content: List[Dict] = None,
    lists_config: List[Dict] = None,
    charts_config: List[Dict] = None,
    header_config: Dict = None,
    footer_config: Dict = None,
    additional_content: str = "",
    cover_config: Dict = None,
    summary_config: Dict = None,
    footnotes_config: List[Dict] = None,
    endnotes_config: List[Dict] = None,
    form_config: List[Dict] = None,
    appendix_config: List[Dict] = None,
    page_breaks_config: List[int] = None,
    sections_config: List[List[Dict]] = None,
    multi_column_config: List[Dict] = None,
    textbox_config: List[Dict] = None,
    callout_config: List[Dict] = None,
    qr_config: List[Dict] = None,
    border_config: Dict = None,
    background_config: Dict = None,
):
    """Create comprehensive PDF with all advanced components
    
    Args:
        filename: Output PDF filename (e.g., "document.pdf")
        title: Main document title

        headings_content: List of heading dicts, each with:
            - level (int, 1-6)
            - text (str)
            - content (str, optional)
            Example: [{"level": 1, "text": "Main Heading", "content": "Intro..."}]

        colored_content: List of dicts for colored text:
            - text (str)
            - color (str, e.g. '#FF0000' or 'red')
            - style (str, e.g. 'bold', 'italic', 'bold-italic', 'normal')
            Example: [{"text": "Red text", "color": "red", "style": "bold"}]

        watermark_config: Dict for watermark:
            - type: 'text' or 'image'
            - text: (str, for text type)
            - url: (str, for image type)
            - opacity: (float, 0-1)
            - rotation: (int, degrees)
            - color: (str, for text)
            - font_size: (int, for text)
            - width, height: (int, for image)
            Example: {"type": "text", "text": "CONFIDENTIAL", "opacity": 0.2, ...}

        signature_config: Dict for digital signature:
            - text (str)
            - date (str, 'YYYY-MM-DD')
            - position (str: 'bottom-right', 'bottom-left', 'top-right', 'top-left', 'center')
            - font_size (int)
            Example: {"text": "Signed by...", "date": "2024-01-01", ...}

        tables_config: List of dicts for tables:
            - data (list of lists)
            - style (dict): header_background, alternate_rows, border_color, grid
            - column_widths (list of int)
            - title (str, optional)
            Example: [{"data": [[...]], "style": {"header_background": "#CCC"}, ...}]

        images_config: List of dicts for images:
            - url (str, for remote)
            - path (str, for local)
            - width, height (int)
            - caption (str, optional)
            - alignment (str: 'left', 'center', 'right')
            Example: [{"url": "...", "width": 200, "alignment": "center"}]

        formatted_content: List of dicts for advanced text:
            - text (str)
            - bold, italic, underline (bool)
            - color (str, optional)
            - link (str, optional)
            Example: [{"text": "Link", "link": "https://...", "color": "#00F"}]

        lists_config: List of dicts for lists:
            - type (str: 'bullet' or 'number')
            - items (list of str)
            - title (str, optional)
            Example: [{"type": "bullet", "items": ["A", "B"]}]

        header_config: Dict for page header:
            - text (str)
            - alignment (str: 'left', 'center', 'right')
            Example: {"text": "Header", "alignment": "center"}

        footer_config: Dict for page footer:
            - text (str)
            - alignment (str: 'left', 'center', 'right')
            - show_page_number (bool)
            Example: {"text": "Footer", "show_page_number": True}

        additional_content: (str) Plain text to add at the end

        cover_config: Dict for cover page:
            - logo_path, logo_url, or logo (str)
            - title (str)
            - subtitle (str, optional)
            - author (str, optional)
            - date (str, 'YYYY-MM-DD', optional)
            - company (str, optional)
            - contact (str, optional)
            Example: {"logo_path": "...", "title": "Report", ...}

        summary_config: Dict for executive summary box:
            - title (str)
            - summary (str)
            Example: {"title": "Summary", "summary": "..."}

        footnotes_config: List of dicts for footnotes:
            - number (int, optional)
            - text (str)
            Example: [{"number": 1, "text": "Footnote."}]

        endnotes_config: List of dicts for endnotes:
            - number (int, optional)
            - text (str)
            Example: [{"number": 1, "text": "Endnote."}]

        form_config: List of dicts for form fields:
            - label (str)
            - type (str: 'text', 'date', 'checkbox', 'signature')
            Example: [{"label": "Name", "type": "text"}]

        appendix_config: List of dicts for appendix sections:
            - title (str, optional)
            - content (str, optional)
            Example: [{"title": "Data", "content": "..."}]

        page_breaks_config: List of int indices for page breaks:
            Example: [2, 5, 10]

        sections_config: List of sections (each is a list of ReportLab elements or strings):
            Example: [[Paragraph('Section 1', style)], [Paragraph('Section 2', style)]]

        charts_config: List of dicts for charts:
            - type (str: 'bar', 'pie', 'line', 'histogram', 'scatter', 'hbar')
            - title (str)
            - data (dict):
                - For 'bar': labels, values, colors, x_label, y_label, show_values
                - For 'pie': labels, values, colors, explode, start_angle
                - For 'line': x, y (list or list of lists), line_labels, colors
                - For 'histogram': values, bins, color, show_stats
                - For 'scatter': x, y, colors, sizes, trend_line
                - For 'hbar': labels, values, show_values
            - width, height (int, optional, for matplotlib)
            - pdf_width, pdf_height (int, optional, for PDF)
            - caption (str, optional)
            Example: [{"type": "bar", "title": "Sales", "data": {"labels": [...], ...}}]

        multi_column_config: List of dicts for multi-column sections:
            - columns (list of dicts with 'content' str)
            - spacing (int, optional)
            Example: [{"columns": [{"content": "A"}, {"content": "B"}], "spacing": 16}]

        textbox_config: List of dicts for text boxes:
            - text (str)
            - background_color (str, optional)
            - border_color (str, optional)
            Example: [{"text": "Notice", "background_color": "#F0F0F0"}]

        callout_config: List of dicts for callout boxes:
            - title (str, optional)
            - text (str)
            - type (str: 'info', 'warning', 'success', 'error')
            Example: [{"title": "Note", "text": "...", "type": "warning"}]

        qr_config: List of dicts for QR codes:
            - data (str)
            - size (int, optional)
            - caption (str, optional)
            Example: [{"data": "https://...", "size": 100, "caption": "Visit"}]

        border_config: Dict for page border:
            - enabled (bool, optional)
            - margin_inches (float)
            - color (str)
            - width (float)
            - style (str: 'single', 'double', 'decorative')
            Example: {"enabled": True, "margin_inches": 1.5, "color": "#333", ...}

        background_config: Dict for page background:
            - color (str, optional)
            - gradient (dict, optional):
                - start_color (str)
                - end_color (str)
                - direction (str: 'vertical' or 'horizontal')
            Example: {"color": "#FAFAFA", "gradient": {"start_color": "#FFF", ...}}

    Returns:
        str: JSON string with creation status, components used, and file details
    """
    return create_enhanced_pdf_with_all_components(
        filename=filename,
        title=title,
        headings_content=headings_content,
        colored_content=colored_content,
        watermark_config=watermark_config,
        signature_config=signature_config,
        tables_config=tables_config,
        images_config=images_config,
        formatted_content=formatted_content,
        lists_config=lists_config,
        charts_config=charts_config,
        header_config=header_config,
        footer_config=footer_config,
        additional_content=additional_content,
        cover_config=cover_config,
        summary_config=summary_config,
        footnotes_config=footnotes_config,
        endnotes_config=endnotes_config,
        form_config=form_config,
        appendix_config=appendix_config,
        page_breaks_config=page_breaks_config,
        sections_config=sections_config,
        multi_column_config=multi_column_config,
        textbox_config=textbox_config,
        callout_config=callout_config,
        qr_config=qr_config,
        background_config=background_config,
        border_config=border_config,
    )

@mcp.tool()
def merge_pdfs(input_files: List[str], output_filename: str):
    """Merge multiple PDF files into a single PDF file
    
    Args:
        input_files: The list of PDF files to merge
        output_filename: The name of the output PDF file
    """
    return merge_pdfs_util(
        input_files=input_files,
        output_filename=output_filename
    )

@mcp.tool()
def split_pdf(input_file: str, output_directory: str, pages_per_file: int = 1):
    """Split a PDF file into multiple PDF files
    
    Args:
        input_file: The path to the input PDF file
        output_directory: The directory to save the output PDF files
        pages_per_file: The number of pages per output PDF file
    """
    return split_pdf_util(
        input_file=input_file,
        output_directory=output_directory,
        pages_per_file=pages_per_file
    )

@mcp.tool()
def pdf_info(filename: str):
    """Get information about a PDF file
    
    Args:
        filename: The path to the PDF file
    """
    return pdf_info_util(filename=filename)