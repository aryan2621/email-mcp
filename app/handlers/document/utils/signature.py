import logging
from typing import List, Dict
from reportlab.platypus import Spacer, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.units import inch

logger = logging.getLogger('pdf-mcp')

def add_signature_to_story(story: List, signature_config: Dict) -> List:
    """
    Issues Found in Original:
    1. No input validation for story or signature_config
    2. Limited positioning - only adds at end of document
    3. Fixed spacing (40 points) regardless of content
    4. No handling of position parameter mentioned in docstring
    5. Basic styling with no customization options
    6. No validation of font_size parameter
    7. Missing error handling for malformed config
    """
    if not signature_config or not isinstance(signature_config, dict):
        return story
    
    if not isinstance(story, list):
        logger.error("Story must be a list")
        return story
    
    try:
        # Validate and extract configuration
        signature_text = str(signature_config.get('text', 'Digitally Signed')).strip()
        date = str(signature_config.get('date', '')).strip()
        position = signature_config.get('position', 'bottom-right').lower()
        font_size = signature_config.get('font_size', 10)
        
        # Validate font size
        try:
            font_size = max(6, min(20, int(font_size)))  # Reasonable range
        except (ValueError, TypeError):
            font_size = 10
            logger.warning("Invalid font_size, using default 10")
        
        # Validate position
        valid_positions = ['bottom-left', 'bottom-right', 'top-left', 'top-right', 'center']
        if position not in valid_positions:
            position = 'bottom-right'
            logger.warning(f"Invalid position, using 'bottom-right'. Valid options: {valid_positions}")
        
        if not signature_text:
            logger.warning("Empty signature text provided")
            return story
        
        # Build full signature text
        full_signature = signature_text
        if date:
            try:
                # Try to validate date format (basic check)
                from datetime import datetime
                if len(date) == 10 and date.count('-') == 2:
                    datetime.strptime(date, '%Y-%m-%d')
                full_signature += f" on {date}"
            except ValueError:
                full_signature += f" on {date}"  # Use as-is if not standard format
        
        # Determine alignment based on position
        if 'left' in position:
            alignment = TA_LEFT
        elif 'right' in position:
            alignment = TA_RIGHT
        else:
            alignment = TA_CENTER
        
        # Create signature style
        styles = getSampleStyleSheet()
        signature_style = ParagraphStyle(
            'SignatureStyle',
            parent=styles['Normal'],
            fontSize=font_size,
            alignment=alignment,
            textColor=colors.black,
            fontName='Helvetica-Oblique',  # Italic font
            spaceBefore=6,
            spaceAfter=6
        )
        
        # Add appropriate spacing based on position
        if 'top' in position:
            # For top signatures, add minimal spacing
            story.append(Spacer(1, 12))
        else:
            # For bottom signatures, add more spacing
            story.append(Spacer(1, 30))
        
        # Create signature paragraph
        signature_paragraph = Paragraph(full_signature, signature_style)
        
        # For center or special positioning, use a table for better control
        if position == 'center' or 'right' in position:
            # Create a table for better positioning control
            table_data = [[signature_paragraph]]
            signature_table = Table(table_data, colWidths=[6*inch])
            signature_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]))
            story.append(signature_table)
        else:
            story.append(signature_paragraph)
        
        # Add trailing space
        story.append(Spacer(1, 12))
        
        return story
        
    except Exception as e:
        logger.error(f"Error adding signature: {e}")
        return story
