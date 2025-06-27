#!/usr/bin/env python3
"""
Gmail Advanced Search & Semantic Filtering
Complete implementation with AI-powered search capabilities
"""

import json
import logging
import re
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from collections import Counter
import difflib

from app import mcp
import app.state as state
from app.handlers.auth import ensure_authenticated
from app.utils.email import parse_email, get_attachments_info, extract_body

logger = logging.getLogger('gmail-mcp')

# Semantic patterns for intelligent matching
URGENT_KEYWORDS = [
    'urgent', 'asap', 'immediately', 'deadline', 'critical', 'emergency', 
    'time-sensitive', 'rush', 'priority', 'important', 'escalate'
]

QUESTION_PATTERNS = [
    r'\?', r'\bcan you\b', r'\bcould you\b', r'\bwould you\b', r'\bwill you\b',
    r'\bhow\b', r'\bwhat\b', r'\bwhen\b', r'\bwhere\b', r'\bwhy\b', r'\bwhich\b'
]

ACTION_KEYWORDS = [
    'please', 'need', 'required', 'must', 'should', 'action', 'task', 
    'todo', 'follow up', 'complete', 'finish', 'deliver', 'submit'
]

MEETING_KEYWORDS = [
    'meeting', 'call', 'conference', 'zoom', 'teams', 'schedule', 
    'appointment', 'calendar', 'invite', 'rsvp'
]

NEWSLETTER_INDICATORS = [
    'unsubscribe', 'newsletter', 'promotional', 'marketing', 'offer',
    'deal', 'sale', 'discount', 'advertisement'
]


