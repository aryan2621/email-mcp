import os
import json
import logging
from typing import List, Dict
from .template import ComprehensiveDocTemplate
from .charts import add_charts_to_story
from .signature import add_signature_to_story
from .tables import add_tables_to_story
from .images import add_images_to_story
from .text import add_formatted_text_to_story
from .lists import add_lists_to_story
from .breaks import add_page_breaks_to_story
from .sections import add_sections_with_breaks
from reportlab.platypus import Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from .extra_components import (
    add_cover_page,
    add_executive_summary_box,
    add_footnotes_to_story,
    add_endnotes_section,
    add_form_fields,
    add_appendix_section,
    add_multi_column_content,
    add_text_boxes_to_story,
    add_callout_boxes,
    add_qr_codes_to_story
)

logger = logging.getLogger('pdf-mcp')

def create_enhanced_pdf_with_all_components(
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
    background_config: Dict = None,
    border_config: Dict = None,
) -> str:
    try:
        # Validate watermark config
        if watermark_config:
            watermark_type = watermark_config.get('type')
            if watermark_type not in ['text', 'image']:
                return json.dumps({'status': 'error', 'message': 'Invalid watermark type'}, indent=2)
            
            if watermark_type == 'text' and not watermark_config.get('text'):
                return json.dumps({'status': 'error', 'message': 'Text watermark requires text field'}, indent=2)
            
            if watermark_type == 'image' and not watermark_config.get('url'):
                return json.dumps({'status': 'error', 'message': 'Image watermark requires url field'}, indent=2)
        
        # Create organized directory
        base_dir = os.path.join(os.getcwd(), 'generated_docs')
        pdfs_dir = os.path.join(base_dir, 'pdfs')
        os.makedirs(pdfs_dir, exist_ok=True)
        
        pdf_filename = os.path.join(pdfs_dir, os.path.basename(filename))
        
        # Create document with proper margins
        margin_adjustment = 0
        if border_config:
            border_margin = border_config.get('margin_inches',0.2) * 72
            margin_adjustment = border_margin + 5  # Less extra padding
        

        doc = ComprehensiveDocTemplate(
            pdf_filename,
            pagesize=letter,
            topMargin=(40 + margin_adjustment) if header_config else (40 + margin_adjustment),
            bottomMargin=(40 + margin_adjustment) if footer_config else (40 + margin_adjustment),
            leftMargin=40 + margin_adjustment,
            rightMargin=40 + margin_adjustment,
            header_config=header_config,
            footer_config=footer_config,
            watermark_config=watermark_config,
            background_config=background_config,
            border_config=border_config
        )
        story = []
        if cover_config:
            story = add_cover_page(story, cover_config)

        styles = getSampleStyleSheet()
        
        # 1. Add title with better formatting
        if title.strip():
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Title'],
                fontSize=20,
                fontName='Helvetica-Bold',
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.black,
                leading=24
            )
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 30))
        
        # 2. Add headings with content
        if headings_content:
            for item in headings_content:
                level = item.get('level', 1)
                text = item.get('text', '').strip()
                content = item.get('content', '').strip()
                
                if text:
                    # Better heading styles
                    font_sizes = {1: 16, 2: 14, 3: 12, 4: 11, 5: 10, 6: 10}
                    font_size = font_sizes.get(level, 12)
                    
                    heading_style = ParagraphStyle(
                        f'CustomHeading{level}',
                        parent=styles['Normal'],
                        fontSize=font_size,
                        fontName='Helvetica-Bold',
                        spaceBefore=20 if level == 1 else 15,
                        spaceAfter=10,
                        textColor=colors.black,
                        alignment=TA_LEFT
                    )
                    
                    story.append(Paragraph(text, heading_style))
                
                if content:
                    content_style = ParagraphStyle(
                        'ContentText',
                        parent=styles['Normal'],
                        fontSize=11,
                        fontName='Helvetica',
                        spaceBefore=5,
                        spaceAfter=15,
                        textColor=colors.black,
                        alignment=TA_LEFT,
                        leading=14
                    )
                    story.append(Paragraph(content, content_style))
        
        # 3. Add charts with proper spacing
        if charts_config:
            story = add_charts_to_story(story, charts_config)
        
        # 4. Add tables
        if tables_config:
            story = add_tables_to_story(story, tables_config)
        
        # 5. Add images
        if images_config:
            story = add_images_to_story(story, images_config)
        
        # 6. Add formatted text
        if formatted_content:
            story = add_formatted_text_to_story(story, formatted_content)
        
        # 7. Add lists
        if lists_config:
            story = add_lists_to_story(story, lists_config)
        
        # 8. Add colored text (simplified)
        if colored_content:
            story.append(Spacer(1, 20))
            story.append(Paragraph('<b>Performance Highlights:</b>', styles['Normal']))
            story.append(Spacer(1, 10))
            
            for item in colored_content:
                text = item.get('text', '').strip()
                color = item.get('color', 'black')
                style_type = item.get('style', 'normal')
                
                if text:
                    formatted_text = text
                    
                    # Handle colors
                    if color.startswith('#'):
                        formatted_text = f'<font color="{color}">{formatted_text}</font>'
                    else:
                        color_map = {
                            'red': '#FF0000', 'blue': '#0000FF', 'green': '#008000',
                            'purple': '#800080', 'orange': '#FFA500', 'black': '#000000'
                        }
                        hex_color = color_map.get(color.lower(), '#000000')
                        formatted_text = f'<font color="{hex_color}">{formatted_text}</font>'
                    
                    # Apply styles
                    if 'bold' in style_type:
                        formatted_text = f'<b>{formatted_text}</b>'
                    if 'italic' in style_type:
                        formatted_text = f'<i>{formatted_text}</i>'
                    
                    story.append(Paragraph(formatted_text, styles['Normal']))
                    story.append(Spacer(1, 8))
            
            story.append(Spacer(1, 15))
        
        # 9. Add additional content
        if additional_content.strip():
            story.append(Spacer(1, 20))
            story.append(Paragraph('<b>Executive Summary:</b>', styles['Normal']))
            story.append(Spacer(1, 10))
            
            content_style = ParagraphStyle(
                'FinalContent',
                parent=styles['Normal'],
                fontSize=11,
                fontName='Helvetica',
                spaceBefore=5,
                spaceAfter=15,
                textColor=colors.black,
                alignment=TA_LEFT,
                leading=14
            )
            story.append(Paragraph(additional_content, content_style))
        
        # 10. Add signature at the end
        if signature_config:
            story = add_signature_to_story(story, signature_config)
        
        # Add footnotes
        if footnotes_config:
            story = add_footnotes_to_story(story, footnotes_config)
        
        # Add endnotes section
        if endnotes_config:
            story = add_endnotes_section(story, endnotes_config)
        
        # Add form fields
        if form_config:
            story = add_form_fields(story, form_config)
        
        # Add appendix section
        if appendix_config:
            story = add_appendix_section(story, appendix_config)
        
        if page_breaks_config:
            story = add_page_breaks_to_story(story, page_breaks_config)
        
        if sections_config:
            story = add_sections_with_breaks(story, sections_config)
        
        if summary_config:
            story = add_executive_summary_box(story, summary_config)
        
        # Add multi-column content (newsletter-style)
        if multi_column_config:
            story = add_multi_column_content(story, multi_column_config)
        
        if textbox_config:
            story = add_text_boxes_to_story(story, textbox_config)
        
        if callout_config:
            story = add_callout_boxes(story, callout_config)
        
        if qr_config:
            story = add_qr_codes_to_story(story, qr_config)
        
        # Build PDF
        doc.build(story)
        
        # Prepare result
        components_used = []
        if title.strip(): 
            components_used.append("title")
        if headings_content: 
            components_used.append(f"headings ({len(headings_content)})")
        if charts_config: 
            components_used.append(f"charts ({len(charts_config)})")
        if tables_config: 
            components_used.append(f"tables ({len(tables_config)})")
        if images_config: 
            components_used.append(f"images ({len(images_config)})")
        if background_config:
            components_used.append("background")
        if border_config:
            components_used.append("border")
        if formatted_content: 
            components_used.append(f"formatted_text ({len(formatted_content)})")
        if lists_config: 
            components_used.append(f"lists ({len(lists_config)})")
        if colored_content: 
            components_used.append(f"colored_text ({len(colored_content)})")
        if watermark_config: 
            components_used.append(f"watermark ({watermark_config.get('type', 'unknown')})")
        if signature_config: 
            components_used.append("signature")
        if header_config: 
            components_used.append("header")
        if footer_config: 
            components_used.append("footer")
        if additional_content.strip(): 
            components_used.append("additional_content")
        if footnotes_config:
            components_used.append("footnotes")
        if endnotes_config:
            components_used.append("endnotes")
        if form_config:
            components_used.append("form")
        if appendix_config:
            components_used.append("appendix")
        if page_breaks_config:
            components_used.append("page_breaks")
        if sections_config:
            components_used.append("sections")
        if cover_config:
            components_used.append("cover")
        if multi_column_config:
            components_used.append(f"multi_column ({len(multi_column_config)})")
        if textbox_config:
            components_used.append(f"textbox ({len(textbox_config)})")
        if callout_config:
            components_used.append(f"callout ({len(callout_config)})")
        if qr_config:
            components_used.append(f"qr ({len(qr_config)})")
        if summary_config:
            components_used.append("summary")
        result = {
            'status': 'success',
            'filename': pdf_filename,
            'original_filename': filename,
            'charts_directory': os.path.join(base_dir, 'charts'),
            'images_directory': os.path.join(base_dir, 'images'),
            'pdfs_directory': pdfs_dir,
            'components_used': components_used,
            'size_bytes': os.path.getsize(pdf_filename)
        }
        
        logger.info(f"Created enhanced PDF: {pdf_filename}")
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error creating enhanced PDF: {str(e)}")
        return json.dumps({'status': 'error', 'message': str(e)}, indent=2)