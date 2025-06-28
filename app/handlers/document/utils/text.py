import logging
from typing import List, Dict
from reportlab.platypus import Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

logger = logging.getLogger('pdf-mcp')

def add_formatted_text_to_story(story: List, formatted_content: List[Dict]) -> List:
    try:
        if not formatted_content:
            return story

        custom_style = ParagraphStyle(
            name='CustomNormal',
            parent=getSampleStyleSheet()['Normal'],
            spaceAfter=2,
            leading=10
        )

        story.append(Spacer(1, 10))

        for item in formatted_content:
            text = item.get('text', '').strip()
            if not text:
                continue

            formatted_text = text
            if item.get('bold', False):
                formatted_text = f'<b>{formatted_text}</b>'
            if item.get('italic', False):
                formatted_text = f'<i>{formatted_text}</i>'
            if item.get('underline', False):
                formatted_text = f'<u>{formatted_text}</u>'
            if item.get('color', ''):
                formatted_text = f'<font color="{item["color"]}">{formatted_text}</font>'
            if item.get('link', ''):
                formatted_text = f'<a href="{item["link"]}">{formatted_text}</a>'

            story.append(Paragraph(formatted_text, custom_style))
            story.append(Spacer(1, 6))  # Reduced spacer between paragraphs

        # Only add final spacer if more content is expected
        if formatted_content:
            story.append(Spacer(1, 8))  # Reduced final spacer

        return story

    except Exception as e:
        logger.error(f"Error adding formatted text: {e}")
        return story