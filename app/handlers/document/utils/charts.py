import os
import logging
from typing import List, Dict
from reportlab.platypus import Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import numpy as np

logger = logging.getLogger('pdf-mcp')

def add_charts_to_story(story: List, charts_config: List[Dict]) -> List:
    try:
        for chart_config in charts_config:
            chart_type = chart_config.get('type', 'bar')
            data = chart_config.get('data', {})
            title = chart_config.get('title', 'Chart')
            
            if not data:
                continue
            
            try:
                # Create figure with better sizing
                fig, ax = plt.subplots(figsize=(10, 6))  # Consistent size
                
                if chart_type == 'bar':
                    x_data = data.get('labels', data.get('x', []))
                    y_data = data.get('values', data.get('y', []))
                    colors_list = data.get('colors', ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])
                    
                    bars = ax.bar(x_data, y_data, color=colors_list[:len(x_data)])
                    ax.set_xlabel(data.get('x_label', 'Categories'))
                    ax.set_ylabel(data.get('y_label', 'Values'))
                    
                    if data.get('show_values', False):
                        for bar in bars:
                            height_val = bar.get_height()
                            ax.text(bar.get_x() + bar.get_width()/2., height_val + max(y_data)*0.01,
                                   f'{height_val}', ha='center', va='bottom', fontweight='bold')
                
                elif chart_type == 'pie':
                    labels = data.get('labels', [])
                    values = data.get('values', [])
                    colors_list = data.get('colors', ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc'])
                    explode = data.get('explode', None)
                    
                    wedges, texts, autotexts = ax.pie(
                        values, 
                        labels=labels, 
                        autopct='%1.1f%%',
                        colors=colors_list[:len(values)],
                        explode=explode,
                        startangle=data.get('start_angle', 90),
                        textprops={'fontsize': 10}
                    )
                    
                    for autotext in autotexts:
                        autotext.set_color('white')
                        autotext.set_fontweight('bold')
                
                elif chart_type == 'line':
                    x_data = data.get('x', data.get('labels', []))
                    y_data = data.get('y', data.get('values', []))
                    
                    if isinstance(y_data[0], list):
                        colors_list = data.get('colors', ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
                        line_labels = data.get('line_labels', [f'Line {i+1}' for i in range(len(y_data))])
                        
                        for i, y_values in enumerate(y_data):
                            color = colors_list[i % len(colors_list)]
                            label = line_labels[i] if i < len(line_labels) else f'Line {i+1}'
                            ax.plot(x_data, y_values, marker='o', color=color, label=label, linewidth=2, markersize=4)
                        ax.legend()
                    else:
                        color = data.get('color', '#1f77b4')
                        ax.plot(x_data, y_data, marker='o', color=color, linewidth=2, markersize=6)
                    
                    ax.set_xlabel(data.get('x_label', 'X Axis'))
                    ax.set_ylabel(data.get('y_label', 'Y Axis'))
                    ax.grid(True, alpha=0.3)
                
                elif chart_type == 'histogram':
                    values = data.get('values', [])
                    bins = data.get('bins', 15)
                    color = data.get('color', '#1f77b4')
                    alpha = data.get('alpha', 0.7)
                    
                    n, bins_array, patches = ax.hist(values, bins=bins, color=color, alpha=alpha, edgecolor='black')
                    
                    ax.set_xlabel(data.get('x_label', 'Values'))
                    ax.set_ylabel(data.get('y_label', 'Frequency'))
                    ax.grid(True, alpha=0.3)
                    
                    if data.get('show_stats', False):
                        mean_val = np.mean(values)
                        ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, 
                                  label=f'Mean: {mean_val:.1f}')
                        ax.legend()
                
                elif chart_type == 'scatter':
                    x_data = data.get('x', [])
                    y_data = data.get('y', [])
                    colors_list = data.get('colors', None)
                    sizes = data.get('sizes', [60] * len(x_data))
                    
                    scatter = ax.scatter(x_data, y_data, c=colors_list, s=sizes, alpha=0.7, edgecolors='black')
                    
                    ax.set_xlabel(data.get('x_label', 'X Values'))
                    ax.set_ylabel(data.get('y_label', 'Y Values'))
                    ax.grid(True, alpha=0.3)
                    
                    if data.get('trend_line', False):
                        z = np.polyfit(x_data, y_data, 1)
                        p = np.poly1d(z)
                        ax.plot(x_data, p(x_data), "r--", alpha=0.8, linewidth=2)
                
                elif chart_type == 'hbar':
                    y_data = data.get('labels', data.get('y', []))
                    x_data = data.get('values', data.get('x', []))
                    colors_list = data.get('colors', ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])
                    
                    bars = ax.barh(y_data, x_data, color=colors_list[:len(y_data)])
                    ax.set_ylabel(data.get('y_label', 'Categories'))
                    ax.set_xlabel(data.get('x_label', 'Values'))
                    
                    if data.get('show_values', False):
                        for i, bar in enumerate(bars):
                            width = bar.get_width()
                            ax.text(width + max(x_data)*0.01, bar.get_y() + bar.get_height()/2.,
                                   f'{width}', ha='left', va='center', fontweight='bold')
                
                # Set title with better formatting
                ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
                
                # Improve layout
                plt.tight_layout()
                plt.subplots_adjust(top=0.9, bottom=0.15)
                
                # Create organized directory structure
                base_dir = os.path.join(os.getcwd(), 'generated_docs')
                charts_dir = os.path.join(base_dir, 'charts')
                os.makedirs(charts_dir, exist_ok=True)
                
                # Generate filename
                import time
                import uuid
                chart_filename = f"{chart_type}_chart_{int(time.time())}_{uuid.uuid4().hex[:8]}.png"
                chart_path = os.path.join(charts_dir, chart_filename)
                
                # Save with high quality
                plt.savefig(chart_path, format='png', dpi=150, bbox_inches='tight', 
                           facecolor='white', edgecolor='none', pad_inches=0.2)
                plt.close(fig)
                
                # Verify file
                if not os.path.exists(chart_path) or os.path.getsize(chart_path) == 0:
                    raise Exception("Chart file was not created properly")
                
                # Add to story with proper spacing
                story.append(Spacer(1, 20))
                story.append(Paragraph(f'<b><font size="12">{title}</font></b>', getSampleStyleSheet()['Normal']))
                story.append(Spacer(1, 10))
                
                # Add chart image with consistent sizing
                img = Image(chart_path, width=500, height=300)  # Fixed consistent size
                story.append(img)
                
                # Add caption
                caption = chart_config.get('caption', '')
                if caption:
                    story.append(Spacer(1, 8))
                    caption_style = f'<i><font size="9" color="gray">{caption}</font></i>'
                    story.append(Paragraph(caption_style, getSampleStyleSheet()['Normal']))
                
                story.append(Spacer(1, 25))
                logger.info(f"Added {chart_type} chart: {chart_path}")
                    
            except Exception as e:
                logger.error(f"Error creating {chart_type} chart: {e}")
                error_msg = f"<i>Chart '{title}' could not be generated</i>"
                story.append(Paragraph(error_msg, getSampleStyleSheet()['Normal']))
                story.append(Spacer(1, 16))
        
        return story
        
    except ImportError:
        logger.warning("Matplotlib not available")
        return story
    except Exception as e:
        logger.error(f"Error adding charts: {e}")
        return story