@mcp.tool()
def semantic_gmail_search(query: str, max_results: int = 10) -> str:
    """Search emails using natural language/semantic queries.
    
    Examples: 
    - "emails about project deadlines"
    - "urgent messages from last week" 
    - "meeting invitations I haven't responded to"
    - "emails asking questions"
    """
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        logger.info(f"Semantic search: '{query}'")
        
        # Parse natural language query into search terms
        semantic_terms = _parse_semantic_query(query)
        
        # Build Gmail query from semantic understanding
        gmail_query = _build_gmail_query_from_semantics(semantic_terms)
        
        logger.info(f"Translated to Gmail query: '{gmail_query}'")
        
        # Execute search
        results = state.gmail_service.users().messages().list(
            userId='me', q=gmail_query, maxResults=max_results * 2).execute()  # Get more for filtering
        
        messages = results.get('messages', [])
        emails = []
        
        for message in messages:
            msg = state.gmail_service.users().messages().get(
                userId='me', id=message['id'], format='full').execute()
            
            email_data = parse_email(msg, include_body=True)
            
            # Apply semantic filtering
            if _matches_semantic_criteria(email_data, semantic_terms):
                emails.append(email_data)
                
            if len(emails) >= max_results:
                break
        
        result = {
            'query': query,
            'gmail_query': gmail_query,
            'semantic_terms': semantic_terms,
            'total_found': len(emails),
            'emails': emails
        }
        
        logger.info(f"Semantic search found {len(emails)} matching emails")
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Semantic search error: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
def advanced_gmail_search(
    content_keywords: Optional[List[str]] = None,
    sentiment: Optional[str] = None,  # urgent, positive, negative, neutral
    priority_level: Optional[str] = None,  # high, medium, low
    response_required: Optional[bool] = None,
    contains_links: Optional[bool] = None,
    contains_calendar_invite: Optional[bool] = None,
    thread_length: Optional[str] = None,  # single, short, long
    attachment_types: Optional[List[str]] = None,  # pdf, image, document
    max_results: int = 10
) -> str:
    """Advanced content filtering with multiple criteria."""
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        logger.info(f"Advanced search with multiple criteria")
        
        # Start with basic query
        query_parts = []
        
        # Add content keywords
        if content_keywords:
            for keyword in content_keywords:
                query_parts.append(f'"{keyword}"')
        
        # Add attachment type filters
        if attachment_types:
            for att_type in attachment_types:
                if att_type.lower() == 'pdf':
                    query_parts.append('filename:pdf')
                elif att_type.lower() in ['image', 'img']:
                    query_parts.append('filename:(jpg OR jpeg OR png OR gif)')
                elif att_type.lower() == 'document':
                    query_parts.append('filename:(doc OR docx OR txt)')
        
        # Build Gmail query
        gmail_query = ' '.join(query_parts) if query_parts else ''
        
        # Get messages
        results = state.gmail_service.users().messages().list(
            userId='me', q=gmail_query, maxResults=max_results * 3).execute()
        
        messages = results.get('messages', [])
        filtered_emails = []
        
        for message in messages:
            msg = state.gmail_service.users().messages().get(
                userId='me', id=message['id'], format='full').execute()
            
            email_data = parse_email(msg, include_body=True)
            
            # Apply advanced filters
            if _passes_advanced_filters(
                email_data, sentiment, priority_level, response_required,
                contains_links, contains_calendar_invite, thread_length
            ):
                # Add analysis metadata
                email_data['analysis'] = _analyze_email_content(email_data)
                filtered_emails.append(email_data)
                
            if len(filtered_emails) >= max_results:
                break
        
        result = {
            'filters_applied': {
                'content_keywords': content_keywords,
                'sentiment': sentiment,
                'priority_level': priority_level,
                'response_required': response_required,
                'contains_links': contains_links,
                'contains_calendar_invite': contains_calendar_invite,
                'thread_length': thread_length,
                'attachment_types': attachment_types
            },
            'total_found': len(filtered_emails),
            'emails': filtered_emails
        }
        
        logger.info(f"Advanced search found {len(filtered_emails)} emails")
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Advanced search error: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
def smart_gmail_patterns(pattern_type: str, max_results: int = 10) -> str:
    """Find emails matching intelligent patterns.
    
    Patterns:
    - "unanswered_questions" - Emails with questions that weren't replied to
    - "follow_up_needed" - Emails that need follow-up
    - "action_items" - Emails containing tasks/action items
    - "meeting_requests" - Meeting invitations and scheduling
    - "newsletters" - Promotional/newsletter content
    - "urgent_unread" - Important unread messages
    - "long_threads" - Extended email conversations
    - "external_senders" - Emails from outside organization
    """
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        logger.info(f"Smart pattern search: '{pattern_type}'")
        
        # Define pattern-specific queries
        pattern_queries = {
            'unanswered_questions': 'is:unread',
            'follow_up_needed': 'is:unread older_than:3d',
            'action_items': '',
            'meeting_requests': 'subject:(meeting OR call OR invite OR calendar)',
            'newsletters': 'list:* OR subject:(newsletter OR unsubscribe)',
            'urgent_unread': 'is:unread is:important',
            'long_threads': '',
            'external_senders': ''
        }
        
        base_query = pattern_queries.get(pattern_type, '')
        
        # Get messages
        results = state.gmail_service.users().messages().list(
            userId='me', q=base_query, maxResults=max_results * 2).execute()
        
        messages = results.get('messages', [])
        pattern_emails = []
        
        for message in messages:
            msg = state.gmail_service.users().messages().get(
                userId='me', id=message['id'], format='full').execute()
            
            email_data = parse_email(msg, include_body=True)
            
            # Apply pattern-specific filtering
            if _matches_pattern(email_data, pattern_type):
                # Add pattern analysis
                email_data['pattern_analysis'] = _analyze_pattern_match(email_data, pattern_type)
                pattern_emails.append(email_data)
                
            if len(pattern_emails) >= max_results:
                break
        
        result = {
            'pattern_type': pattern_type,
            'total_found': len(pattern_emails),
            'emails': pattern_emails
        }
        
        logger.info(f"Pattern '{pattern_type}' found {len(pattern_emails)} emails")
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Smart pattern search error: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
def fuzzy_gmail_search(reference_email_id: str, similarity_threshold: float = 0.3, 
                      max_results: int = 10) -> str:
    """Find emails similar to a reference email based on content/context."""
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        logger.info(f"Fuzzy search for emails similar to: {reference_email_id}")
        
        # Get reference email
        ref_msg = state.gmail_service.users().messages().get(
            userId='me', id=reference_email_id, format='full').execute()
        ref_email = parse_email(ref_msg, include_body=True)
        
        # Extract key features from reference email
        ref_features = _extract_email_features(ref_email)
        
        # Get candidate emails (recent emails)
        results = state.gmail_service.users().messages().list(
            userId='me', maxResults=100).execute()
        
        messages = results.get('messages', [])
        similar_emails = []
        
        for message in messages:
            if message['id'] == reference_email_id:
                continue
                
            msg = state.gmail_service.users().messages().get(
                userId='me', id=message['id'], format='full').execute()
            
            email_data = parse_email(msg, include_body=True)
            email_features = _extract_email_features(email_data)
            
            # Calculate similarity
            similarity = _calculate_similarity(ref_features, email_features)
            
            if similarity >= similarity_threshold:
                email_data['similarity_score'] = similarity
                email_data['similarity_reasons'] = _explain_similarity(ref_features, email_features)
                similar_emails.append(email_data)
        
        # Sort by similarity
        similar_emails.sort(key=lambda x: x['similarity_score'], reverse=True)
        similar_emails = similar_emails[:max_results]
        
        result = {
            'reference_email_id': reference_email_id,
            'reference_subject': ref_email['subject'],
            'similarity_threshold': similarity_threshold,
            'total_found': len(similar_emails),
            'emails': similar_emails
        }
        
        logger.info(f"Found {len(similar_emails)} similar emails")
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Fuzzy search error: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
def temporal_gmail_search(
    time_pattern: str,  # "daily_digest", "weekly_summary", "overdue_responses", "recent_important"
    reference_date: Optional[str] = None,
    max_results: int = 10
) -> str:
    """Search based on temporal patterns and time-sensitive content."""
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        logger.info(f"Temporal search: '{time_pattern}'")
        
        # Calculate date ranges
        today = datetime.now()
        if reference_date:
            ref_date = datetime.strptime(reference_date, '%Y-%m-%d')
        else:
            ref_date = today
        
        # Define temporal queries
        if time_pattern == "daily_digest":
            start_date = ref_date.strftime('%Y/%m/%d')
            query = f'after:{start_date} before:{(ref_date + timedelta(days=1)).strftime("%Y/%m/%d")}'
        elif time_pattern == "weekly_summary":
            start_date = (ref_date - timedelta(days=7)).strftime('%Y/%m/%d')
            query = f'after:{start_date}'
        elif time_pattern == "overdue_responses":
            cutoff_date = (ref_date - timedelta(days=3)).strftime('%Y/%m/%d')
            query = f'is:unread before:{cutoff_date}'
        elif time_pattern == "recent_important":
            start_date = (ref_date - timedelta(days=2)).strftime('%Y/%m/%d')
            query = f'is:important after:{start_date}'
        else:
            return f"Error: Unknown time pattern '{time_pattern}'"
        
        # Execute search
        results = state.gmail_service.users().messages().list(
            userId='me', q=query, maxResults=max_results).execute()
        
        messages = results.get('messages', [])
        temporal_emails = []
        
        for message in messages:
            msg = state.gmail_service.users().messages().get(
                userId='me', id=message['id'], format='full').execute()
            
            email_data = parse_email(msg, include_body=True)
            
            # Add temporal analysis
            email_data['temporal_analysis'] = _analyze_temporal_relevance(email_data, time_pattern, ref_date)
            temporal_emails.append(email_data)
        
        result = {
            'time_pattern': time_pattern,
            'reference_date': reference_date or today.strftime('%Y-%m-%d'),
            'gmail_query': query,
            'total_found': len(temporal_emails),
            'emails': temporal_emails
        }
        
        logger.info(f"Temporal search '{time_pattern}' found {len(temporal_emails)} emails")
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Temporal search error: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
def content_analysis_search(analysis_type: str, max_results: int = 10) -> str:
    """Search emails based on content analysis.
    
    Analysis types:
    - "sentiment_negative" - Emails with negative sentiment
    - "sentiment_positive" - Emails with positive sentiment  
    - "high_complexity" - Emails with complex/technical content
    - "contains_numbers" - Emails with financial/numerical data
    - "contains_urls" - Emails with many links
    - "short_messages" - Brief emails (likely quick responses)
    - "long_messages" - Detailed emails (likely important)
    """
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        logger.info(f"Content analysis search: '{analysis_type}'")
        
        # Get recent emails for analysis
        results = state.gmail_service.users().messages().list(
            userId='me', maxResults=50).execute()
        
        messages = results.get('messages', [])
        analyzed_emails = []
        
        for message in messages:
            msg = state.gmail_service.users().messages().get(
                userId='me', id=message['id'], format='full').execute()
            
            email_data = parse_email(msg, include_body=True)
            
            # Perform content analysis
            content_analysis = _perform_content_analysis(email_data)
            
            # Check if matches analysis type
            if _matches_analysis_criteria(content_analysis, analysis_type):
                email_data['content_analysis'] = content_analysis
                analyzed_emails.append(email_data)
                
            if len(analyzed_emails) >= max_results:
                break
        
        result = {
            'analysis_type': analysis_type,
            'total_found': len(analyzed_emails),
            'emails': analyzed_emails
        }
        
        logger.info(f"Content analysis '{analysis_type}' found {len(analyzed_emails)} emails")
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Content analysis search error: {str(e)}")
        return f"Error: {str(e)}"


