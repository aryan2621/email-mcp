#!/usr/bin/env python3
"""
Ultra-Enhanced PDF MCP Server - Part 1: Core Architecture
Professional PDF generation with advanced styling, layouts, and visual effects
"""

import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

# Core ReportLab imports
from reportlab.platypus import (
    Paragraph, Spacer, Table, TableStyle, 
    Image, KeepTogether, Flowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.colors import Color, HexColor
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.barcharts import VerticalBarChart, HorizontalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.doughnut import Doughnut

logger = logging.getLogger('gmail-mcp')

# Enhanced Enums for better type safety and options
class PageOrientation(Enum):
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"

class DocumentTemplate(Enum):
    MINIMAL = "minimal"
    CORPORATE = "corporate"
    CREATIVE = "creative"
    ACADEMIC = "academic"
    MAGAZINE = "magazine"
    NEWSPAPER = "newspaper"
    BROCHURE = "brochure"
    INVOICE = "invoice"
    CERTIFICATE = "certificate"
    PRESENTATION = "presentation"

class ColorScheme(Enum):
    CLASSIC = "classic"
    MODERN = "modern"
    VIBRANT = "vibrant"
    PASTEL = "pastel"
    MONOCHROME = "monochrome"
    CORPORATE_BLUE = "corporate_blue"
    NATURE = "nature"
    SUNSET = "sunset"
    OCEAN = "ocean"
    FOREST = "forest"

class FontFamily(Enum):
    HELVETICA = "Helvetica"
    TIMES = "Times-Roman"
    COURIER = "Courier"
    SYMBOL = "Symbol"
    ZAPF_DINGBATS = "ZapfDingbats"

class ChartType(Enum):
    BAR_VERTICAL = "bar_vertical"
    BAR_HORIZONTAL = "bar_horizontal"
    PIE = "pie"
    DOUGHNUT = "doughnut"
    LINE = "line"
    AREA = "area"
    SPIDER = "spider"
    SCATTER = "scatter"

@dataclass
class ColorPalette:
    """Advanced color palette system"""
    primary: Color = field(default_factory=lambda: colors.darkblue)
    secondary: Color = field(default_factory=lambda: colors.lightblue)
    accent: Color = field(default_factory=lambda: colors.orange)
    background: Color = field(default_factory=lambda: colors.white)
    text: Color = field(default_factory=lambda: colors.black)
    muted: Color = field(default_factory=lambda: colors.grey)
    success: Color = field(default_factory=lambda: colors.green)
    warning: Color = field(default_factory=lambda: colors.orange)
    error: Color = field(default_factory=lambda: colors.red)
    info: Color = field(default_factory=lambda: colors.blue)
    
    @classmethod
    def from_scheme(cls, scheme: ColorScheme) -> 'ColorPalette':
        """Create color palette from predefined scheme"""
        palettes = {
            ColorScheme.CLASSIC: cls(
                primary=colors.darkblue,
                secondary=colors.lightblue,
                accent=colors.gold,
                background=colors.white,
                text=colors.black
            ),
            ColorScheme.MODERN: cls(
                primary=HexColor('#2E86AB'),
                secondary=HexColor('#A23B72'),
                accent=HexColor('#F18F01'),
                background=HexColor('#F5F5F5'),
                text=HexColor('#333333')
            ),
            ColorScheme.VIBRANT: cls(
                primary=HexColor('#FF6B6B'),
                secondary=HexColor('#4ECDC4'),
                accent=HexColor('#45B7D1'),
                background=colors.white,
                text=HexColor('#2C3E50')
            ),
            ColorScheme.PASTEL: cls(
                primary=HexColor('#FFB3BA'),
                secondary=HexColor('#FFDFBA'),
                accent=HexColor('#FFFFBA'),
                background=HexColor('#FEFEFE'),
                text=HexColor('#5D5D5D')
            ),
            ColorScheme.CORPORATE_BLUE: cls(
                primary=HexColor('#003366'),
                secondary=HexColor('#0066CC'),
                accent=HexColor('#FF9900'),
                background=colors.white,
                text=HexColor('#333333')
            ),
            ColorScheme.NATURE: cls(
                primary=HexColor('#2E7D32'),
                secondary=HexColor('#66BB6A'),
                accent=HexColor('#FFC107'),
                background=HexColor('#F1F8E9'),
                text=HexColor('#1B5E20')
            )
        }
        return palettes.get(scheme, cls())

@dataclass
class Typography:
    """Advanced typography configuration"""
    primary_font: str = "Helvetica"
    secondary_font: str = "Helvetica-Oblique"
    monospace_font: str = "Courier"
    base_size: int = 12
    scale_ratio: float = 1.414  # Perfect fourth ratio
    line_height: float = 1.5
    paragraph_spacing: float = 12
    
    def get_size(self, level: int) -> int:
        """Get font size for heading level (0 = base, 1 = h1, etc.)"""
        if level <= 0:
            return self.base_size
        return int(self.base_size * (self.scale_ratio ** level))

@dataclass
class LayoutConfig:
    """Advanced layout configuration"""
    page_size: tuple = letter
    orientation: PageOrientation = PageOrientation.PORTRAIT
    margins: Dict[str, float] = field(default_factory=lambda: {
        "top": 1*inch, "bottom": 1*inch, "left": 1*inch, "right": 1*inch
    })
    columns: int = 1
    column_gap: float = 0.5*inch
    grid_system: bool = False
    golden_ratio: bool = False
    
    def get_page_dimensions(self) -> Tuple[float, float]:
        """Get page dimensions considering orientation"""
        width, height = self.page_size
        if self.orientation == PageOrientation.LANDSCAPE:
            return height, width
        return width, height
    
    def get_content_area(self) -> Tuple[float, float]:
        """Get available content area"""
        width, height = self.get_page_dimensions()
        content_width = width - self.margins["left"] - self.margins["right"]
        content_height = height - self.margins["top"] - self.margins["bottom"]
        return content_width, content_height

@dataclass
class WatermarkConfig:
    """Watermark configuration"""
    text: str = ""
    opacity: float = 0.1
    angle: float = 45
    font_size: int = 60
    color: Color = field(default_factory=lambda: colors.grey)
    position: str = "center"  # center, top-left, top-right, bottom-left, bottom-right

@dataclass
class HeaderFooterConfig:
    """Header and footer configuration"""
    header_text: str = ""
    footer_text: str = ""
    show_page_numbers: bool = True
    page_number_format: str = "Page {page} of {total}"
    include_date: bool = False
    date_format: str = "%Y-%m-%d"
    separator_line: bool = True
    height: float = 0.5*inch

@dataclass
class PDFConfig:
    """Comprehensive PDF configuration"""
    # Core settings
    template: DocumentTemplate = DocumentTemplate.MINIMAL
    color_scheme: ColorScheme = ColorScheme.CLASSIC
    
    # Layout and typography
    layout: LayoutConfig = field(default_factory=LayoutConfig)
    typography: Typography = field(default_factory=Typography)
    color_palette: ColorPalette = field(default_factory=ColorPalette)
    
    # Document elements
    watermark: WatermarkConfig = field(default_factory=WatermarkConfig)
    header_footer: HeaderFooterConfig = field(default_factory=HeaderFooterConfig)
    
    # Advanced features
    table_of_contents: bool = False
    page_breaks_before_sections: bool = False
    section_numbering: bool = False
    footnotes: bool = False
    
    # Quality and optimization
    compress_images: bool = True
    image_quality: int = 85
    embed_fonts: bool = True
    
    # Security (for future implementation)
    password_protection: bool = False
    allow_printing: bool = True
    allow_copying: bool = True
    
    def __post_init__(self):
        """Post-initialization to set up dependent configs"""
        # Set color palette based on scheme
        self.color_palette = ColorPalette.from_scheme(self.color_scheme)
        
        # Adjust layout based on template
        if self.template == DocumentTemplate.MAGAZINE:
            self.layout.columns = 2
            self.layout.column_gap = 0.3*inch
        elif self.template == DocumentTemplate.NEWSPAPER:
            self.layout.columns = 3
            self.layout.column_gap = 0.2*inch
        elif self.template == DocumentTemplate.ACADEMIC:
            self.layout.margins["top"] = 1.5*inch
            self.layout.margins["bottom"] = 1.5*inch
            self.table_of_contents = True
            self.section_numbering = True

class StyleManager:
    """Advanced style management system"""
    
    def __init__(self, config: PDFConfig):
        self.config = config
        self.styles = getSampleStyleSheet()
        self._create_enhanced_styles()
    
    def _create_enhanced_styles(self):
        """Create comprehensive set of custom styles"""
        typo = self.config.typography
        colors_pal = self.config.color_palette
        
        # Title styles with different templates
        title_configs = {
            DocumentTemplate.MINIMAL: {
                'fontSize': typo.get_size(3),
                'textColor': colors_pal.primary,
                'alignment': TA_CENTER,
                'spaceAfter': 30,
                'spaceBefore': 0
            },
            DocumentTemplate.CORPORATE: {
                'fontSize': typo.get_size(3),
                'textColor': colors_pal.primary,
                'alignment': TA_LEFT,
                'spaceAfter': 20,
                'borderWidth': 3,
                'borderColor': colors_pal.accent,
                'borderPadding': 10
            },
            DocumentTemplate.CREATIVE: {
                'fontSize': typo.get_size(4),
                'textColor': colors_pal.accent,
                'alignment': TA_CENTER,
                'spaceAfter': 40,
                'backColor': colors_pal.secondary,
                'borderRadius': 10
            }
        }
        
        title_config = title_configs.get(self.config.template, title_configs[DocumentTemplate.MINIMAL])
        
        self.styles.add(ParagraphStyle(
            name='EnhancedTitle',
            parent=self.styles['Heading1'],
            fontName=f"{typo.primary_font}-Bold",
            **title_config
        ))
        
        # Subtitle styles
        self.styles.add(ParagraphStyle(
            name='EnhancedSubtitle',
            parent=self.styles['Heading2'],
            fontName=typo.secondary_font,
            fontSize=typo.get_size(2),
            textColor=colors_pal.secondary,
            alignment=TA_CENTER,
            spaceAfter=20,
            spaceBefore=10
        ))
        
        # Section headers with numbering support
        for i in range(1, 7):  # H1 through H6
            self.styles.add(ParagraphStyle(
                name=f'Heading{i}Enhanced',
                parent=self.styles['Normal'],
                fontName=f"{typo.primary_font}-Bold",
                fontSize=typo.get_size(7-i),
                textColor=colors_pal.primary,
                spaceBefore=typo.get_size(7-i) * 0.8,
                spaceAfter=typo.get_size(7-i) * 0.4,
                leftIndent=(i-1) * 20,
                bulletIndent=10
            ))
        
        # Enhanced body text styles
        self.styles.add(ParagraphStyle(
            name='BodyEnhanced',
            parent=self.styles['Normal'],
            fontName=typo.primary_font,
            fontSize=typo.base_size,
            textColor=colors_pal.text,
            leading=typo.base_size * typo.line_height,
            spaceAfter=typo.paragraph_spacing,
            alignment=TA_JUSTIFY
        ))
        
        # Special text styles
        special_styles = {
            'Quote': {
                'leftIndent': 30,
                'rightIndent': 30,
                'fontSize': typo.base_size + 2,
                'textColor': colors_pal.muted,
                'backColor': Color(colors_pal.background.red, colors_pal.background.green, colors_pal.background.blue, alpha=0.5),
                'borderWidth': 1,
                'borderColor': colors_pal.accent,
                'borderPadding': 15
            },
            'Highlight': {
                'backColor': colors_pal.warning,
                'borderWidth': 1,
                'borderColor': colors_pal.accent,
                'borderPadding': 8
            },
            'CodeBlock': {
                'fontName': typo.monospace_font,
                'fontSize': typo.base_size - 1,
                'backColor': HexColor('#F5F5F5'),
                'borderWidth': 1,
                'borderColor': colors_pal.muted,
                'borderPadding': 10,
                'leftIndent': 20,
                'rightIndent': 20
            },
            'Caption': {
                'fontSize': typo.base_size - 2,
                'textColor': colors_pal.muted,
                'alignment': TA_CENTER,
                'spaceAfter': 6
            },
            'Sidebar': {
                'backColor': colors_pal.secondary,
                'borderWidth': 3,
                'borderColor': colors_pal.primary,
                'borderPadding': 15,
                'leftIndent': 10,
                'rightIndent': 10
            }
        }
        
        for name, style_props in special_styles.items():
            self.styles.add(ParagraphStyle(
                name=f'{name}Enhanced',
                parent=self.styles['Normal'],
                fontName=typo.primary_font,
                fontSize=typo.base_size,
                textColor=colors_pal.text,
                **style_props
            ))

class DocumentProcessor(ABC):
    """Abstract base class for document processors"""
    
    def __init__(self, config: PDFConfig):
        self.config = config
        self.style_manager = StyleManager(config)
    
    @abstractmethod
    def process_content(self, content: Any) -> List[Flowable]:
        """Process content and return list of flowables"""
        pass
    
    def create_watermark(self) -> Drawing:
        """Create watermark drawing"""
        if not self.config.watermark.text:
            return None
            
        width, height = self.config.layout.get_page_dimensions()
        drawing = Drawing(width, height)
        
        watermark = String(
            width/2, height/2,
            self.config.watermark.text,
            textAnchor='middle',
            fontSize=self.config.watermark.font_size,
            fillColor=Color(
                self.config.watermark.color.red,
                self.config.watermark.color.green,
                self.config.watermark.color.blue,
                alpha=self.config.watermark.opacity
            )
        )
        
        # Rotate watermark
        watermark.transform = (
            1, 0, 0, 1,
            0, 0  # Translation
        )
        
        drawing.add(watermark)
        return drawing
    
"""
Ultra-Enhanced PDF MCP Server - Part 2: Advanced Content Processing & Custom Flowables
Smart content parsing, enhanced tables, images, and custom visual elements
"""

import re
import math
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass
import requests
from io import BytesIO

from reportlab.platypus import (
    Flowable, Paragraph, Spacer, Table, TableStyle, Image, 
    KeepTogether
)
from reportlab.lib.units import inch
from reportlab.lib.colors import Color, HexColor
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.barcharts import VerticalBarChart, HorizontalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.doughnut import Doughnut
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

# Custom Flowable Classes for Enhanced Visual Elements

class GradientBox(Flowable):
    """Custom flowable for gradient backgrounds"""
    
    def __init__(self, width, height, start_color, end_color, direction='horizontal'):
        self.width = width
        self.height = height
        self.start_color = start_color
        self.end_color = end_color
        self.direction = direction
    
    def draw(self):
        """Draw gradient box"""
        canvas = self.canv
        steps = 50
        
        if self.direction == 'horizontal':
            step_width = self.width / steps
            for i in range(steps):
                ratio = i / steps
                r = self.start_color.red + (self.end_color.red - self.start_color.red) * ratio
                g = self.start_color.green + (self.end_color.green - self.start_color.green) * ratio
                b = self.start_color.blue + (self.end_color.blue - self.start_color.blue) * ratio
                
                canvas.setFillColor(Color(r, g, b))
                canvas.rect(i * step_width, 0, step_width, self.height, fill=1, stroke=0)
        else:  # vertical
            step_height = self.height / steps
            for i in range(steps):
                ratio = i / steps
                r = self.start_color.red + (self.end_color.red - self.start_color.red) * ratio
                g = self.start_color.green + (self.end_color.green - self.start_color.green) * ratio
                b = self.start_color.blue + (self.end_color.blue - self.start_color.blue) * ratio
                
                canvas.setFillColor(Color(r, g, b))
                canvas.rect(0, i * step_height, self.width, step_height, fill=1, stroke=0)

class InfoBox(Flowable):
    """Enhanced info box with icons and styling"""
    
    def __init__(self, content, box_type='info', width=None, config=None):
        self.content = content
        self.box_type = box_type  # info, warning, error, success, tip
        self.width = width or 6*inch
        self.config = config
        self.height = self._calculate_height()
    
    def _calculate_height(self):
        """Calculate required height based on content"""
        # Simplified calculation - in real implementation would measure text
        lines = len(self.content.split('\n'))
        return max(1*inch, lines * 0.3*inch)
    
    def draw(self):
        """Draw styled info box"""
        canvas = self.canv
        
        # Define colors and icons for different box types
        box_configs = {
            'info': {'color': colors.lightblue, 'border': colors.blue, 'icon': 'ℹ'},
            'warning': {'color': colors.lightyellow, 'border': colors.orange, 'icon': '⚠'},
            'error': {'color': colors.pink, 'border': colors.red, 'icon': '✖'},
            'success': {'color': colors.lightgreen, 'border': colors.green, 'icon': '✓'},
            'tip': {'color': colors.lightgrey, 'border': colors.grey, 'icon': '💡'}
        }
        
        box_config = box_configs.get(self.box_type, box_configs['info'])
        
        # Draw background
        canvas.setFillColor(box_config['color'])
        canvas.setStrokeColor(box_config['border'])
        canvas.setLineWidth(2)
        canvas.roundRect(0, 0, self.width, self.height, 10, fill=1, stroke=1)
        
        # Draw icon
        canvas.setFillColor(box_config['border'])
        canvas.setFont('Helvetica-Bold', 16)
        canvas.drawString(15, self.height - 25, box_config['icon'])
        
        # Draw content (simplified - would use proper text wrapping in real implementation)
        canvas.setFillColor(colors.black)
        canvas.setFont('Helvetica', 10)
        y_position = self.height - 25
        for line in self.content.split('\n')[:5]:  # Limit to 5 lines for space
            canvas.drawString(45, y_position, line[:60])  # Truncate long lines
            y_position -= 15

class ProgressBar(Flowable):
    """Custom progress bar flowable"""
    
    def __init__(self, percentage, width=4*inch, height=0.3*inch, 
                 color=colors.green, bg_color=colors.lightgrey, 
                 show_text=True, text_format="{percentage}%"):
        self.percentage = max(0, min(100, percentage))
        self.width = width
        self.height = height
        self.color = color
        self.bg_color = bg_color
        self.show_text = show_text
        self.text_format = text_format
    
    def draw(self):
        """Draw progress bar"""
        canvas = self.canv
        
        # Background
        canvas.setFillColor(self.bg_color)
        canvas.setStrokeColor(colors.grey)
        canvas.roundRect(0, 0, self.width, self.height, 5, fill=1, stroke=1)
        
        # Progress fill
        fill_width = (self.width - 4) * (self.percentage / 100)
        if fill_width > 0:
            canvas.setFillColor(self.color)
            canvas.roundRect(2, 2, fill_width, self.height - 4, 3, fill=1, stroke=0)
        
        # Text
        if self.show_text:
            text = self.text_format.format(percentage=self.percentage)
            canvas.setFillColor(colors.black)
            canvas.setFont('Helvetica-Bold', 8)
            text_width = canvas.stringWidth(text, 'Helvetica-Bold', 8)
            canvas.drawString(
                (self.width - text_width) / 2,
                (self.height - 8) / 2,
                text
            )

class Timeline(Flowable):
    """Timeline flowable for displaying chronological events"""
    
    def __init__(self, events, width=6*inch, config=None):
        self.events = events  # List of {'date': str, 'title': str, 'description': str}
        self.width = width
        self.config = config
        self.height = len(events) * 0.8*inch + 0.5*inch
    
    def draw(self):
        """Draw timeline"""
        canvas = self.canv
        
        # Timeline line
        line_x = 1*inch
        canvas.setStrokeColor(colors.grey)
        canvas.setLineWidth(3)
        canvas.line(line_x, 0.25*inch, line_x, self.height - 0.25*inch)
        
        # Events
        y_position = self.height - 0.5*inch
        for event in self.events:
            # Event dot
            canvas.setFillColor(colors.blue)
            canvas.circle(line_x, y_position, 5, fill=1, stroke=0)
            
            # Event content
            canvas.setFillColor(colors.black)
            canvas.setFont('Helvetica-Bold', 10)
            canvas.drawString(line_x + 20, y_position + 5, event.get('date', ''))
            
            canvas.setFont('Helvetica-Bold', 12)
            canvas.drawString(line_x + 20, y_position - 10, event.get('title', ''))
            
            canvas.setFont('Helvetica', 9)
            description = event.get('description', '')[:80]  # Truncate for space
            canvas.drawString(line_x + 20, y_position - 25, description)
            
            y_position -= 0.8*inch

class SmartContentProcessor(DocumentProcessor):
    """Advanced content processor with intelligent parsing"""
    
    def __init__(self, config: PDFConfig):
        super().__init__(config)
        self.section_counter = 0
        self.image_cache = {}
        
    def process_content(self, content: Any) -> List[Flowable]:
        """Main content processing method"""
        if isinstance(content, str):
            return self._process_text_content(content)
        elif isinstance(content, dict):
            return self._process_structured_content(content)
        elif isinstance(content, list):
            return self._process_list_content(content)
        else:
            return [Paragraph(str(content), self.style_manager.styles['BodyEnhanced'])]
    
    def _process_text_content(self, text: str) -> List[Flowable]:
        """Process plain text with smart formatting detection"""
        flowables = []
        lines = text.split('\n')
        current_block = []
        in_code_block = False
        in_quote_block = False
        
        for line in lines:
            stripped = line.strip()
            
            # Handle empty lines
            if not stripped:
                if current_block:
                    flowables.extend(self._process_text_block(current_block, in_code_block, in_quote_block))
                    current_block = []
                flowables.append(Spacer(1, 6))
                continue
            
            # Detect code blocks
            if stripped.startswith('```'):
                if current_block:
                    flowables.extend(self._process_text_block(current_block, in_code_block, in_quote_block))
                    current_block = []
                in_code_block = not in_code_block
                continue
            
            # Detect quote blocks
            if stripped.startswith('>'):
                if not in_quote_block and current_block:
                    flowables.extend(self._process_text_block(current_block, in_code_block, in_quote_block))
                    current_block = []
                in_quote_block = True
                current_block.append(stripped[1:].strip())
                continue
            else:
                if in_quote_block:
                    flowables.extend(self._process_text_block(current_block, in_code_block, True))
                    current_block = []
                    in_quote_block = False
            
            # Detect headers
            if self._is_header(stripped):
                if current_block:
                    flowables.extend(self._process_text_block(current_block, in_code_block, in_quote_block))
                    current_block = []
                flowables.append(self._create_header(stripped))
                continue
            
            # Detect special blocks
            special_block = self._detect_special_block(stripped)
            if special_block:
                if current_block:
                    flowables.extend(self._process_text_block(current_block, in_code_block, in_quote_block))
                    current_block = []
                flowables.append(special_block)
                continue
            
            current_block.append(line)
        
        # Process remaining block
        if current_block:
            flowables.extend(self._process_text_block(current_block, in_code_block, in_quote_block))
        
        return flowables
    
    def _is_header(self, line: str) -> bool:
        """Detect if line is a header"""
        # Markdown style headers
        if re.match(r'^#{1,6}\s+', line):
            return True
        # Underlined headers
        if len(line) > 0 and all(c in '=-~^' for c in line):
            return True
        # ALL CAPS headers (basic detection)
        if line.isupper() and len(line) > 3 and not line.startswith('['):
            return True
        return False
    
    def _create_header(self, line: str) -> Flowable:
        """Create header flowable"""
        # Markdown style
        if line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            text = line.lstrip('# ').strip()
            style_name = f'Heading{min(level, 6)}Enhanced'
        else:
            # Default to H2 for other header types
            text = line.strip()
            style_name = 'Heading2Enhanced'
        
        # Add section numbering if enabled
        if self.config.section_numbering:
            self.section_counter += 1
            text = f"{self.section_counter}. {text}"
        
        return Paragraph(text, self.style_manager.styles[style_name])
    
    def _detect_special_block(self, line: str) -> Optional[Flowable]:
        """Detect and create special content blocks"""
        
        # Info boxes
        info_patterns = {
            r'^\[INFO\](.*)': ('info', lambda m: m.group(1).strip()),
            r'^\[WARNING\](.*)': ('warning', lambda m: m.group(1).strip()),
            r'^\[ERROR\](.*)': ('error', lambda m: m.group(1).strip()),
            r'^\[SUCCESS\](.*)': ('success', lambda m: m.group(1).strip()),
            r'^\[TIP\](.*)': ('tip', lambda m: m.group(1).strip()),
        }
        
        for pattern, (box_type, extractor) in info_patterns.items():
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                content = extractor(match)
                return InfoBox(content, box_type, config=self.config)
        
        # Progress bars
        progress_match = re.match(r'^\[PROGRESS:(\d+)\](.*)$', line, re.IGNORECASE)
        if progress_match:
            percentage = int(progress_match.group(1))
            label = progress_match.group(2).strip()
            return KeepTogether([
                Paragraph(label, self.style_manager.styles['Normal']) if label else Spacer(1, 0),
                ProgressBar(percentage, color=self.config.color_palette.primary)
            ])
        
        # Horizontal rules
        if re.match(r'^-{3,}$|^\*{3,}$|^_{3,}$', line):
            return self._create_horizontal_rule()
        
        return None
    
    def _create_horizontal_rule(self) -> Flowable:
        """Create horizontal rule"""
        class HorizontalRule(Flowable):
            def __init__(self, width, color=colors.grey):
                self.width = width
                self.height = 0.1*inch
                self.color = color
            
            def draw(self):
                self.canv.setStrokeColor(self.color)
                self.canv.setLineWidth(1)
                self.canv.line(0, self.height/2, self.width, self.height/2)
        
        content_width, _ = self.config.layout.get_content_area()
        return HorizontalRule(content_width, self.config.color_palette.muted)
    
    def _process_text_block(self, lines: List[str], is_code: bool, is_quote: bool) -> List[Flowable]:
        """Process a block of text lines"""
        if not lines:
            return []
        
        text = '\n'.join(lines)
        
        if is_code:
            return [Paragraph(f"<pre>{text}</pre>", self.style_manager.styles['CodeBlockEnhanced'])]
        elif is_quote:
            return [Paragraph(text, self.style_manager.styles['QuoteEnhanced'])]
        else:
            # Enhanced text processing with inline formatting
            processed_text = self._process_inline_formatting(text)
            return [Paragraph(processed_text, self.style_manager.styles['BodyEnhanced'])]
    
    def _process_inline_formatting(self, text: str) -> str:
        """Process inline formatting like **bold**, *italic*, etc."""
        # Bold text
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'__(.*?)__', r'<b>\1</b>', text)
        
        # Italic text
        text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
        text = re.sub(r'_(.*?)_', r'<i>\1</i>', text)
        
        # Inline code
        text = re.sub(r'`(.*?)`', r'<font name="Courier" backColor="lightgrey">\1</font>', text)
        
        # Links (basic)
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<link href="\2">\1</link>', text)
        
        # Highlight
        text = re.sub(r'==(.*?)==', r'<font backColor="yellow">\1</font>', text)
        
        return text

