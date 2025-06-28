import os
from reportlab.platypus import Paragraph, Spacer, Image, Table, TableStyle, PageBreak, Frame, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import inch
from datetime import datetime
import requests
from io import BytesIO
import qrcode

def add_cover_page(story, cover_config):
    if not cover_config:
        return story

    styles = getSampleStyleSheet()
    cover = []

    # Sophisticated logo presentation (move to top)
    logo_path = (cover_config.get('logo_path') or 
                 cover_config.get('logo_url') or 
                 cover_config.get('logo'))
    
    if logo_path:
        try:
            if logo_path.startswith(('http://', 'https://')):
                response = requests.get(logo_path, timeout=10)
                response.raise_for_status()
                logo_data = BytesIO(response.content)
                img = Image(logo_data)
            else:
                if os.path.exists(logo_path):
                    img = Image(logo_path)
                else:
                    raise Exception("Local file not found")

            # Dynamic logo sizing for premium effect
            img_width, img_height = img.imageWidth, img.imageHeight
            max_width, max_height = 250, 250  # Larger for prominence
            ratio = min(max_width / img_width, max_height / img_height)
            img.drawWidth = img_width * ratio
            img.drawHeight = img_height * ratio

            # Logo container at the top (vertical align top)
            logo_table = Table([[img]], colWidths=[6.5*inch])
            logo_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.1, 0.45, 0.65)),
                ('BOX', (0, 0), (-1, -1), 3, colors.Color(0.05, 0.25, 0.45)),
                ('INNERGRID', (0, 0), (-1, -1), 1, colors.Color(0.9, 0.9, 0.9, alpha=0.2)),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ]))
            cover.append(logo_table)
            cover.append(Spacer(1, 20))

        except Exception as e:
            print(f"Logo loading failed: {e}")
            cover.append(Spacer(1, 30))

    # Initial spacing for elegant layout (reduced, now after logo)
    # cover.append(Spacer(1, 30))  # Removed or commented out

    # Luxurious title design
    if cover_config.get('title'):
        title_text = str(cover_config['title'])
        title_style = ParagraphStyle(
            'LuxuryTitle',
            parent=styles['Title'],
            fontName='Times-Bold',
            fontSize=42,
            alignment=TA_CENTER,
            textColor=colors.Color(0.05, 0.25, 0.45),
            leading=48,
            spaceAfter=10,
            borderPadding=20,
            borderWidth=2,
            borderColor=colors.Color(0.8, 0.7, 0.4)
        )

        # Title with decorative frame (reduced paddings)
        title_content = [[Paragraph(title_text, title_style)]]
        title_table = Table(title_content, colWidths=[6.5*inch])
        title_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.95, 0.95, 0.97)),
            ('BOX', (0, 0), (-1, -1), 2, colors.Color(0.05, 0.25, 0.45)),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        cover.append(title_table)
        cover.append(Spacer(1, 15))

    # Refined subtitle
    if cover_config.get('subtitle'):
        subtitle_style = ParagraphStyle(
            'RefinedSubtitle',
            parent=styles['Normal'],
            fontName='Times-Italic',
            fontSize=22,
            alignment=TA_CENTER,
            textColor=colors.Color(0.3, 0.3, 0.3),
            leading=28,
            spaceAfter=20
        )
        subtitle_text = f"<i>{str(cover_config['subtitle'])}</i>"
        cover.append(Paragraph(subtitle_text, subtitle_style))
        cover.append(Spacer(1, 20))

    # Ornate separator with flourish
    separator_data = [['', '✦', '']]
    separator_table = Table(separator_data, colWidths=[2.5*inch, 1.5*inch, 2.5*inch])
    separator_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('FONTSIZE', (1, 0), (1, 0), 30),
        ('TEXTCOLOR', (1, 0), (1, 0), colors.Color(0.8, 0.7, 0.4)),
        ('LINEABOVE', (0, 0), (0, 0), 1.5, colors.Color(0.8, 0.7, 0.4)),
        ('LINEABOVE', (2, 0), (2, 0), 1.5, colors.Color(0.8, 0.7, 0.4)),
        ('LINEBELOW', (0, 0), (0, 0), 1.5, colors.Color(0.8, 0.7, 0.4)),
        ('LINEBELOW', (2, 0), (2, 0), 1.5, colors.Color(0.8, 0.7, 0.4)),
    ]))
    cover.append(separator_table)
    cover.append(Spacer(1, 20))

    # Premium info section
    info_items = []
    if cover_config.get('author'):
        author_style = ParagraphStyle(
            'AuthorStyle',
            parent=styles['Normal'],
            fontName='Times-Roman',
            fontSize=18,
            alignment=TA_LEFT,
            textColor=colors.Color(0.2, 0.2, 0.2),
            leading=22
        )
        author_text = f"<b>Prepared by:</b> {str(cover_config['author'])}"
        info_items.append(Paragraph(author_text, author_style))

    if cover_config.get('contact'):
        contact_style = ParagraphStyle(
            'ContactStyle',
            parent=styles['Normal'],
            fontName='Times-Roman',
            fontSize=18,
            alignment=TA_LEFT,
            textColor=colors.Color(0.2, 0.2, 0.2),
            leading=22
        )
        contact_text = f"<b>Contact:</b> {str(cover_config['contact'])}"
        info_items.append(Paragraph(contact_text, contact_style))

    # Enhanced date formatting
    if cover_config.get('date'):
        try:
            if isinstance(cover_config['date'], str):
                parsed_date = datetime.strptime(cover_config['date'], '%Y-%m-%d')
                formatted_date = parsed_date.strftime('%B %d, %Y')
            else:
                formatted_date = str(cover_config['date'])
        except ValueError:
            formatted_date = str(cover_config['date'])
    else:
        formatted_date = datetime.today().strftime('%B %d, %Y')

    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=18,
        alignment=TA_LEFT,
        textColor=colors.Color(0.2, 0.2, 0.2),
        leading=22
    )
    date_text = f"<b>Published:</b> {formatted_date}"
    info_items.append(Paragraph(date_text, date_style))

    # Elegant info box with subtle shadow (reduced paddings)
    if info_items:
        info_table = Table([[info_items]], colWidths=[6.5*inch])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.97, 0.97, 0.98)),
            ('BOX', (0, 0), (-1, -1), 1.5, colors.Color(0.05, 0.25, 0.45)),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.Color(0.9, 0.9, 0.9, alpha=0.3)),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        cover.append(info_table)

    # Luxurious footer (reduced)
    cover.append(Spacer(1, 30))

    # Wrap the cover in KeepTogether to prevent splitting
    story.append(KeepTogether(cover))
    story.append(PageBreak())
    return story