# Helper functions for semantic analysis

def _parse_semantic_query(query: str) -> Dict[str, Any]:
    """Parse natural language query into semantic terms."""
    query_lower = query.lower()
    
    terms = {
        'keywords': [],
        'time_period': None,
        'sender_type': None,
        'urgency': None,
        'content_type': None,
        'action_required': False
    }
    
    # Extract keywords
    words = re.findall(r'\b\w+\b', query_lower)
    terms['keywords'] = [w for w in words if len(w) > 3]
    
    # Detect time periods
    if any(word in query_lower for word in ['today', 'yesterday']):
        terms['time_period'] = 'recent'
    elif any(word in query_lower for word in ['week', 'last week']):
        terms['time_period'] = 'week'
    elif any(word in query_lower for word in ['month', 'last month']):
        terms['time_period'] = 'month'
    
    # Detect urgency
    if any(word in query_lower for word in URGENT_KEYWORDS):
        terms['urgency'] = 'high'
    
    # Detect content types
    if any(word in query_lower for word in ['meeting', 'call', 'invite']):
        terms['content_type'] = 'meeting'
    elif any(word in query_lower for word in ['question', 'ask', '?']):
        terms['content_type'] = 'question'
    
    # Detect action required
    if any(word in query_lower for word in ['respond', 'reply', 'answer']):
        terms['action_required'] = True
    
    return terms