class EnhancedTableProcessor:
    """Advanced table processing with styling and features"""
    
    def __init__(self, config: PDFConfig):
        self.config = config
    
    def create_enhanced_table(
        self, 
        data: List[List[str]], 
        headers: Optional[List[str]] = None,
        table_style: str = 'default',
        col_widths: Optional[List[float]] = None,
        row_heights: Optional[List[float]] = None
    ) -> Table:
        """Create an enhanced table with advanced styling"""
        
        # Prepare data
        if headers:
            full_data = [headers] + data
        else:
            full_data = data
        
        if not full_data:
            return None
        
        # Calculate column widths if not provided
        if col_widths is None:
            content_width, _ = self.config.layout.get_content_area()
            col_count = len(full_data[0])
            col_widths = [content_width / col_count] * col_count
        
        table = Table(full_data, colWidths=col_widths, rowHeights=row_heights)
        
        # Apply styling based on table style
        style_commands = self._get_table_style_commands(table_style, len(full_data), len(full_data[0]))
        table.setStyle(TableStyle(style_commands))
        
        return table
    
    def _get_table_style_commands(self, style_name: str, rows: int, cols: int) -> List:
        """Get table style commands based on style name"""
        colors_pal = self.config.color_palette
        
        base_commands = [
            ('FONTNAME', (0, 0), (-1, -1), self.config.typography.primary_font),
            ('FONTSIZE', (0, 0), (-1, -1), self.config.typography.base_size),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]
        
        style_configs = {
            'default': [
                ('BACKGROUND', (0, 0), (-1, 0), colors_pal.primary),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), f"{self.config.typography.primary_font}-Bold"),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors_pal.muted)
            ],
            'striped': [
                ('BACKGROUND', (0, 0), (-1, 0), colors_pal.primary),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), f"{self.config.typography.primary_font}-Bold"),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors_pal.background]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors_pal.muted)
            ],
            'minimal': [
                ('FONTNAME', (0, 0), (-1, 0), f"{self.config.typography.primary_font}-Bold"),
                ('LINEBELOW', (0, 0), (-1, 0), 2, colors_pal.primary),
                ('LINEBELOW', (0, -1), (-1, -1), 1, colors_pal.muted)
            ],
            'corporate': [
                ('BACKGROUND', (0, 0), (-1, 0), colors_pal.primary),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), f"{self.config.typography.primary_font}-Bold"),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('BOX', (0, 0), (-1, -1), 2, colors_pal.primary),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors_pal.secondary)
            ]
        }
        
        style_commands = style_configs.get(style_name, style_configs['default'])
        return base_commands + style_commands

