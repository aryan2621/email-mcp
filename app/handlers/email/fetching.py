import json
import logging
from typing import Optional

from app import mcp
import app.state as state
from app.handlers.auth import ensure_authenticated
from app.utils.email import parse_email, get_attachments_info

logger = logging.getLogger('gmail-mcp')


@mcp.tool()
def fetch_gmail_emails(query: str = "", max_results: int = 10, include_body: bool = True) -> str:
    """Fetch emails from Gmail with optional filtering."""
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        logger.info(f"Fetching emails: '{query}', max: {max_results}")
        
        results = state.gmail_service.users().messages().list(
            userId='me', q=query, maxResults=max_results).execute()
        
        messages = results.get('messages', [])
        emails = []
        
        for message in messages:
            msg = state.gmail_service.users().messages().get(
                userId='me', id=message['id'],
                format='full' if include_body else 'metadata').execute()
            emails.append(parse_email(msg, include_body))
        
        logger.info(f"Fetched {len(emails)} emails")
        return json.dumps(emails, indent=2)
        
    except Exception as e:
        logger.error(f"Fetch error: {str(e)}")
        return f"Error: {str(e)}"

@mcp.tool()
def search_gmail_emails(sender: Optional[str] = None, subject: Optional[str] = None,
                       date_from: Optional[str] = None, date_to: Optional[str] = None,
                       has_attachment: Optional[bool] = None, max_results: int = 10) -> str:
    """Search emails with specific criteria."""
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        query_parts = []
        if sender: query_parts.append(f"from:{sender}")
        if subject: query_parts.append(f"subject:{subject}")
        if date_from: query_parts.append(f"after:{date_from}")
        if date_to: query_parts.append(f"before:{date_to}")
        if has_attachment: query_parts.append("has:attachment")
        
        query = " ".join(query_parts)
        logger.info(f"Search query: {query}")
        
        results = state.gmail_service.users().messages().list(
            userId='me', q=query, maxResults=max_results).execute()
        
        messages = results.get('messages', [])
        emails = []
        
        for message in messages:
            msg = state.gmail_service.users().messages().get(
                userId='me', id=message['id'], format='full').execute()
            emails.append(parse_email(msg, include_body=True))
        
        logger.info(f"Search returned {len(emails)} emails")
        return json.dumps(emails, indent=2)
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return f"Error: {str(e)}"

@mcp.tool()
def get_gmail_email_details(message_id: str, include_attachments: bool = False) -> str:
    """Get detailed information about a specific email."""
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        logger.info(f"Getting details: {message_id}")
        
        msg = state.gmail_service.users().messages().get(
            userId='me', id=message_id, format='full').execute()
        
        email_data = parse_email(msg, include_body=True)
        
        if include_attachments:
            email_data['attachments'] = get_attachments_info(msg)
        
        logger.info(f"Retrieved details for: {message_id}")
        return json.dumps(email_data, indent=2)
        
    except Exception as e:
        logger.error(f"Details error: {str(e)}")
        return f"Error: {str(e)}"

@mcp.tool()
def get_gmail_inbox(max_results: int = 10) -> str:
    """
    Get emails from Gmail inbox.
    
    Parameters:
        max_results (int): Maximum number of emails to fetch (1-100, default: 10).
    
    Returns:
        str: JSON string with inbox emails or error message.
    """
    if not ensure_authenticated():
        return "Error: Authentication required. Please run authenticate_gmail tool first."
    
    logger.info(f"Getting inbox emails, max_results: {max_results}")
    return fetch_gmail_emails("in:inbox", max_results, True)

@mcp.tool()
def get_gmail_sent(max_results: int = 10) -> str:
    """
    Get emails from Gmail sent folder.
    
    Parameters:
        max_results (int): Maximum number of emails to fetch (1-100, default: 10).
    
    Returns:
        str: JSON string with sent emails or error message.
    """
    if not ensure_authenticated():
        return "Error: Authentication required. Please run authenticate_gmail tool first."
    
    logger.info(f"Getting sent emails, max_results: {max_results}")
    return fetch_gmail_emails("in:sent", max_results, True)

@mcp.tool()
def get_gmail_unread(max_results: int = 10) -> str:
    """
    Get unread emails from Gmail.
    
    Parameters:
        max_results (int): Maximum number of emails to fetch (1-100, default: 10).
    
    Returns:
        str: JSON string with unread emails or error message.
    """
    if not ensure_authenticated():
        return "Error: Authentication required. Please run authenticate_gmail tool first."
    
    logger.info(f"Getting unread emails, max_results: {max_results}")
    return fetch_gmail_emails("is:unread", max_results, True) 