def _build_gmail_query_from_semantics(terms: Dict[str, Any]) -> str:
    """Build Gmail query from semantic terms."""
    query_parts = []
    
    # Add keywords
    for keyword in terms['keywords'][:3]:  # Limit to avoid complex queries
        query_parts.append(keyword)
    
    # Add time filters
    if terms['time_period'] == 'recent':
        query_parts.append('newer_than:1d')
    elif terms['time_period'] == 'week':
        query_parts.append('newer_than:7d')
    elif terms['time_period'] == 'month':
        query_parts.append('newer_than:30d')
    
    # Add urgency filters
    if terms['urgency'] == 'high':
        query_parts.append('is:important')
    
    # Add content type filters
    if terms['content_type'] == 'meeting':
        query_parts.append('(meeting OR call OR invite)')
    
    # Add action filters
    if terms['action_required']:
        query_parts.append('is:unread')
    
    return ' '.join(query_parts)


def _matches_semantic_criteria(email_data: Dict[str, Any], terms: Dict[str, Any]) -> bool:
    """Check if email matches semantic criteria."""
    content = (email_data.get('body', '') + ' ' + email_data.get('subject', '')).lower()
    
    # Check keywords
    if terms['keywords']:
        keyword_matches = sum(1 for keyword in terms['keywords'] if keyword in content)
        if keyword_matches < len(terms['keywords']) * 0.5:  # At least 50% match
            return False
    
    # Check content type
    if terms['content_type'] == 'question':
        if not any(re.search(pattern, content) for pattern in QUESTION_PATTERNS):
            return False
    
    return True


def _passes_advanced_filters(
    email_data: Dict[str, Any], sentiment: Optional[str], priority_level: Optional[str],
    response_required: Optional[bool], contains_links: Optional[bool],
    contains_calendar_invite: Optional[bool], thread_length: Optional[str]
) -> bool:
    """Check if email passes advanced filters."""
    
    content = email_data.get('body', '') + ' ' + email_data.get('subject', '')
    
    # Sentiment filter
    if sentiment:
        detected_sentiment = _detect_sentiment(content)
        if detected_sentiment != sentiment:
            return False
    
    # Priority filter
    if priority_level:
        detected_priority = _detect_priority(email_data)
        if detected_priority != priority_level:
            return False
    
    # Response required filter
    if response_required is not None:
        has_questions = any(re.search(pattern, content.lower()) for pattern in QUESTION_PATTERNS)
        if response_required != has_questions:
            return False
    
    # Links filter
    if contains_links is not None:
        has_links = 'http' in content.lower()
        if contains_links != has_links:
            return False
    
    # Calendar invite filter
    if contains_calendar_invite is not None:
        has_invite = any(word in content.lower() for word in MEETING_KEYWORDS)
        if contains_calendar_invite != has_invite:
            return False
    
    return True