class EnhancedImageProcessor:
    """Advanced image processing and handling"""
    
    def __init__(self, config: PDFConfig):
        self.config = config
        self.image_cache = {}
    
    def process_image(
        self, 
        image_source: Union[str, bytes], 
        width: Optional[float] = None,
        height: Optional[float] = None,
        caption: Optional[str] = None,
        alignment: str = 'center'
    ) -> List[Flowable]:
        """Process and create image flowable with caption"""
        flowables = []
        
        try:
            # Handle different image sources
            if isinstance(image_source, str):
                if image_source.startswith(('http://', 'https://')):
                    # Download image
                    response = requests.get(image_source)
                    image_data = BytesIO(response.content)
                else:
                    # Local file
                    image_data = image_source
            else:
                # Bytes data
                image_data = BytesIO(image_source)
            
            # Create image
            img = Image(image_data, width=width, height=height)
            
            # Wrap with alignment
            if alignment == 'center':
                content_width, _ = self.config.layout.get_content_area()
                img.hAlign = 'CENTER'
            elif alignment == 'right':
                img.hAlign = 'RIGHT'
            else:
                img.hAlign = 'LEFT'
            
            flowables.append(img)
            
            # Add caption if provided
            if caption:
                caption_para = Paragraph(
                    f"<i>{caption}</i>", 
                    self.style_manager.styles['CaptionEnhanced']
                )
                flowables.append(caption_para)
                flowables.append(Spacer(1, 6))
            
        except Exception as e:
            # Fallback to text if image fails
            error_text = f"[Image could not be loaded: {str(e)}]"
            flowables.append(Paragraph(error_text, self.style_manager.styles['Normal']))
        
        return flowables
    