def add_executive_summary_box(story, summary_config):
    """
    Add executive summary box - FIXED VERSION
    Removes KeepTogether wrapper that was causing height calculation errors
    """
    if not summary_config:
        return story
        
    styles = getSampleStyleSheet()
    
    # Validate and extract content
    title_text = str(summary_config.get('title', '')).strip()
    summary_text = str(summary_config.get('summary', '')).strip()
    
    # Length limits to prevent oversized content
    if len(summary_text) > 1000:  # Reasonable limit
        summary_text = summary_text[:1000] + "..."
        print("Warning: Summary text truncated to prevent layout issues")
    
    if not title_text and not summary_text:
        return story
    
    try:
        # Build content as separate elements (not in KeepTogether)
        box_elements = []
        
        # Add title if provided
        if title_text:
            title_style = ParagraphStyle(
                'SummaryTitle',
                parent=styles['Heading3'],
                fontSize=14,
                fontName='Helvetica-Bold',
                spaceAfter=8,
                textColor=colors.black
            )
            box_elements.append(Paragraph(title_text, title_style))
        
        # Add summary text if provided
        if summary_text:
            summary_style = ParagraphStyle(
                'SummaryText',
                parent=styles['Normal'],
                fontSize=11,
                leading=14,
                wordWrap='CJK',
                textColor=colors.black,
                spaceBefore=0,
                spaceAfter=0
            )
            box_elements.append(Paragraph(summary_text, summary_style))
        
        # Create table with individual elements (no KeepTogether wrapper)
        table_data = []
        for element in box_elements:
            table_data.append([element])
        
        # Create table with proper styling
        table = Table(table_data, colWidths=[6*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.lightyellow),
            ('BOX', (0,0), (-1,-1), 1, colors.orange),
            ('LEFTPADDING', (0,0), (-1,-1), 12),
            ('RIGHTPADDING', (0,0), (-1,-1), 12),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 15))
        
    except Exception as e:
        print(f"Warning: Could not create summary box: {e}")
        # Fallback: Add content as regular paragraphs with simple styling
        story.append(Spacer(1, 10))
        
        if title_text:
            story.append(Paragraph(f"<b>{title_text}</b>", styles['Heading3']))
            story.append(Spacer(1, 8))
        
        if summary_text:
            story.append(Paragraph(summary_text, styles['Normal']))
        
        story.append(Spacer(1, 15))
    
    return story