def _analyze_email_content(email_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze email content and return metadata."""
    content = email_data.get('body', '') + ' ' + email_data.get('subject', '')
    
    return {
        'word_count': len(content.split()),
        'has_questions': any(re.search(pattern, content.lower()) for pattern in QUESTION_PATTERNS),
        'has_action_items': any(word in content.lower() for word in ACTION_KEYWORDS),
        'urgency_level': _detect_urgency(content),
        'sentiment': _detect_sentiment(content),
        'contains_numbers': bool(re.search(r'\d+', content)),
        'contains_links': 'http' in content.lower(),
        'estimated_read_time': len(content.split()) // 200 + 1  # minutes
    }


def _matches_pattern(email_data: Dict[str, Any], pattern_type: str) -> bool:
    """Check if email matches specific pattern."""
    content = (email_data.get('body', '') + ' ' + email_data.get('subject', '')).lower()
    
    if pattern_type == 'unanswered_questions':
        return any(re.search(pattern, content) for pattern in QUESTION_PATTERNS)
    
    elif pattern_type == 'follow_up_needed':
        return any(word in content for word in ['follow up', 'follow-up', 'pending', 'waiting'])
    
    elif pattern_type == 'action_items':
        return any(word in content for word in ACTION_KEYWORDS)
    
    elif pattern_type == 'meeting_requests':
        return any(word in content for word in MEETING_KEYWORDS)
    
    elif pattern_type == 'newsletters':
        return any(word in content for word in NEWSLETTER_INDICATORS)
    
    elif pattern_type == 'urgent_unread':
        return any(word in content for word in URGENT_KEYWORDS)
    
    elif pattern_type == 'long_threads':
        return email_data.get('thread_id') and len(content) > 1000
    
    elif pattern_type == 'external_senders':
        sender = email_data.get('from', '')
        # Simple heuristic for external vs internal
        return '@gmail.com' in sender or '@yahoo.com' in sender or '@hotmail.com' in sender
    
    return False


def _analyze_pattern_match(email_data: Dict[str, Any], pattern_type: str) -> Dict[str, Any]:
    """Analyze why email matches the pattern."""
    return {
        'pattern': pattern_type,
        'confidence': 0.8,  # Could be improved with ML
        'matching_elements': _get_matching_elements(email_data, pattern_type)
    }


def _get_matching_elements(email_data: Dict[str, Any], pattern_type: str) -> List[str]:
    """Get specific elements that caused pattern match."""
    content = (email_data.get('body', '') + ' ' + email_data.get('subject', '')).lower()
    elements = []
    
    if pattern_type == 'unanswered_questions':
        for pattern in QUESTION_PATTERNS:
            if re.search(pattern, content):
                elements.append(f"Contains question pattern: {pattern}")
    
    # Add more specific matching logic for other patterns
    
    return elements


def _extract_email_features(email_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract features for similarity comparison."""
    content = email_data.get('body', '') + ' ' + email_data.get('subject', '')
    words = re.findall(r'\b\w+\b', content.lower())
    
    return {
        'word_frequency': Counter(words),
        'length': len(content),
        'sender_domain': email_data.get('from', '').split('@')[-1] if '@' in email_data.get('from', '') else '',
        'subject_words': set(email_data.get('subject', '').lower().split()),
        'has_attachments': len(email_data.get('attachments', [])) > 0
    }


def _calculate_similarity(features1: Dict[str, Any], features2: Dict[str, Any]) -> float:
    """Calculate similarity between two emails."""
    # Word frequency similarity
    words1 = set(features1['word_frequency'].keys())
    words2 = set(features2['word_frequency'].keys())
    word_similarity = len(words1 & words2) / len(words1 | words2) if words1 | words2 else 0
    
    # Subject similarity
    subject_similarity = len(features1['subject_words'] & features2['subject_words']) / \
                        len(features1['subject_words'] | features2['subject_words']) \
                        if features1['subject_words'] | features2['subject_words'] else 0
    
    # Sender domain similarity
    domain_similarity = 1.0 if features1['sender_domain'] == features2['sender_domain'] else 0.0
    
    # Combine similarities
    return (word_similarity * 0.5 + subject_similarity * 0.3 + domain_similarity * 0.2)


def _explain_similarity(features1: Dict[str, Any], features2: Dict[str, Any]) -> List[str]:
    """Explain why emails are similar."""
    reasons = []
    
    common_words = set(features1['word_frequency'].keys()) & set(features2['word_frequency'].keys())
    if common_words:
        reasons.append(f"Common words: {', '.join(list(common_words)[:5])}")
    
    if features1['sender_domain'] == features2['sender_domain']:
        reasons.append(f"Same sender domain: {features1['sender_domain']}")
    
    return reasons


def _analyze_temporal_relevance(email_data: Dict[str, Any], pattern: str, ref_date: datetime) -> Dict[str, Any]:
    """Analyze temporal relevance of email."""
    return {
        'pattern': pattern,
        'relevance_score': 0.8,  # Placeholder
        'time_factors': ['Recent', 'Unread'] if 'UNREAD' in email_data.get('labels', []) else ['Recent']
    }


def _perform_content_analysis(email_data: Dict[str, Any]) -> Dict[str, Any]:
    """Perform comprehensive content analysis."""
    content = email_data.get('body', '') + ' ' + email_data.get('subject', '')
    
    return {
        'sentiment': _detect_sentiment(content),
        'complexity': _calculate_complexity(content),
        'word_count': len(content.split()),
        'contains_numbers': bool(re.search(r'\d+', content)),
        'url_count': len(re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)),
        'question_count': len(re.findall(r'\?', content))
    }