"""
Ultra-Enhanced PDF MCP Server - Part 3: Advanced Chart Generation & Data Visualization
Beautiful charts, dashboards, infographics, and advanced data visualization components
"""

import math
import statistics
import colorsys
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field

from reportlab.platypus import Flowable, Spacer, Table, TableStyle, KeepTogether, Paragraph
from reportlab.lib.units import inch
from reportlab.lib.colors import Color, HexColor
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.barcharts import VerticalBarChart, HorizontalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.doughnut import Doughnut
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.charts.textlabels import Label
from reportlab.lib.enums import TA_LEFT, TA_CENTER

logger = logging.getLogger('gmail-mcp')

@dataclass
class ChartDataPoint:
    """Enhanced data point with metadata"""
    value: float
    label: str = ""
    color: Optional[Color] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ChartSeries:
    """Chart data series with styling"""
    name: str
    data: List[ChartDataPoint]
    color: Optional[Color] = None
    style: Dict[str, Any] = field(default_factory=dict)

class ColorGenerator:
    """Advanced color palette generator for charts"""
    
    def __init__(self, base_color: Color = None, scheme: str = 'analogous'):
        self.base_color = base_color or colors.blue
        self.scheme = scheme
        self._color_cache = {}
    
    def generate_palette(self, count: int) -> List[Color]:
        """Generate color palette with specified count"""
        cache_key = f"{self.scheme}_{count}"
        if cache_key in self._color_cache:
            return self._color_cache[cache_key]
        
        if self.scheme == 'analogous':
            colors_list = self._generate_analogous(count)
        elif self.scheme == 'complementary':
            colors_list = self._generate_complementary(count)
        elif self.scheme == 'triadic':
            colors_list = self._generate_triadic(count)
        elif self.scheme == 'rainbow':
            colors_list = self._generate_rainbow(count)
        elif self.scheme == 'gradient':
            colors_list = self._generate_gradient(count)
        else:
            colors_list = self._generate_distinct(count)
        
        self._color_cache[cache_key] = colors_list
        return colors_list
    
    def _rgb_to_hsv(self, color: Color) -> Tuple[float, float, float]:
        """Convert RGB color to HSV"""
        return colorsys.rgb_to_hsv(color.red, color.green, color.blue)
    
    def _hsv_to_color(self, h: float, s: float, v: float) -> Color:
        """Convert HSV to Color object"""
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return Color(r, g, b)
    
    def _generate_analogous(self, count: int) -> List[Color]:
        """Generate analogous color scheme"""
        h, s, v = self._rgb_to_hsv(self.base_color)
        colors_list = []
        
        for i in range(count):
            # Shift hue by small amounts
            new_h = (h + (i * 0.1)) % 1.0
            colors_list.append(self._hsv_to_color(new_h, s, v))
        
        return colors_list
    
    def _generate_complementary(self, count: int) -> List[Color]:
        """Generate complementary color scheme"""
        h, s, v = self._rgb_to_hsv(self.base_color)
        colors_list = [self.base_color]
        
        if count > 1:
            # Complementary color
            comp_h = (h + 0.5) % 1.0
            colors_list.append(self._hsv_to_color(comp_h, s, v))
        
        # Fill remaining with variations
        for i in range(2, count):
            variation_h = (h + (i * 0.15)) % 1.0
            colors_list.append(self._hsv_to_color(variation_h, s * 0.8, v))
        
        return colors_list
    
    def _generate_triadic(self, count: int) -> List[Color]:
        """Generate triadic color scheme"""
        h, s, v = self._rgb_to_hsv(self.base_color)
        colors_list = [self.base_color]
        
        if count > 1:
            colors_list.append(self._hsv_to_color((h + 1/3) % 1.0, s, v))
        if count > 2:
            colors_list.append(self._hsv_to_color((h + 2/3) % 1.0, s, v))
        
        # Fill remaining with variations
        for i in range(3, count):
            variation_h = (h + (i * 0.1)) % 1.0
            colors_list.append(self._hsv_to_color(variation_h, s * 0.7, v))
        
        return colors_list
    
    def _generate_rainbow(self, count: int) -> List[Color]:
        """Generate rainbow color scheme"""
        colors_list = []
        for i in range(count):
            h = i / count
            colors_list.append(self._hsv_to_color(h, 0.8, 0.9))
        return colors_list
    
    def _generate_gradient(self, count: int) -> List[Color]:
        """Generate gradient from base color"""
        h, s, v = self._rgb_to_hsv(self.base_color)
        colors_list = []
        
        for i in range(count):
            factor = i / max(1, count - 1)
            new_v = v * (0.3 + 0.7 * factor)  # Vary brightness
            new_s = s * (0.5 + 0.5 * factor)  # Vary saturation
            colors_list.append(self._hsv_to_color(h, new_s, new_v))
        
        return colors_list
    
    def _generate_distinct(self, count: int) -> List[Color]:
        """Generate visually distinct colors"""
        # Predefined distinct colors
        distinct_colors = [
            colors.blue, colors.red, colors.green, colors.orange,
            colors.purple, colors.brown, colors.pink, colors.grey,
            colors.olive, colors.cyan, colors.magenta, colors.yellow,
            HexColor('#FF6B6B'), HexColor('#4ECDC4'), HexColor('#45B7D1'),
            HexColor('#96CEB4'), HexColor('#FFEAA7'), HexColor('#DDA0DD')
        ]
        
        if count <= len(distinct_colors):
            return distinct_colors[:count]
        
        # Generate additional colors if needed
        colors_list = distinct_colors.copy()
        for i in range(len(distinct_colors), count):
            h = (i * 0.618034) % 1.0  # Golden ratio for distribution
            colors_list.append(self._hsv_to_color(h, 0.7, 0.8))
        
        return colors_list