def add_footnotes_to_story(story, footnotes_config):
    """
    Issues Found:
    1. No validation of footnotes_config
    2. No handling of duplicate numbers
    3. No validation of footnote structure
    """
    if not footnotes_config or not isinstance(footnotes_config, list):
        return story
        
    styles = getSampleStyleSheet()
    
    # Filter out invalid footnotes
    valid_footnotes = []
    for note in footnotes_config:
        if isinstance(note, dict) and note.get('text'):
            valid_footnotes.append(note)
    
    if valid_footnotes:
        story.append(Spacer(1, 20))
        
        # Create footnote header style
        footnote_header_style = ParagraphStyle(
            'FootnoteHeader',
            parent=styles['Normal'],
            fontSize=12,
            fontName='Helvetica-Bold'
        )
        story.append(Paragraph('Footnotes:', footnote_header_style))
        
        # Create footnote text style
        footnote_style = ParagraphStyle(
            'FootnoteText',
            parent=styles['Normal'],
            fontSize=10,
            leading=12,
            leftIndent=20
        )
        
        for i, note in enumerate(valid_footnotes, 1):
            number = note.get('number', i)
            text = str(note.get('text', '')).strip()
            if text:
                story.append(Paragraph(f"<super>{number}</super> {text}", footnote_style))
                story.append(Spacer(1, 3))
    
    return story


def add_endnotes_section(story, endnotes_config):
    """
    Issues Found:
    1. Same issues as footnotes
    2. No page break validation
    """
    if not endnotes_config or not isinstance(endnotes_config, list):
        return story
        
    styles = getSampleStyleSheet()
    
    # Filter out invalid endnotes
    valid_endnotes = []
    for note in endnotes_config:
        if isinstance(note, dict) and note.get('text'):
            valid_endnotes.append(note)
    
    if valid_endnotes:
        story.append(PageBreak())
        story.append(Paragraph('Endnotes', styles['Heading2']))
        story.append(Spacer(1, 12))
        
        # Create endnote text style
        endnote_style = ParagraphStyle(
            'EndnoteText',
            parent=styles['Normal'],
            fontSize=11,
            leading=13,
            leftIndent=15
        )
        
        for i, note in enumerate(valid_endnotes, 1):
            number = note.get('number', i)
            text = str(note.get('text', '')).strip()
            if text:
                story.append(Paragraph(f"<super>{number}</super> {text}", endnote_style))
                story.append(Spacer(1, 6))
    
    return story