def _matches_analysis_criteria(analysis: Dict[str, Any], analysis_type: str) -> bool:
    """Check if content analysis matches criteria."""
    if analysis_type == 'sentiment_negative':
        return analysis['sentiment'] == 'negative'
    elif analysis_type == 'sentiment_positive':
        return analysis['sentiment'] == 'positive'
    elif analysis_type == 'high_complexity':
        return analysis['complexity'] > 0.7
    elif analysis_type == 'contains_numbers':
        return analysis['contains_numbers']
    elif analysis_type == 'contains_urls':
        return analysis['url_count'] > 0
    elif analysis_type == 'short_messages':
        return analysis['word_count'] < 50
    elif analysis_type == 'long_messages':
        return analysis['word_count'] > 200
    
    return False


def _detect_sentiment(content: str) -> str:
    """Simple sentiment detection."""
    positive_words = ['great', 'excellent', 'good', 'thanks', 'wonderful', 'amazing']
    negative_words = ['bad', 'terrible', 'problem', 'issue', 'error', 'wrong', 'urgent']
    
    content_lower = content.lower()
    pos_count = sum(1 for word in positive_words if word in content_lower)
    neg_count = sum(1 for word in negative_words if word in content_lower)
    
    if pos_count > neg_count:
        return 'positive'
    elif neg_count > pos_count:
        return 'negative'
    else:
        return 'neutral'


def _detect_priority(email_data: Dict[str, Any]) -> str:
    """Detect email priority level."""
    content = (email_data.get('body', '') + ' ' + email_data.get('subject', '')).lower()
    
    # Check for high priority indicators
    if any(word in content for word in URGENT_KEYWORDS):
        return 'high'
    elif 'IMPORTANT' in email_data.get('labels', []):
        return 'high'
    elif any(word in content for word in ['please', 'need', 'request']):
        return 'medium'
    else:
        return 'low'


def _detect_urgency(content: str) -> str:
    """Detect urgency level in content."""
    content_lower = content.lower()
    urgent_count = sum(1 for word in URGENT_KEYWORDS if word in content_lower)
    
    if urgent_count >= 2:
        return 'high'
    elif urgent_count == 1:
        return 'medium'
    else:
        return 'low'


def _calculate_complexity(content: str) -> float:
    """Calculate content complexity score (0-1)."""
    words = content.split()
    if not words:
        return 0.0
    
    # Factors that increase complexity
    avg_word_length = sum(len(word) for word in words) / len(words)
    sentence_count = len(re.split(r'[.!?]+', content))
    avg_sentence_length = len(words) / sentence_count if sentence_count > 0 else 0
    
    # Technical terms increase complexity
    technical_words = ['implementation', 'configuration', 'analysis', 'architecture', 'specification']
    tech_count = sum(1 for word in technical_words if word.lower() in content.lower())
    
    # Normalize to 0-1 scale
    complexity = min(1.0, (avg_word_length / 10 + avg_sentence_length / 20 + tech_count / 10))
    return complexity


