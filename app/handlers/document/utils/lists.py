import logging
from typing import List, Dict
from reportlab.platypus import Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

logger = logging.getLogger('pdf-mcp')

def add_lists_to_story(story: List, lists_config: List[Dict]) -> List:
    try:
        for list_config in lists_config:
            list_type = list_config.get('type', 'bullet')
            items = list_config.get('items', [])
            title = list_config.get('title', '')
            
            if not items:
                continue
            
            if title:
                story.append(Spacer(1, 20))
                story.append(Paragraph(f'<b><font size="12">{title}</font></b>', getSampleStyleSheet()['Normal']))
                story.append(Spacer(1, 10))
            
            for i, item in enumerate(items):
                if list_type == 'bullet':
                    list_text = f'• {item}'
                else:  # numbered
                    list_text = f'{i+1}. {item}'
                
                story.append(Paragraph(list_text, getSampleStyleSheet()['Normal']))
                story.append(Spacer(1, 6))
            
            story.append(Spacer(1, 15))
        
        return story
        
    except Exception as e:
        logger.error(f"Error adding lists: {e}")
        return story 