class EnhancedChart(Flowable):
    """Base class for enhanced charts with advanced styling"""
    
    def __init__(self, width: float, height: float, config=None):
        self.width = width
        self.height = height
        self.config = config
        self.drawing = Drawing(width, height)
        if config and hasattr(config, 'color_palette'):
            self.color_generator = ColorGenerator(config.color_palette.primary)
        else:
            self.color_generator = ColorGenerator(colors.blue)
    
    def add_title(self, title: str, y_offset: float = 0):
        """Add title to chart"""
        title_label = Label()
        title_label.setOrigin(self.width/2, self.height - 30 + y_offset)
        title_label.boxAnchor = 'n'
        title_label.setText(title)
        title_label.fontSize = 16
        title_label.fontName = "Helvetica-Bold"
        if self.config and hasattr(self.config, 'color_palette'):
            title_label.fillColor = self.config.color_palette.primary
        else:
            title_label.fillColor = colors.darkblue
        self.drawing.add(title_label)
    
    def add_subtitle(self, subtitle: str, y_offset: float = 0):
        """Add subtitle to chart"""
        subtitle_label = Label()
        subtitle_label.setOrigin(self.width/2, self.height - 50 + y_offset)
        subtitle_label.boxAnchor = 'n'
        subtitle_label.setText(subtitle)
        subtitle_label.fontSize = 12
        subtitle_label.fontName = "Helvetica-Oblique"
        if self.config and hasattr(self.config, 'color_palette'):
            subtitle_label.fillColor = self.config.color_palette.secondary
        else:
            subtitle_label.fillColor = colors.darkgrey
        self.drawing.add(subtitle_label)
    
    def add_background(self, gradient: bool = False):
        """Add background to chart"""
        if gradient:
            # Create gradient background
            steps = 20
            step_height = self.height / steps
            start_color = Color(0.98, 0.98, 0.98)
            end_color = Color(0.94, 0.94, 0.94)
            
            for i in range(steps):
                ratio = i / steps
                r = start_color.red + (end_color.red - start_color.red) * ratio
                g = start_color.green + (end_color.green - start_color.green) * ratio
                b = start_color.blue + (end_color.blue - start_color.blue) * ratio
                
                rect = Rect(0, i * step_height, self.width, step_height)
                rect.fillColor = Color(r, g, b)
                rect.strokeColor = None
                self.drawing.add(rect)
        else:
            # Simple background
            bg = Rect(0, 0, self.width, self.height)
            bg.fillColor = colors.white
            bg.strokeColor = colors.lightgrey
            bg.strokeWidth = 1
            self.drawing.add(bg)