def add_form_fields(story, form_config):
    """
    Issues Found:
    1. No validation of form_config structure
    2. Limited field types
    3. No proper form field sizing
    """
    if not form_config or not isinstance(form_config, list):
        return story
        
    styles = getSampleStyleSheet()
    
    # Filter valid form fields
    valid_fields = []
    for field in form_config:
        if isinstance(field, dict) and field.get('label'):
            valid_fields.append(field)
    
    if valid_fields:
        story.append(Spacer(1, 20))
        story.append(Paragraph('Form Fields', styles['Heading3']))
        story.append(Spacer(1, 10))
        
        # Create form field style
        field_style = ParagraphStyle(
            'FormField',
            parent=styles['Normal'],
            fontSize=11,
            leading=16
        )
        
        for field in valid_fields:
            label = str(field.get('label', 'Field')).strip()
            field_type = str(field.get('type', 'text')).lower()
            
            # Create appropriate field representation
            if field_type == 'checkbox':
                field_repr = "☐"
            elif field_type == 'date':
                field_repr = "___/___/______"
            elif field_type == 'signature':
                field_repr = "_" * 30
            else:  # text or other
                field_repr = "_" * 20
            
            story.append(Paragraph(f"{label}: {field_repr}", field_style))
            story.append(Spacer(1, 8))
    
    return story


def add_appendix_section(story, appendix_config):
    """
    Issues Found:
    1. No validation of appendix structure
    2. No handling of empty sections
    3. Fixed spacing regardless of content
    """
    if not appendix_config or not isinstance(appendix_config, list):
        return story
        
    styles = getSampleStyleSheet()
    
    # Filter valid appendix sections
    valid_sections = []
    for section in appendix_config:
        if isinstance(section, dict) and (section.get('title') or section.get('content')):
            valid_sections.append(section)
    
    if valid_sections:
        story.append(PageBreak())
        story.append(Paragraph('Appendix', styles['Heading2']))
        story.append(Spacer(1, 15))
        
        # Create appendix content style
        appendix_style = ParagraphStyle(
            'AppendixContent',
            parent=styles['Normal'],
            fontSize=11,
            leading=14,
            wordWrap='CJK'
        )
        
        for i, section in enumerate(valid_sections):
            # Add section title if provided
            if section.get('title'):
                title = str(section['title']).strip()
                if title:
                    # Use numbered subsections
                    section_style = ParagraphStyle(
                        'AppendixSection',
                        parent=styles['Heading3'],
                        fontSize=14,
                        spaceAfter=8
                    )
                    story.append(Paragraph(f"A.{i+1} {title}", section_style))
            
            # Add section content if provided
            if section.get('content'):
                content = str(section['content']).strip()
                if content:
                    story.append(Paragraph(content, appendix_style))
                    story.append(Spacer(1, 12))
            
            # Add extra spacing between major sections
            if i < len(valid_sections) - 1:
                story.append(Spacer(1, 8))
    
    return story


def add_multi_column_content(story, column_config):
    """
    Issues Found (from previous analysis):
    1. No column width control
    2. No validation
    3. No error handling
    4. No limits on column count
    """
    if not column_config or not isinstance(column_config, list):
        return story
        
    styles = getSampleStyleSheet()
    
    for section in column_config:
        if not isinstance(section, dict):
            continue
            
        columns = section.get('columns', [])
        spacing = max(6, int(section.get('spacing', 12)))  # Minimum spacing
        
        # Skip empty sections
        if not columns or not isinstance(columns, list):
            continue
            
        # Limit number of columns to prevent layout issues
        max_columns = min(len(columns), 4)
        columns = columns[:max_columns]
        
        try:
            data = []
            row = []
            
            # Calculate column widths dynamically
            available_width = 500  # Approximate usable page width in points
            col_width = available_width / len(columns)
            col_widths = [col_width] * len(columns)
            
            for col in columns:
                if not isinstance(col, dict):
                    continue
                    
                content = str(col.get('content', '')).strip()
                if not content:
                    content = "&nbsp;"  # Non-breaking space
                    
                style = ParagraphStyle(
                    'ColumnContent',
                    parent=styles['Normal'],
                    fontSize=11,
                    fontName='Helvetica',
                    spaceBefore=5,
                    spaceAfter=5,
                    textColor=colors.black,
                    alignment=TA_LEFT,
                    leading=14,
                    wordWrap='CJK'
                )
                row.append(Paragraph(content, style))
                
            if row:  # Only create table if we have content
                data.append(row)
                
                table = Table(data, colWidths=col_widths)
                table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                    ('LINEAFTER', (0, 0), (-2, -1), 0.5, colors.lightgrey),
                ]))
                
                story.append(table)
                story.append(Spacer(1, spacing))
            
        except Exception as e:
            print(f"Warning: Multi-column layout failed, using fallback: {e}")
            # Fallback: Add content as regular paragraphs
            for col in columns:
                if isinstance(col, dict):
                    content = str(col.get('content', '')).strip()
                    if content:
                        story.append(Paragraph(content, styles['Normal']))
                        story.append(Spacer(1, 6))
            story.append(Spacer(1, spacing))
    
    return story