@mcp.tool()
def email_insights_dashboard(max_emails: int = 50) -> str:
    """Generate insights dashboard for recent emails."""
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        logger.info(f"Generating email insights dashboard")
        
        # Get recent emails
        results = state.gmail_service.users().messages().list(
            userId='me', maxResults=max_emails).execute()
        
        messages = results.get('messages', [])
        
        # Analyze all emails
        insights = {
            'total_analyzed': 0,
            'sentiment_distribution': {'positive': 0, 'negative': 0, 'neutral': 0},
            'priority_distribution': {'high': 0, 'medium': 0, 'low': 0},
            'content_types': {'questions': 0, 'action_items': 0, 'meetings': 0, 'newsletters': 0},
            'sender_domains': {},
            'urgency_trends': {'high': 0, 'medium': 0, 'low': 0},
            'avg_response_time_needed': 0,
            'unread_by_category': {},
            'top_keywords': {},
            'email_length_distribution': {'short': 0, 'medium': 0, 'long': 0}
        }
        
        all_keywords = []
        response_times = []
        
        for message in messages:
            try:
                msg = state.gmail_service.users().messages().get(
                    userId='me', id=message['id'], format='full').execute()
                
                email_data = parse_email(msg, include_body=True)
                content = email_data.get('body', '') + ' ' + email_data.get('subject', '')
                
                insights['total_analyzed'] += 1
                
                # Sentiment analysis
                sentiment = _detect_sentiment(content)
                insights['sentiment_distribution'][sentiment] += 1
                
                # Priority analysis
                priority = _detect_priority(email_data)
                insights['priority_distribution'][priority] += 1
                
                # Content type analysis
                if any(re.search(pattern, content.lower()) for pattern in QUESTION_PATTERNS):
                    insights['content_types']['questions'] += 1
                if any(word in content.lower() for word in ACTION_KEYWORDS):
                    insights['content_types']['action_items'] += 1
                if any(word in content.lower() for word in MEETING_KEYWORDS):
                    insights['content_types']['meetings'] += 1
                if any(word in content.lower() for word in NEWSLETTER_INDICATORS):
                    insights['content_types']['newsletters'] += 1
                
                # Sender domain analysis
                sender = email_data.get('from', '')
                if '@' in sender:
                    domain = sender.split('@')[-1]
                    insights['sender_domains'][domain] = insights['sender_domains'].get(domain, 0) + 1
                
                # Urgency analysis
                urgency = _detect_urgency(content)
                insights['urgency_trends'][urgency] += 1
                
                # Length analysis
                word_count = len(content.split())
                if word_count < 50:
                    insights['email_length_distribution']['short'] += 1
                elif word_count < 200:
                    insights['email_length_distribution']['medium'] += 1
                else:
                    insights['email_length_distribution']['long'] += 1
                
                # Keyword extraction
                words = re.findall(r'\b[a-zA-Z]{4,}\b', content.lower())
                all_keywords.extend(words)
                
                # Estimate response time needed
                if priority == 'high':
                    response_times.append(2)  # hours
                elif priority == 'medium':
                    response_times.append(24)  # hours
                else:
                    response_times.append(72)  # hours
                    
            except Exception as e:
                logger.warning(f"Error analyzing email {message['id']}: {str(e)}")
                continue
        
        # Calculate averages and top items
        if response_times:
            insights['avg_response_time_needed'] = sum(response_times) / len(response_times)
        
        # Top keywords (excluding common words)
        common_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy', 'did', 'she', 'use', 'way', 'way', 'will', 'with', 'have', 'this', 'that', 'from', 'they', 'know', 'want', 'been', 'good', 'much', 'some', 'time', 'very', 'when', 'come', 'here', 'just', 'like', 'long', 'make', 'many', 'over', 'such', 'take', 'than', 'them', 'well', 'were'}
        
        keyword_counts = Counter([word for word in all_keywords if word not in common_words])
        insights['top_keywords'] = dict(keyword_counts.most_common(10))
        
        # Top sender domains
        insights['sender_domains'] = dict(sorted(insights['sender_domains'].items(), key=lambda x: x[1], reverse=True)[:10])
        
        logger.info(f"Generated insights for {insights['total_analyzed']} emails")
        return json.dumps(insights, indent=2)
        
    except Exception as e:
        logger.error(f"Insights dashboard error: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
def smart_email_categorization(max_emails: int = 30) -> str:
    """Automatically categorize recent emails into smart groups."""
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        logger.info(f"Smart categorization of {max_emails} emails")
        
        # Get recent emails
        results = state.gmail_service.users().messages().list(
            userId='me', maxResults=max_emails).execute()
        
        messages = results.get('messages', [])
        
        categories = {
            'urgent_action_required': [],
            'meetings_and_events': [],
            'newsletters_and_promotions': [],
            'personal_communications': [],
            'work_projects': [],
            'automated_notifications': [],
            'questions_requiring_response': [],
            'fyi_updates': []
        }
        
        for message in messages:
            try:
                msg = state.gmail_service.users().messages().get(
                    userId='me', id=message['id'], format='full').execute()
                
                email_data = parse_email(msg, include_body=True)
                content = (email_data.get('body', '') + ' ' + email_data.get('subject', '')).lower()
                
                # Categorize based on content analysis
                category = _smart_categorize_email(email_data, content)
                
                if category in categories:
                    email_summary = {
                        'id': email_data['id'],
                        'subject': email_data['subject'][:80] + '...' if len(email_data['subject']) > 80 else email_data['subject'],
                        'from': email_data['from'],
                        'snippet': email_data['snippet'][:100] + '...' if len(email_data['snippet']) > 100 else email_data['snippet'],
                        'confidence': _calculate_categorization_confidence(email_data, content, category)
                    }
                    categories[category].append(email_summary)
                    
            except Exception as e:
                logger.warning(f"Error categorizing email {message['id']}: {str(e)}")
                continue
        
        # Add summary statistics
        result = {
            'total_emails_categorized': sum(len(emails) for emails in categories.values()),
            'category_counts': {cat: len(emails) for cat, emails in categories.items()},
            'categories': categories
        }
        
        logger.info(f"Categorized {result['total_emails_categorized']} emails into {len(categories)} categories")
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Smart categorization error: {str(e)}")
        return f"Error: {str(e)}"


def _smart_categorize_email(email_data: Dict[str, Any], content: str) -> str:
    """Intelligently categorize an email."""
    
    # Check for urgent action required
    if (any(word in content for word in URGENT_KEYWORDS) and 
        any(word in content for word in ACTION_KEYWORDS)):
        return 'urgent_action_required'
    
    # Check for meetings and events
    if any(word in content for word in MEETING_KEYWORDS):
        return 'meetings_and_events'
    
    # Check for newsletters and promotions
    if any(word in content for word in NEWSLETTER_INDICATORS):
        return 'newsletters_and_promotions'
    
    # Check for questions requiring response
    if any(re.search(pattern, content) for pattern in QUESTION_PATTERNS):
        return 'questions_requiring_response'
    
    # Check for automated notifications
    if any(word in content for word in ['notification', 'automated', 'no-reply', 'noreply', 'alert']):
        return 'automated_notifications'
    
    # Check sender domain for personal vs work
    sender = email_data.get('from', '')
    if any(domain in sender for domain in ['@gmail.com', '@yahoo.com', '@hotmail.com', '@outlook.com']):
        return 'personal_communications'
    
    # Check for work projects (contains project-related keywords)
    work_keywords = ['project', 'deadline', 'milestone', 'deliverable', 'sprint', 'review']
    if any(word in content for word in work_keywords):
        return 'work_projects'
    
    # Default to FYI updates
    return 'fyi_updates'


def _calculate_categorization_confidence(email_data: Dict[str, Any], content: str, category: str) -> float:
    """Calculate confidence score for categorization."""
    # Simple confidence calculation based on keyword matches
    # In a real implementation, this could use ML models
    
    confidence_scores = {
        'urgent_action_required': 0.9 if any(word in content for word in URGENT_KEYWORDS) else 0.6,
        'meetings_and_events': 0.95 if 'calendar' in content else 0.8,
        'newsletters_and_promotions': 0.9 if 'unsubscribe' in content else 0.7,
        'questions_requiring_response': 0.9 if '?' in content else 0.6,
        'automated_notifications': 0.95 if 'no-reply' in content else 0.7,
        'personal_communications': 0.8,
        'work_projects': 0.8,
        'fyi_updates': 0.6
    }
    
    return confidence_scores.get(category, 0.5)


@mcp.tool()
def bulk_semantic_search(queries: List[str], max_results_per_query: int = 5) -> str:
    """Run multiple semantic searches at once."""
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        logger.info(f"Running bulk semantic search for {len(queries)} queries")
        
        results = {}
        
        for query in queries:
            try:
                # Run semantic search for each query
                search_result = semantic_gmail_search(query, max_results_per_query)
                parsed_result = json.loads(search_result)
                
                results[query] = {
                    'total_found': parsed_result.get('total_found', 0),
                    'emails': parsed_result.get('emails', [])
                }
                
            except Exception as e:
                logger.warning(f"Error in bulk search for query '{query}': {str(e)}")
                results[query] = {'error': str(e)}
        
        summary = {
            'total_queries': len(queries),
            'successful_queries': len([r for r in results.values() if 'error' not in r]),
            'total_emails_found': sum(r.get('total_found', 0) for r in results.values() if 'error' not in r),
            'results': results
        }
        
        logger.info(f"Bulk search completed: {summary['successful_queries']}/{summary['total_queries']} successful")
        return json.dumps(summary, indent=2)
        
    except Exception as e:
        logger.error(f"Bulk semantic search error: {str(e)}")
        return f"Error: {str(e)}"