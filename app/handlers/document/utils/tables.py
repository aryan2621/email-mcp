import logging
from typing import List, Dict
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

logger = logging.getLogger('pdf-mcp')

def add_tables_to_story(story: List, tables_config: List[Dict]) -> List:
    try:
        for table_config in tables_config:
            data = table_config.get('data', [])
            if not data:
                continue
            
            # Add table title
            title = table_config.get('title', '')
            if title:
                story.append(Spacer(1, 20))
                story.append(Paragraph(f'<b><font size="12">{title}</font></b>', getSampleStyleSheet()['Normal']))
                story.append(Spacer(1, 10))
            
            # Create table with better column widths
            column_widths = table_config.get('column_widths', [120, 100, 100, 100])
            table = Table(data, colWidths=column_widths, repeatRows=1)
            
            # Improved table styling
            style_config = table_config.get('style', {})
            table_styles = [
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]
            
            # Grid and borders
            if style_config.get('grid', True):
                border_color = colors.toColor(style_config.get('border_color', '#000000'))
                table_styles.append(('GRID', (0, 0), (-1, -1), 1, border_color))
            
            # Header styling
            if len(data) > 0 and style_config.get('header_background'):
                header_color = colors.toColor(style_config['header_background'])
                table_styles.extend([
                    ('BACKGROUND', (0, 0), (-1, 0), header_color),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black)
                ])
            
            # Alternate row colors
            if style_config.get('alternate_rows', False) and len(data) > 1:
                for i in range(1, len(data), 2):
                    table_styles.append(('BACKGROUND', (0, i), (-1, i), colors.lightgrey))
            
            table.setStyle(TableStyle(table_styles))
            story.append(table)
            story.append(Spacer(1, 25))
        
        return story
        
    except Exception as e:
        logger.error(f"Error adding tables: {e}")
        return story 