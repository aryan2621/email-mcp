from reportlab.platypus import PageBreak, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def add_sections_with_breaks(story, sections_config):
    """
    Add sections with page breaks between them
    
    Args:
        story: List of ReportLab elements
        sections_config: List of sections (each section is a list of ReportLab elements)
            Example: [
                [Paragraph('Section 1 content', style), Spacer(1, 12)],
                [Paragraph('Section 2 content', style), Table(data)]
            ]
    """
    if not sections_config:
        return story
    
    if not isinstance(story, list):
        print("Warning: story must be a list")
        return story
    
    if not isinstance(sections_config, (list, tuple)):
        print("Warning: sections_config must be a list or tuple of sections")
        return story
    
    styles = getSampleStyleSheet()
    
    try:
        for i, section in enumerate(sections_config):
            # Validate section structure
            if section is None:
                print(f"Warning: Section {i} is None, skipping")
                continue
            
            # Handle different section types
            if isinstance(section, str):
                # Convert string to paragraph
                story.append(Paragraph(section, styles['Normal']))
            elif isinstance(section, (list, tuple)):
                # Handle list of elements
                valid_elements = []
                for element in section:
                    if element is not None:
                        # Convert strings to paragraphs
                        if isinstance(element, str):
                            valid_elements.append(Paragraph(element, styles['Normal']))
                        else:
                            valid_elements.append(element)
                
                if valid_elements:  # Only add non-empty sections
                    story.extend(valid_elements)
                else:
                    print(f"Warning: Section {i} is empty after validation, skipping")
                    continue
            
            elif hasattr(section, '__iter__') and not isinstance(section, str):
                # Handle other iterable types (but not strings)
                try:
                    valid_elements = [elem for elem in section if elem is not None]
                    if valid_elements:
                        story.extend(valid_elements)
                    else:
                        print(f"Warning: Section {i} is empty, skipping")
                        continue
                except Exception as e:
                    print(f"Warning: Could not iterate section {i}: {e}, skipping")
                    continue
            
            else:
                # Handle single elements
                if isinstance(section, str):
                    story.append(Paragraph(section, styles['Normal']))
                else:
                    story.append(section)
            
            # Add page break between sections (but not after the last one)
            if i < len(sections_config) - 1:
                # Check if the last added element is already a PageBreak
                if story and not isinstance(story[-1], PageBreak):
                    story.append(PageBreak())
        
        return story
        
    except Exception as e:
        print(f"Error processing sections: {e}")
        return story

def add_smart_sections_with_breaks(story, sections_config, break_options=None):
    """
    Enhanced version with more control over page breaks
    
    Args:
        story: List of ReportLab elements
        sections_config: List of sections (can be strings, lists, or elements)
        break_options: Dict with options:
            {
                'break_between_all': True,  # Break between every section (default)
                'break_after_indices': [0, 2],  # Only break after specific sections
                'no_breaks': False,  # Don't add any breaks
                'min_content_for_break': 3,  # Minimum elements in section before allowing break
                'section_titles': ['Intro', 'Body', 'Conclusion']  # Optional titles
            }
    """
    if not sections_config:
        return story
    
    if not isinstance(story, list):
        return story
    
    if break_options is None:
        break_options = {'break_between_all': True}
    
    styles = getSampleStyleSheet()
    
    try:
        section_titles = break_options.get('section_titles', [])
        break_between_all = break_options.get('break_between_all', True)
        break_after_indices = set(break_options.get('break_after_indices', []))
        no_breaks = break_options.get('no_breaks', False)
        min_content_for_break = break_options.get('min_content_for_break', 1)
        
        for i, section in enumerate(sections_config):
            # Add section title if provided
            if i < len(section_titles) and section_titles[i]:
                title_style = styles.get('Heading2', styles['Normal'])
                story.append(Paragraph(str(section_titles[i]), title_style))
                story.append(Spacer(1, 12))
            
            # Process section content
            section_start_length = len(story)
            
            if isinstance(section, str):
                story.append(Paragraph(section, styles['Normal']))
            elif isinstance(section, (list, tuple)):
                valid_elements = []
                for element in section:
                    if element is not None:
                        if isinstance(element, str):
                            valid_elements.append(Paragraph(element, styles['Normal']))
                        else:
                            valid_elements.append(element)
                
                if valid_elements:
                    story.extend(valid_elements)
            else:
                if section is not None:
                    if isinstance(section, str):
                        story.append(Paragraph(section, styles['Normal']))
                    else:
                        story.append(section)
            
            # Determine if we should add a page break
            section_length = len(story) - section_start_length
            should_break = False
            
            if not no_breaks and i < len(sections_config) - 1:  # Not the last section
                if break_between_all:
                    should_break = section_length >= min_content_for_break
                elif i in break_after_indices:
                    should_break = section_length >= min_content_for_break
            
            # Add page break if needed
            if should_break and story and not isinstance(story[-1], PageBreak):
                story.append(PageBreak())
        
        return story
        
    except Exception as e:
        print(f"Error in smart sections: {e}")
        return story