class EnhancedBarChart(EnhancedChart):
    """Enhanced bar chart with advanced styling and features"""
    
    def __init__(self, width: float = 6*inch, height: float = 4*inch, config=None):
        super().__init__(width, height, config)
        self.chart = None
        self.data_series = []
    
    def add_data_series(self, series: ChartSeries):
        """Add data series to chart"""
        self.data_series.append(series)
    
    def create_chart(self, 
                    title: str = "", 
                    subtitle: str = "",
                    orientation: str = 'vertical',
                    show_values: bool = True,
                    show_grid: bool = True,
                    stacked: bool = False) -> Drawing:
        """Create enhanced bar chart"""
        
        # Add background
        self.add_background(gradient=True)
        
        # Choose chart type
        if orientation == 'vertical':
            chart = VerticalBarChart()
            chart.x = 60
            chart.y = 60
            chart.width = self.width - 120
            chart.height = self.height - 140
        else:
            chart = HorizontalBarChart()
            chart.x = 80
            chart.y = 60
            chart.width = self.width - 140
            chart.height = self.height - 120
        
        # Prepare data
        if self.data_series:
            chart.data = []
            colors_list = self.color_generator.generate_palette(max(len(self.data_series), 
                                                                   len(self.data_series[0].data) if self.data_series else 1))
            
            for i, series in enumerate(self.data_series):
                values = [dp.value for dp in series.data]
                chart.data.append(values)
                
                # Set colors for bars
                for j in range(len(values)):
                    if hasattr(chart, 'bars') and len(chart.bars) > j:
                        if stacked:
                            chart.bars[j][i].fillColor = colors_list[i]
                        else:
                            chart.bars[j].fillColor = colors_list[j % len(colors_list)]
        
        # Styling
        chart.strokeColor = colors.grey
        chart.strokeWidth = 1
        
        # Axes styling
        if hasattr(chart, 'valueAxis'):
            chart.valueAxis.valueMin = 0
            chart.valueAxis.strokeColor = colors.black
            chart.valueAxis.labelTextFormat = '%0.0f'
            chart.valueAxis.labels.fontName = 'Helvetica'
            chart.valueAxis.labels.fontSize = 8
            
            if show_grid:
                chart.valueAxis.visibleGrid = 1
                chart.valueAxis.gridStrokeColor = Color(0.9, 0.9, 0.9)
        
        if hasattr(chart, 'categoryAxis'):
            chart.categoryAxis.strokeColor = colors.black
            chart.categoryAxis.labels.fontName = 'Helvetica'
            chart.categoryAxis.labels.fontSize = 8
            chart.categoryAxis.labels.angle = 0
            
            # Set category labels
            if self.data_series and self.data_series[0].data:
                chart.categoryAxis.categoryNames = [dp.label for dp in self.data_series[0].data]
        
        self.drawing.add(chart)
        
        # Add titles
        if title:
            self.add_title(title)
        if subtitle:
            self.add_subtitle(subtitle)
        
        # Add legend if multiple series
        if len(self.data_series) > 1:
            self._add_legend()
        
        return self.drawing
    
    def _add_legend(self):
        """Add legend to chart"""
        legend = Legend()
        legend.x = self.width - 150
        legend.y = self.height - 80
        legend.deltax = 10
        legend.deltay = 10
        legend.fontName = 'Helvetica'
        legend.fontSize = 8
        legend.boxAnchor = 'nw'
        
        legend.colorNamePairs = []
        colors_list = self.color_generator.generate_palette(len(self.data_series))
        
        for i, series in enumerate(self.data_series):
            legend.colorNamePairs.append((colors_list[i], series.name))
        
        self.drawing.add(legend)

class EnhancedPieChart(EnhancedChart):
    """Enhanced pie chart with advanced styling"""
    
    def __init__(self, width: float = 6*inch, height: float = 4*inch, config=None):
        super().__init__(width, height, config)
        self.data_points = []
    
    def add_data(self, data_points: List[ChartDataPoint]):
        """Add data points to pie chart"""
        self.data_points = data_points
    
    def create_chart(self,
                    title: str = "",
                    subtitle: str = "",
                    chart_type: str = 'pie',  # 'pie' or 'doughnut'
                    show_percentages: bool = True,
                    explode_largest: bool = False) -> Drawing:
        """Create enhanced pie chart"""
        
        # Add background
        self.add_background()
        
        # Choose chart type
        if chart_type == 'doughnut':
            chart = Doughnut()
            chart.innerRadiusFraction = 0.4
        else:
            chart = Pie()
        
        # Position chart
        chart.x = self.width / 2 - 100
        chart.y = self.height / 2 - 50
        chart.width = 200
        chart.height = 200
        
        # Prepare data
        if self.data_points:
            chart.data = [dp.value for dp in self.data_points]
            chart.labels = [dp.label for dp in self.data_points]
            
            # Generate colors
            colors_list = self.color_generator.generate_palette(len(self.data_points))
            
            # Apply colors and styling
            for i in range(len(self.data_points)):
                if i < len(chart.slices):
                    chart.slices[i].fillColor = colors_list[i]
                    chart.slices[i].strokeColor = colors.white
                    chart.slices[i].strokeWidth = 2
                    
                    # Explode largest slice if requested
                    if explode_largest and i == 0:  # Assume first is largest
                        chart.slices[i].popout = 10
        
        # Label styling
        if hasattr(chart, 'slices'):
            chart.slices.fontName = 'Helvetica'
            chart.slices.fontSize = 8
            chart.slices.labelRadius = 1.2
        
        if show_percentages and self.data_points:
            total = sum(dp.value for dp in self.data_points)
            chart.labels = [f"{dp.label}\n{(dp.value/total)*100:.1f}%" 
                           for dp in self.data_points]
        
        self.drawing.add(chart)
        
        # Add titles
        if title:
            self.add_title(title)
        if subtitle:
            self.add_subtitle(subtitle)
        
        return self.drawing

class DashboardWidget(Flowable):
    """Dashboard widget for KPI displays"""
    
    def __init__(self, title: str, value: str, subtitle: str = "", 
                 icon: str = "", trend: str = "", width: float = 2*inch, 
                 height: float = 1.5*inch, config=None):
        self.title = title
        self.value = value
        self.subtitle = subtitle
        self.icon = icon
        self.trend = trend
        self.width = width
        self.height = height
        self.config = config
    
    def draw(self):
        """Draw dashboard widget"""
        canvas = self.canv
        
        # Background with gradient effect
        if self.config and hasattr(self.config, 'color_palette'):
            bg_color = self.config.color_palette.background
            primary_color = self.config.color_palette.primary
            text_color = self.config.color_palette.text
            success_color = getattr(self.config.color_palette, 'success', colors.green)
            error_color = getattr(self.config.color_palette, 'error', colors.red)
        else:
            bg_color = colors.white
            primary_color = colors.blue
            text_color = colors.black
            success_color = colors.green
            error_color = colors.red
        
        # Main background
        canvas.setFillColor(bg_color)
        canvas.setStrokeColor(primary_color)
        canvas.setLineWidth(2)
        canvas.roundRect(0, 0, self.width, self.height, 10, fill=1, stroke=1)
        
        # Header bar
        canvas.setFillColor(primary_color)
        canvas.roundRect(0, self.height - 30, self.width, 30, 10, fill=1, stroke=0)
        
        # Title
        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawCentredText(self.width/2, self.height - 20, self.title)
        
        # Main value
        canvas.setFillColor(primary_color)
        canvas.setFont("Helvetica-Bold", 24)
        canvas.drawCentredText(self.width/2, self.height/2 + 10, self.value)
        
        # Subtitle
        if self.subtitle:
            canvas.setFillColor(text_color)
            canvas.setFont("Helvetica", 8)
            canvas.drawCentredText(self.width/2, self.height/2 - 20, self.subtitle)
        
        # Trend indicator
        if self.trend:
            trend_color = success_color if self.trend.startswith('+') else error_color
            canvas.setFillColor(trend_color)
            canvas.setFont("Helvetica-Bold", 10)
            canvas.drawCentredText(self.width/2, 15, self.trend)

class ChartFactory:
    """Factory for creating various chart types"""
    
    def __init__(self, config=None):
        self.config = config
    
    def create_chart(self, chart_type: str, data: Dict[str, Any], 
                    width: float = 6*inch, height: float = 4*inch) -> Flowable:
        """Create chart based on type and data"""
        
        if chart_type == 'bar':
            return self._create_bar_chart(data, width, height)
        elif chart_type == 'pie':
            return self._create_pie_chart(data, width, height)
        elif chart_type == 'line':
            return self._create_line_chart(data, width, height)
        elif chart_type == 'dashboard':
            return self._create_dashboard(data, width, height)
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")
    
    def _create_bar_chart(self, data: Dict[str, Any], width: float, height: float) -> Flowable:
        """Create bar chart from data"""
        chart = EnhancedBarChart(width, height, self.config)
        
        # Process data
        series_data = data.get('series', [])
        for series_info in series_data:
            data_points = []
            for item in series_info.get('data', []):
                data_points.append(ChartDataPoint(
                    value=item.get('value', 0),
                    label=item.get('label', '')
                ))
            
            series = ChartSeries(
                name=series_info.get('name', ''),
                data=data_points
            )
            chart.add_data_series(series)
        
        return chart.create_chart(
            title=data.get('title', ''),
            subtitle=data.get('subtitle', ''),
            orientation=data.get('orientation', 'vertical'),
            show_values=data.get('show_values', True),
            show_grid=data.get('show_grid', True)
        )
    
    def _create_pie_chart(self, data: Dict[str, Any], width: float, height: float) -> Flowable:
        """Create pie chart from data"""
        chart = EnhancedPieChart(width, height, self.config)
        
        # Process data
        data_points = []
        for item in data.get('data', []):
            data_points.append(ChartDataPoint(
                value=item.get('value', 0),
                label=item.get('label', '')
            ))
        
        chart.add_data(data_points)
        
        return chart.create_chart(
            title=data.get('title', ''),
            subtitle=data.get('subtitle', ''),
            chart_type=data.get('chart_type', 'pie'),
            show_percentages=data.get('show_percentages', True)
        )
    
    def _create_line_chart(self, data: Dict[str, Any], width: float, height: float) -> Flowable:
        """Create line chart from data"""
        # For now, create as bar chart - line chart implementation would be similar
        return self._create_bar_chart(data, width, height)
    
    def _create_dashboard(self, data: Dict[str, Any], width: float, height: float) -> Flowable:
        """Create dashboard layout with multiple widgets"""
        widgets = []
        widget_data = data.get('widgets', [])
        
        # Calculate widget dimensions
        cols = data.get('columns', 2)
        rows = math.ceil(len(widget_data) / cols)
        widget_width = (width - (cols - 1) * 0.2*inch) / cols
        widget_height = (height - (rows - 1) * 0.2*inch) / rows
        
        # Create dashboard table
        dashboard_data = []
        for row in range(rows):
            row_widgets = []
            for col in range(cols):
                widget_index = row * cols + col
                if widget_index < len(widget_data):
                    widget_info = widget_data[widget_index]
                    widget = DashboardWidget(
                        title=widget_info.get('title', ''),
                        value=widget_info.get('value', ''),
                        subtitle=widget_info.get('subtitle', ''),
                        trend=widget_info.get('trend', ''),
                        width=widget_width,
                        height=widget_height,
                        config=self.config
                    )
                    row_widgets.append(widget)
                else:
                    # Empty cell
                    row_widgets.append(Spacer(widget_width, widget_height))
            dashboard_data.append(row_widgets)
        
        # Create table for layout
        dashboard_table = Table(dashboard_data)
        dashboard_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        
        return dashboard_table

