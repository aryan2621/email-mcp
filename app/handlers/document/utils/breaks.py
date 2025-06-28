from reportlab.platypus import PageBreak, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def add_page_breaks_to_story(story, breaks_config):
    """
    Issues Found in Original:
    1. No validation of breaks_config type
    2. No validation of index values
    3. Could insert breaks at invalid positions
    4. No handling of duplicate indices
    5. No error handling for edge cases
    6. Modifies original story list in place without warning
    """
    if not breaks_config:
        return story
    
    # Validate input types
    if not isinstance(story, list):
        print("Warning: story must be a list")
        return story
    
    if not isinstance(breaks_config, (list, tuple)):
        print("Warning: breaks_config must be a list or tuple of indices")
        return story
    
    if not story:  # Empty story
        return story
    
    # Validate and clean indices
    valid_indices = []
    for idx in breaks_config:
        try:
            idx = int(idx)
            # Valid range: 0 to len(story)-1 (can insert after last element)
            if 0 <= idx <= len(story):
                valid_indices.append(idx)
            else:
                print(f"Warning: Index {idx} is out of range (0-{len(story)}), skipping")
        except (ValueError, TypeError):
            print(f"Warning: Invalid index '{idx}', must be integer, skipping")
    
    # Remove duplicates and sort in reverse order
    valid_indices = sorted(set(valid_indices), reverse=True)
    
    if not valid_indices:
        return story
    
    try:
        # Insert page breaks from end to beginning to preserve indices
        for idx in valid_indices:
            # Don't add page break at the very beginning or if previous element is already PageBreak
            if idx > 0 and (idx >= len(story) or not isinstance(story[idx-1], PageBreak)):
                story.insert(idx, PageBreak())
            elif idx == 0:
                print("Warning: Skipping page break at beginning of document")
        
        return story
        
    except Exception as e:
        print(f"Error inserting page breaks: {e}")
        return story


def add_conditional_page_breaks(story, break_conditions):
    """
    Enhanced function: Add page breaks based on conditions
    
    Args:
        story: List of ReportLab elements
        break_conditions: Dict with conditions like:
            {
                'after_headings': True,  # Add breaks after heading elements
                'before_tables': True,   # Add breaks before table elements
                'max_elements_per_page': 10,  # Max elements before forced break
                'custom_positions': [5, 15, 25]  # Specific positions for breaks
            }
    """
    if not break_conditions or not isinstance(break_conditions, dict):
        return story
    
    if not isinstance(story, list) or not story:
        return story
    
    try:
        # Handle custom positions first (similar to original function)
        if 'custom_positions' in break_conditions:
            story = add_page_breaks_to_story(story, break_conditions['custom_positions'])
        
        # Add breaks after headings
        if break_conditions.get('after_headings', False):
            indices_to_break = []
            for i, element in enumerate(story):
                if hasattr(element, 'style') and hasattr(element.style, 'name'):
                    if 'Heading' in element.style.name:
                        indices_to_break.append(i + 1)
            
            if indices_to_break:
                story = add_page_breaks_to_story(story, indices_to_break)
        
        # Add breaks before tables
        if break_conditions.get('before_tables', False):
            indices_to_break = []
            for i, element in enumerate(story):
                if element.__class__.__name__ == 'Table':
                    indices_to_break.append(i)
            
            if indices_to_break:
                story = add_page_breaks_to_story(story, indices_to_break)
        
        # Add breaks based on element count per page
        max_per_page = break_conditions.get('max_elements_per_page')
        if max_per_page and isinstance(max_per_page, int) and max_per_page > 0:
            indices_to_break = []
            element_count = 0
            
            for i, element in enumerate(story):
                if isinstance(element, PageBreak):
                    element_count = 0  # Reset count after page break
                else:
                    element_count += 1
                    if element_count >= max_per_page:
                        indices_to_break.append(i + 1)
                        element_count = 0
            
            if indices_to_break:
                story = add_page_breaks_to_story(story, indices_to_break)
        
        return story
        
    except Exception as e:
        print(f"Error in conditional page breaks: {e}")
        return story


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