def add_text_boxes_to_story(story, textbox_config):
    """Add styled text boxes with borders and background colors"""
    if not textbox_config or not isinstance(textbox_config, list):
        return story
    
    styles = getSampleStyleSheet()
    
    for box in textbox_config:
        if not isinstance(box, dict) or not box.get('text'):
            continue
        
        text = str(box.get('text', '')).strip()
        bg_color = colors.toColor(box.get('background_color', '#F0F0F0'))
        border_color = colors.toColor(box.get('border_color', '#000000'))
        
        box_content = [Paragraph(text, styles['Normal'])]
        table = Table([box_content])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg_color),
            ('BOX', (0,0), (-1,-1), 1, border_color),
            ('LEFTPADDING', (0,0), (-1,-1), 12),
            ('RIGHTPADDING', (0,0), (-1,-1), 12),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ]))
        
        story.append(Spacer(1, 10))
        story.append(table)
        story.append(Spacer(1, 10))
    
    return story


def add_callout_boxes(story, callout_config):
    """Add callout boxes for highlighting important information"""
    if not callout_config or not isinstance(callout_config, list):
        return story
    
    styles = getSampleStyleSheet()
    
    for callout in callout_config:
        if not isinstance(callout, dict) or not callout.get('text'):
            continue
        
        title = callout.get('title', '')
        text = str(callout.get('text', '')).strip()
        callout_type = callout.get('type', 'info')  # info, warning, success, error
        
        # Color scheme based on type
        color_schemes = {
            'info': {'bg': '#E3F2FD', 'border': '#2196F3'},
            'warning': {'bg': '#FFF3E0', 'border': '#FF9800'},
            'success': {'bg': '#E8F5E8', 'border': '#4CAF50'},
            'error': {'bg': '#FFEBEE', 'border': '#F44336'}
        }
        
        scheme = color_schemes.get(callout_type, color_schemes['info'])
        
        box_content = []
        if title:
            box_content.append(Paragraph(f"<b>{title}</b>", styles['Normal']))
            box_content.append(Spacer(1, 6))
        box_content.append(Paragraph(text, styles['Normal']))
        
        table = Table([box_content])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.toColor(scheme['bg'])),
            ('BOX', (0,0), (-1,-1), 2, colors.toColor(scheme['border'])),
            ('LEFTPADDING', (0,0), (-1,-1), 15),
            ('RIGHTPADDING', (0,0), (-1,-1), 15),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ]))
        
        story.append(Spacer(1, 15))
        story.append(table)
        story.append(Spacer(1, 15))
    
    return story


def add_qr_codes_to_story(story, qr_config):
    """Add QR codes for links, contact info, etc."""
    if not qr_config or not isinstance(qr_config, list):
        return story
    
    styles = getSampleStyleSheet()
    
    for qr_item in qr_config:
        if not isinstance(qr_item, dict) or not qr_item.get('data'):
            continue
        
        data = str(qr_item.get('data', ''))
        size = qr_item.get('size', 100)
        caption = qr_item.get('caption', '')
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data)
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to BytesIO
        img_buffer = BytesIO()
        qr_img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        # Add to story
        story.append(Spacer(1, 15))
        qr_image = Image(img_buffer, width=size, height=size)
        story.append(qr_image)
        
        if caption:
            story.append(Spacer(1, 8))
            story.append(Paragraph(f'<i><font size="9">{caption}</font></i>', styles['Normal']))
        
        story.append(Spacer(1, 15))
    
    return story