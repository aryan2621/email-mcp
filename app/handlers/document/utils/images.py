import os
import logging
from typing import List, Dict
import requests
from reportlab.platypus import Spacer, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet

logger = logging.getLogger('pdf-mcp')

def add_images_to_story(story: List, images_config: List[Dict]) -> List:
    try:
        for img_config in images_config:
            url = img_config.get('url', '')
            path = img_config.get('path', '')
            width = img_config.get('width', 150)
            height = img_config.get('height', 150)
            caption = img_config.get('caption', '')
            
            image_path = None
            
            if url:
                try:
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()
                    
                    base_dir = os.path.join(os.getcwd(), 'generated_docs')
                    images_dir = os.path.join(base_dir, 'images')
                    os.makedirs(images_dir, exist_ok=True)
                    
                    import time
                    import uuid
                    ext = '.jpg'
                    if url.lower().endswith('.png'):
                        ext = '.png'
                    
                    image_filename = f"image_{int(time.time())}_{uuid.uuid4().hex[:8]}{ext}"
                    image_path = os.path.join(images_dir, image_filename)
                    
                    with open(image_path, 'wb') as f:
                        f.write(response.content)
                        
                except Exception as e:
                    logger.warning(f"Could not download image: {e}")
                    continue
            
            elif path and os.path.exists(path):
                image_path = path
            
            if image_path:
                try:
                    story.append(Spacer(1, 15))
                    
                    # Create image with specified dimensions
                    img = Image(image_path, width=width, height=height)
                    
                    # Handle alignment
                    alignment = img_config.get('alignment', 'left').lower()
                    
                    if alignment == 'center':
                        # Center the image using a table
                        from reportlab.platypus import Table, TableStyle
                        from reportlab.lib.enums import TA_CENTER
                        table_data = [[img]]
                        img_table = Table(table_data)
                        img_table.setStyle(TableStyle([
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                            ('TOPPADDING', (0, 0), (-1, -1), 0),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                        ]))
                        story.append(img_table)
                    elif alignment == 'right':
                        # Right align using a table
                        from reportlab.platypus import Table, TableStyle
                        table_data = [[img]]
                        img_table = Table(table_data)
                        img_table.setStyle(TableStyle([
                            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                            ('TOPPADDING', (0, 0), (-1, -1), 0),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                        ]))
                        story.append(img_table)
                    else:  # left alignment (default)
                        story.append(img)
                    
                    if caption:
                        story.append(Spacer(1, 8))
                        # Align caption to match image alignment
                        if alignment == 'center':
                            caption_style = f'<para align="center"><i><font size="9" color="gray">{caption}</font></i></para>'
                        elif alignment == 'right':
                            caption_style = f'<para align="right"><i><font size="9" color="gray">{caption}</font></i></para>'
                        else:
                            caption_style = f'<i><font size="9" color="gray">{caption}</font></i>'
                        story.append(Paragraph(caption_style, getSampleStyleSheet()['Normal']))
                    
                    story.append(Spacer(1, 15))
                    
                except Exception as e:
                    logger.error(f"Error adding image: {e}")
        
        return story
        
    except Exception as e:
        logger.error(f"Error adding images: {e}")
        return story 