class DataAnalyzer:
    """Analyze data and suggest appropriate visualizations"""
    
    @staticmethod
    def analyze_data(data: Union[List, Dict]) -> Dict[str, Any]:
        """Analyze data structure and suggest visualization"""
        if isinstance(data, list):
            return DataAnalyzer._analyze_list_data(data)
        elif isinstance(data, dict):
            return DataAnalyzer._analyze_dict_data(data)
        else:
            return {'suggested_chart': 'table', 'reason': 'Unknown data structure'}
    
    @staticmethod
    def _analyze_list_data(data: List) -> Dict[str, Any]:
        """Analyze list data"""
        if not data:
            return {'suggested_chart': 'table', 'reason': 'Empty data'}
        
        # Check if it's numerical data
        if all(isinstance(item, (int, float)) for item in data):
            if len(data) <= 10:
                return {'suggested_chart': 'bar', 'reason': 'Small numerical dataset'}
            else:
                return {'suggested_chart': 'line', 'reason': 'Large numerical dataset'}
        
        # Check if it's categorical data
        if all(isinstance(item, str) for item in data):
            unique_values = len(set(data))
            if unique_values <= 8:
                return {'suggested_chart': 'pie', 'reason': 'Categorical data with few categories'}
            else:
                return {'suggested_chart': 'bar', 'reason': 'Categorical data with many categories'}
        
        return {'suggested_chart': 'table', 'reason': 'Mixed data types'}
    
    @staticmethod
    def _analyze_dict_data(data: Dict) -> Dict[str, Any]:
        """Analyze dictionary data"""
        if not data:
            return {'suggested_chart': 'table', 'reason': 'Empty data'}
        
        # Check if it's key-value pairs with numerical values
        if all(isinstance(v, (int, float)) for v in data.values()):
            if len(data) <= 8:
                return {'suggested_chart': 'pie', 'reason': 'Key-value pairs suitable for pie chart'}
            else:
                return {'suggested_chart': 'bar', 'reason': 'Many key-value pairs suitable for bar chart'}
        
        # Check if it's time series data
        if any(key.lower() in ['date', 'time', 'timestamp'] for key in data.keys()):
            return {'suggested_chart': 'line', 'reason': 'Time series data detected'}
        
        return {'suggested_chart': 'table', 'reason': 'Complex dictionary structure'}

class AdvancedVisualizationProcessor:
    """Advanced processor for creating sophisticated visualizations"""
    
    def __init__(self, config=None):
        self.config = config
        self.chart_factory = ChartFactory(config)
        if config and hasattr(config, 'color_palette'):
            self.color_generator = ColorGenerator(config.color_palette.primary)
        else:
            self.color_generator = ColorGenerator(colors.blue)
    
    def create_visualization(self, data: Any, chart_type: str = 'auto', 
                           title: str = "", subtitle: str = "",
                           width: float = 6*inch, height: float = 4*inch,
                           **kwargs) -> List[Flowable]:
        """Create visualization from data"""
        flowables = []
        
        # Auto-detect chart type if requested
        if chart_type == 'auto':
            analysis = DataAnalyzer.analyze_data(data)
            chart_type = analysis['suggested_chart']
            if not title:
                title = f"Data Visualization ({analysis['reason']})"
        
        # Prepare data for chart creation
        chart_data = self._prepare_chart_data(data, chart_type)
        chart_data.update({
            'title': title,
            'subtitle': subtitle,
            **kwargs
        })
        
        try:
            # Create the chart
            chart = self.chart_factory.create_chart(chart_type, chart_data, width, height)
            flowables.append(chart)
            
            # Add data summary if requested
            if kwargs.get('show_summary', False):
                summary = self._create_data_summary(data)
                flowables.append(Spacer(1, 12))
                flowables.append(summary)
                
        except Exception as e:
            # Fallback to simple text if chart creation fails
            logger.warning(f"Chart creation failed: {e}. Falling back to text representation.")
            from reportlab.lib.styles import getSampleStyleSheet
            styles = getSampleStyleSheet()
            error_text = f"Chart could not be created: {str(e)}\nData: {str(data)[:200]}..."
            from reportlab.lib.styles import getSampleStyleSheet
            styles = getSampleStyleSheet()
            flowables.append(Paragraph(error_text, styles['Normal']))
        
        return flowables
    
    def _prepare_chart_data(self, data: Any, chart_type: str) -> Dict[str, Any]:
        """Prepare data for specific chart type"""
        if chart_type in ['pie', 'doughnut']:
            return self._prepare_pie_data(data)
        elif chart_type in ['bar', 'column']:
            return self._prepare_bar_data(data)
        elif chart_type == 'line':
            return self._prepare_line_data(data)
        elif chart_type == 'dashboard':
            return self._prepare_dashboard_data(data)
        else:
            return {'data': data}
    
    def _prepare_pie_data(self, data: Any) -> Dict[str, Any]:
        """Prepare data for pie chart"""
        if isinstance(data, dict):
            chart_data = []
            for label, value in data.items():
                if isinstance(value, (int, float)):
                    chart_data.append({'label': str(label), 'value': float(value)})
            return {'data': chart_data}
        elif isinstance(data, list) and all(isinstance(item, dict) for item in data):
            return {'data': data}
        else:
            # Convert list to simple frequency data
            from collections import Counter
            counter = Counter(data)
            chart_data = [{'label': str(k), 'value': v} for k, v in counter.items()]
            return {'data': chart_data}
    
    def _prepare_bar_data(self, data: Any) -> Dict[str, Any]:
        """Prepare data for bar chart"""
        if isinstance(data, dict):
            series_data = [{
                'name': 'Data Series',
                'data': [{'label': str(k), 'value': float(v)} for k, v in data.items()]
            }]
            return {'series': series_data}
        elif isinstance(data, list):
            if all(isinstance(item, dict) for item in data):
                # Assume it's already in the right format
                return {'series': [{'name': 'Series 1', 'data': data}]}
            else:
                # Convert simple list to bar data
                series_data = [{
                    'name': 'Values',
                    'data': [{'label': f'Item {i+1}', 'value': float(v)} 
                            for i, v in enumerate(data) if isinstance(v, (int, float))]
                }]
                return {'series': series_data}
        else:
            return {'series': []}
    
    def _prepare_line_data(self, data: Any) -> Dict[str, Any]:
        """Prepare data for line chart"""
        # Similar to bar data but optimized for time series
        return self._prepare_bar_data(data)
    
    def _prepare_dashboard_data(self, data: Any) -> Dict[str, Any]:
        """Prepare data for dashboard"""
        if isinstance(data, dict):
            widgets = []
            for key, value in data.items():
                widgets.append({
                    'title': str(key),
                    'value': str(value),
                    'subtitle': f"Current: {value}"
                })
            return {'widgets': widgets, 'columns': 2}
        return {'widgets': []}
    
    def _create_data_summary(self, data: Any) -> Flowable:
        """Create data summary statistics"""
        summary_text = "Data Summary:\n"
        
        if isinstance(data, list) and all(isinstance(x, (int, float)) for x in data):
            # Numerical summary
            summary_text += f"Count: {len(data)}\n"
            summary_text += f"Mean: {statistics.mean(data):.2f}\n"
            summary_text += f"Median: {statistics.median(data):.2f}\n"
            summary_text += f"Min: {min(data):.2f}\n"
            summary_text += f"Max: {max(data):.2f}\n"
            if len(data) > 1:
                summary_text += f"Std Dev: {statistics.stdev(data):.2f}\n"
        
        elif isinstance(data, dict):
            summary_text += f"Categories: {len(data)}\n"
            if all(isinstance(v, (int, float)) for v in data.values()):
                summary_text += f"Total: {sum(data.values()):.2f}\n"
                summary_text += f"Average: {statistics.mean(data.values()):.2f}\n"
        
        else:
            summary_text += f"Items: {len(data) if hasattr(data, '__len__') else 'Unknown'}\n"
            summary_text += f"Type: {type(data).__name__}\n"
        
        from reportlab.lib.styles import getSampleStyleSheet
        styles = getSampleStyleSheet()
        return Paragraph(summary_text, styles['Normal'])

