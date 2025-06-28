import logging
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib import colors

logger = logging.getLogger('pdf-mcp')

class ComprehensiveDocTemplate(SimpleDocTemplate):
    """Document template with header, footer, and subtle watermark support"""
    
    def __init__(self, filename, header_config=None, footer_config=None, 
                 watermark_config=None, border_config=None, background_config=None, **kwargs):
        super().__init__(filename, **kwargs)
        self.header_config = header_config or {}
        self.footer_config = footer_config or {}
        self.watermark_config = watermark_config or {}
        self.border_config = border_config or {}
        self.background_config = background_config or {}
        self.watermark_config = watermark_config or {}
    
    def handle_pageBegin(self):
        super().handle_pageBegin()
    
        if self.background_config:
            self._add_background()
        
        if self.border_config:
            self._add_border()
        
        if self.watermark_config:
            self._add_watermark()
        
        if self.header_config:
            self._add_header()
        
        if self.footer_config:
            self._add_footer()
    
    def _add_watermark(self):
        """Add watermark (text or image) that doesn't interfere"""
        try:
            canvas_obj = self.canv
            canvas_obj.saveState()
            
            # Get page dimensions
            page_width, page_height = canvas_obj._pagesize
            center_x = page_width / 2
            center_y = page_height / 2
            
            watermark_type = self.watermark_config.get('type', 'text')
            opacity = self.watermark_config.get('opacity', 0.2)
            canvas_obj.setFillAlpha(opacity)
            
            if watermark_type == 'text':
                text = self.watermark_config.get('text', 'WATERMARK')
                font_size = self.watermark_config.get('font_size', 40)
                rotation = self.watermark_config.get('rotation', 45)
                color = self.watermark_config.get('color', 'gray')
                
                canvas_obj.translate(center_x, center_y)
                canvas_obj.rotate(rotation)
                canvas_obj.setFillColor(colors.toColor(color))
                canvas_obj.setFont("Helvetica-Bold", font_size)
                canvas_obj.drawCentredString(0, 0, text)
                
            elif watermark_type == 'image':
                url = self.watermark_config.get('url', '')
                width = self.watermark_config.get('width', 150)
                height = self.watermark_config.get('height', 150)
                rotation = self.watermark_config.get('rotation', 0)
                
                if url:
                    import requests
                    from reportlab.lib.utils import ImageReader
                    from io import BytesIO
                    
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()
                    img_data = BytesIO(response.content)
                    img = ImageReader(img_data)
                    
                    canvas_obj.translate(center_x, center_y)
                    canvas_obj.rotate(rotation)
                    canvas_obj.drawImage(img, -width/2, -height/2, width=width, height=height, mask='auto')
            
            canvas_obj.restoreState()
            
        except Exception as e:
            logger.error(f"Error adding watermark: {e}")
    
    def _add_header(self):
        """Add header to page"""
        try:
            canvas_obj = self.canv
            page_width, page_height = canvas_obj._pagesize
            
            header_text = self.header_config.get('text', '')
            if not header_text:
                return
            
            canvas_obj.saveState()
            canvas_obj.setFont("Helvetica", 9)  # Smaller font
            canvas_obj.setFillColor(colors.darkgray)  # Darker for visibility
            
            # Position header higher up
            y_position = page_height - 40
            alignment = self.header_config.get('alignment', 'center')
            
            if alignment == 'center':
                canvas_obj.drawCentredString(page_width/2, y_position, header_text)
            elif alignment == 'right':
                canvas_obj.drawRightString(page_width - 72, y_position, header_text)
            else:  # left
                canvas_obj.drawString(72, y_position, header_text)
            
            canvas_obj.restoreState()
            
        except Exception as e:
            logger.error(f"Error adding header: {e}")
    
    def _add_footer(self):
        """Add footer to page"""
        try:
            canvas_obj = self.canv
            page_width, page_height = canvas_obj._pagesize
            
            footer_text = self.footer_config.get('text', '')
            show_page_number = self.footer_config.get('show_page_number', False)
            
            if not footer_text and not show_page_number:
                return
            
            canvas_obj.saveState()
            canvas_obj.setFont("Helvetica", 9)  # Smaller font
            canvas_obj.setFillColor(colors.darkgray)  # Darker for visibility
            
            y_position = 40  # Higher up from bottom
            
            # Add footer text
            if footer_text:
                alignment = self.footer_config.get('alignment', 'center')
                
                if alignment == 'center':
                    canvas_obj.drawCentredString(page_width/2, y_position, footer_text)
                elif alignment == 'right':
                    canvas_obj.drawRightString(page_width - 72, y_position, footer_text)
                else:  # left
                    canvas_obj.drawString(72, y_position, footer_text)
            
            # Add page number
            if show_page_number:
                page_num = f"Page {canvas_obj.getPageNumber()}"
                canvas_obj.drawRightString(page_width - 72, y_position - 15, page_num)
            
            canvas_obj.restoreState()
            
        except Exception as e:
            logger.error(f"Error adding footer: {e}") 
    
    def _add_background(self):
        """Add background color or gradient to page"""
        try:
            canvas_obj = self.canv
            canvas_obj.saveState()
            
            page_width, page_height = canvas_obj._pagesize
            
            if self.background_config.get('gradient'):
                # Gradient background
                gradient = self.background_config['gradient']
                start_color = colors.toColor(gradient.get('start_color', '#FFFFFF'))
                end_color = colors.toColor(gradient.get('end_color', '#F0F0F0'))
                direction = gradient.get('direction', 'vertical')
                
                # Simple gradient simulation with multiple rectangles
                steps = 50
                for i in range(steps):
                    ratio = i / steps
                    # Blend colors
                    r = start_color.red + (end_color.red - start_color.red) * ratio
                    g = start_color.green + (end_color.green - start_color.green) * ratio  
                    b = start_color.blue + (end_color.blue - start_color.blue) * ratio
                    
                    canvas_obj.setFillColor(colors.Color(r, g, b))
                    
                    if direction == 'vertical':
                        rect_height = page_height / steps
                        canvas_obj.rect(0, i * rect_height, page_width, rect_height, stroke=0, fill=1)
                    else:  # horizontal
                        rect_width = page_width / steps
                        canvas_obj.rect(i * rect_width, 0, rect_width, page_height, stroke=0, fill=1)
            
            elif self.background_config.get('color'):
                # Solid background color
                bg_color = colors.toColor(self.background_config['color'])
                canvas_obj.setFillColor(bg_color)
                canvas_obj.rect(0, 0, page_width, page_height, stroke=0, fill=1)
            
            canvas_obj.restoreState()
            
        except Exception as e:
            logger.error(f"Error adding background: {e}")

    def _add_border(self):
        """Add decorative border around page"""
        try:
            canvas_obj = self.canv
            canvas_obj.saveState()
            
            page_width, page_height = canvas_obj._pagesize
            
            # Get border configuration
            margin_inches = self.border_config.get('margin_inches', 0.2)
            margin = margin_inches * 72  # Convert to points
            color = colors.toColor(self.border_config.get('color', '#333333'))
            width = self.border_config.get('width', 1.5)
            style = self.border_config.get('style', 'single')
            
            # Calculate border coordinates
            x1, y1 = margin, margin
            x2, y2 = page_width - margin, page_height - margin
            
            canvas_obj.setStrokeColor(color)
            canvas_obj.setLineWidth(width)
            
            if style == 'single':
                # Single border
                canvas_obj.rect(x1, y1, x2 - x1, y2 - y1, stroke=1, fill=0)
                
            elif style == 'double':
                # Double border
                canvas_obj.rect(x1, y1, x2 - x1, y2 - y1, stroke=1, fill=0)
                inner_margin = 6
                canvas_obj.rect(x1 + inner_margin, y1 + inner_margin, 
                              x2 - x1 - 2*inner_margin, y2 - y1 - 2*inner_margin, stroke=1, fill=0)
                
            elif style == 'decorative':
                # Decorative border with corners
                canvas_obj.rect(x1, y1, x2 - x1, y2 - y1, stroke=1, fill=0)
                
                # Corner decorations
                corner_size = 15
                canvas_obj.setLineWidth(width + 0.5)
                
                # Corner lines
                corners = [
                    (x1, y2, x1 + corner_size, y2, x1, y2 - corner_size),  # Top-left
                    (x2, y2, x2 - corner_size, y2, x2, y2 - corner_size),  # Top-right  
                    (x1, y1, x1 + corner_size, y1, x1, y1 + corner_size),  # Bottom-left
                    (x2, y1, x2 - corner_size, y1, x2, y1 + corner_size),  # Bottom-right
                ]
                
                for corner in corners:
                    canvas_obj.line(corner[0], corner[1], corner[2], corner[3])
                    canvas_obj.line(corner[0], corner[1], corner[4], corner[5])
            
            canvas_obj.restoreState()
            
        except Exception as e:
            logger.error(f"Error adding border: {e}")