# Progress Bar and Timeline Flowables
class ProgressBar(Flowable):
    """Custom progress bar flowable"""
    
    def __init__(self, percentage, width=4*inch, height=0.3*inch, 
                 color=colors.green, bg_color=colors.lightgrey, 
                 show_text=True, text_format="{percentage}%"):
        self.percentage = max(0, min(100, percentage))
        self.width = width
        self.height = height
        self.color = color
        self.bg_color = bg_color
        self.show_text = show_text
        self.text_format = text_format
    
    def draw(self):
        """Draw progress bar"""
        canvas = self.canv
        
        # Background
        canvas.setFillColor(self.bg_color)
        canvas.setStrokeColor(colors.grey)
        canvas.roundRect(0, 0, self.width, self.height, 5, fill=1, stroke=1)
        
        # Progress fill
        fill_width = (self.width - 4) * (self.percentage / 100)
        if fill_width > 0:
            canvas.setFillColor(self.color)
            canvas.roundRect(2, 2, fill_width, self.height - 4, 3, fill=1, stroke=0)
        
        # Text
        if self.show_text:
            text = self.text_format.format(percentage=self.percentage)
            canvas.setFillColor(colors.black)
            canvas.setFont('Helvetica-Bold', 8)
            text_width = canvas.stringWidth(text, 'Helvetica-Bold', 8)
            canvas.drawString(
                (self.width - text_width) / 2,
                (self.height - 8) / 2,
                text
            )

class Timeline(Flowable):
    """Timeline flowable for displaying chronological events"""
    
    def __init__(self, events, width=6*inch, config=None):
        self.events = events  # List of {'date': str, 'title': str, 'description': str}
        self.width = width
        self.config = config
        self.height = len(events) * 0.8*inch + 0.5*inch
    
    def draw(self):
        """Draw timeline"""
        canvas = self.canv
        
        # Timeline line
        line_x = 1*inch
        canvas.setStrokeColor(colors.grey)
        canvas.setLineWidth(3)
        canvas.line(line_x, 0.25*inch, line_x, self.height - 0.25*inch)
        
        # Events
        y_position = self.height - 0.5*inch
        for event in self.events:
            # Event dot
            canvas.setFillColor(colors.blue)
            canvas.circle(line_x, y_position, 5, fill=1, stroke=0)
            
            # Event content
            canvas.setFillColor(colors.black)
            canvas.setFont('Helvetica-Bold', 10)
            canvas.drawString(line_x + 20, y_position + 5, event.get('date', ''))
            
            canvas.setFont('Helvetica-Bold', 12)
            canvas.drawString(line_x + 20, y_position - 10, event.get('title', ''))
            
            canvas.setFont('Helvetica', 9)
            description = event.get('description', '')[:80]  # Truncate for space
            canvas.drawString(line_x + 20, y_position - 25, description)
            
            y_position -= 0.8*inch

class InfoBox(Flowable):
    """Enhanced info box with icons and styling"""
    
    def __init__(self, content, box_type='info', width=None, config=None):
        self.content = content
        self.box_type = box_type  # info, warning, error, success, tip
        self.width = width or 6*inch
        self.config = config
        self.height = self._calculate_height()
    
    def _calculate_height(self):
        """Calculate required height based on content"""
        # Simplified calculation - in real implementation would measure text
        lines = len(self.content.split('\n'))
        return max(1*inch, lines * 0.3*inch)
    
    def draw(self):
        """Draw styled info box"""
        canvas = self.canv
        
        # Define colors and icons for different box types
        box_configs = {
            'info': {'color': colors.lightblue, 'border': colors.blue, 'icon': 'ℹ'},
            'warning': {'color': colors.lightyellow, 'border': colors.orange, 'icon': '⚠'},
            'error': {'color': colors.pink, 'border': colors.red, 'icon': '✖'},
            'success': {'color': colors.lightgreen, 'border': colors.green, 'icon': '✓'},
            'tip': {'color': colors.lightgrey, 'border': colors.grey, 'icon': '💡'}
        }
        
        box_config = box_configs.get(self.box_type, box_configs['info'])
        
        # Draw background
        canvas.setFillColor(box_config['color'])
        canvas.setStrokeColor(box_config['border'])
        canvas.setLineWidth(2)
        canvas.roundRect(0, 0, self.width, self.height, 10, fill=1, stroke=1)
        
        # Draw icon
        canvas.setFillColor(box_config['border'])
        canvas.setFont('Helvetica-Bold', 16)
        canvas.drawString(15, self.height - 25, box_config['icon'])
        
        # Draw content (simplified - would use proper text wrapping in real implementation)
        canvas.setFillColor(colors.black)
        canvas.setFont('Helvetica', 10)
        y_position = self.height - 25
        for line in self.content.split('\n')[:5]:  # Limit to 5 lines for space
            canvas.drawString(45, y_position, line[:60])  # Truncate long lines
            y_position -= 15

# Utility functions for quick chart creation
def create_quick_chart(data: Any, chart_type: str = 'auto', config=None) -> List[Flowable]:
    """Quick utility function to create charts"""
    processor = AdvancedVisualizationProcessor(config)
    return processor.create_visualization(data, chart_type)

def create_dashboard(widgets_data: List[Dict[str, Any]], config=None, 
                    columns: int = 2, width: float = 6*inch, height: float = 4*inch) -> Flowable:
    """Quick utility to create dashboard"""
    factory = ChartFactory(config)
    dashboard_data = {
        'widgets': widgets_data,
        'columns': columns
    }
    return factory.create_chart('dashboard', dashboard_data, width, height)

def create_progress_bars(data: Dict[str, float], config=None) -> List[Flowable]:
    """Create multiple progress bars from data"""
    flowables = []
    for label, percentage in data.items():
        from reportlab.lib.styles import getSampleStyleSheet
        styles = getSampleStyleSheet()
        
        # Add label
        flowables.append(Paragraph(label, styles['Normal']))
        
        # Add progress bar
        color = colors.green if config is None else getattr(config.color_palette, 'primary', colors.green)
        flowables.append(ProgressBar(percentage, color=color))
        flowables.append(Spacer(1, 6))
    
    return flowables

def create_timeline_chart(events: List[Dict[str, str]], config=None) -> Flowable:
    """Create timeline from events data"""
    return Timeline(events, config=config)

def create_info_boxes(boxes_data: List[Dict[str, str]], config=None) -> List[Flowable]:
    """Create multiple info boxes"""
    flowables = []
    for box_data in boxes_data:
        box = InfoBox(
            content=box_data.get('content', ''),
            box_type=box_data.get('type', 'info'),
            config=config
        )
        flowables.append(box)
        flowables.append(Spacer(1, 12))
    
    return flowables