#!/usr/bin/env python3
"""
Gmail Batch Operations Functions
Add these to your main Gmail MCP server
"""

import json
import logging
from typing import List, Dict, Any, Optional

from googleapiclient.errors import HttpError

from app import mcp
import app.state as state
from app.handlers.auth import ensure_authenticated

logger = logging.getLogger('gmail-mcp')


@mcp.tool()
def batch_delete_emails(message_ids: List[str]) -> str:
    """Permanently delete multiple emails."""
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        # Gmail API allows batch delete of up to 1000 messages
        if len(message_ids) > 1000:
            return "Error: Maximum 1000 emails can be deleted at once"
        
        delete_request = {'ids': message_ids}
        
        state.gmail_service.users().messages().batchDelete(
            userId='me', body=delete_request).execute()
        
        logger.info(f"Batch deleted {len(message_ids)} messages")
        return f"Successfully deleted {len(message_ids)} emails permanently"
        
    except Exception as e:
        logger.error(f"Batch delete error: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
def batch_move_to_trash(message_ids: List[str]) -> str:
    """Move multiple emails to trash."""
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        modify_request = {
            'ids': message_ids,
            'addLabelIds': ['TRASH'],
            'removeLabelIds': ['INBOX', 'UNREAD']
        }
        
        state.gmail_service.users().messages().batchModify(
            userId='me', body=modify_request).execute()
        
        logger.info(f"Moved {len(message_ids)} messages to trash")
        return f"Successfully moved {len(message_ids)} emails to trash"
        
    except Exception as e:
        logger.error(f"Batch trash error: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
def batch_mark_as_spam(message_ids: List[str]) -> str:
    """Mark multiple emails as spam."""
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        modify_request = {
            'ids': message_ids,
            'addLabelIds': ['SPAM'],
            'removeLabelIds': ['INBOX', 'UNREAD']
        }
        
        state.gmail_service.users().messages().batchModify(
            userId='me', body=modify_request).execute()
        
        logger.info(f"Marked {len(message_ids)} messages as spam")
        return f"Successfully marked {len(message_ids)} emails as spam"
        
    except Exception as e:
        logger.error(f"Batch spam error: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
def batch_mark_important(message_ids: List[str], important: bool = True) -> str:
    """Mark multiple emails as important or not important."""
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        if important:
            modify_request = {
                'ids': message_ids,
                'addLabelIds': ['IMPORTANT']
            }
            action = "marked as important"
        else:
            modify_request = {
                'ids': message_ids,
                'removeLabelIds': ['IMPORTANT']
            }
            action = "unmarked as important"
        
        state.gmail_service.users().messages().batchModify(
            userId='me', body=modify_request).execute()
        
        logger.info(f"Batch {action}: {len(message_ids)} messages")
        return f"Successfully {action} {len(message_ids)} emails"
        
    except Exception as e:
        logger.error(f"Batch importance error: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
def batch_star_emails(message_ids: List[str], starred: bool = True) -> str:
    """Star or unstar multiple emails."""
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        if starred:
            modify_request = {
                'ids': message_ids,
                'addLabelIds': ['STARRED']
            }
            action = "starred"
        else:
            modify_request = {
                'ids': message_ids,
                'removeLabelIds': ['STARRED']
            }
            action = "unstarred"
        
        state.gmail_service.users().messages().batchModify(
            userId='me', body=modify_request).execute()
        
        logger.info(f"Batch {action}: {len(message_ids)} messages")
        return f"Successfully {action} {len(message_ids)} emails"
        
    except Exception as e:
        logger.error(f"Batch star error: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
def batch_apply_multiple_labels(message_ids: List[str], add_labels: List[str], 
                               remove_labels: Optional[List[str]] = None) -> str:
    """Apply multiple label changes to multiple emails in one operation."""
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        modify_request = {'ids': message_ids}
        
        if add_labels:
            modify_request['addLabelIds'] = add_labels
        if remove_labels:
            modify_request['removeLabelIds'] = remove_labels
        
        state.gmail_service.users().messages().batchModify(
            userId='me', body=modify_request).execute()
        
        summary = f"Applied label changes to {len(message_ids)} emails"
        if add_labels:
            summary += f" (added: {len(add_labels)} labels)"
        if remove_labels:
            summary += f" (removed: {len(remove_labels)} labels)"
        
        logger.info(summary)
        return f"Successfully {summary.lower()}"
        
    except Exception as e:
        logger.error(f"Batch label apply error: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
def batch_process_by_criteria(sender: Optional[str] = None, 
                             subject_contains: Optional[str] = None,
                             date_from: Optional[str] = None,
                             date_to: Optional[str] = None,
                             has_attachment: Optional[bool] = None,
                             is_unread: Optional[bool] = None,
                             action: str = "archive",
                             max_emails: int = 100) -> str:
    """Process emails in batch based on search criteria.
    
    Actions: archive, delete, trash, mark_read, mark_unread, star, unstar, spam
    """
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        # Build search query
        query_parts = []
        if sender: query_parts.append(f"from:{sender}")
        if subject_contains: query_parts.append(f"subject:{subject_contains}")
        if date_from: query_parts.append(f"after:{date_from}")
        if date_to: query_parts.append(f"before:{date_to}")
        if has_attachment: query_parts.append("has:attachment")
        if is_unread: query_parts.append("is:unread")
        
        query = " ".join(query_parts)
        
        # Search for messages
        results = state.gmail_service.users().messages().list(
            userId='me', q=query, maxResults=max_emails).execute()
        
        messages = results.get('messages', [])
        if not messages:
            return f"No emails found matching criteria: {query}"
        
        message_ids = [msg['id'] for msg in messages]
        
        # Apply action
        if action == "archive":
            result = batch_archive_emails(message_ids)
        elif action == "delete":
            result = batch_delete_emails(message_ids)
        elif action == "trash":
            result = batch_move_to_trash(message_ids)
        elif action == "mark_read":
            result = batch_mark_as_read(message_ids)
        elif action == "mark_unread":
            result = batch_mark_as_unread(message_ids)
        elif action == "star":
            result = batch_star_emails(message_ids, True)
        elif action == "unstar":
            result = batch_star_emails(message_ids, False)
        elif action == "spam":
            result = batch_mark_as_spam(message_ids)
        else:
            return f"Error: Unknown action '{action}'"
        
        summary = f"Found {len(messages)} emails matching criteria '{query}'. {result}"
        logger.info(summary)
        return summary
        
    except Exception as e:
        logger.error(f"Batch process by criteria error: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
def batch_archive_emails(message_ids: List[str]) -> str:
    """Archive multiple emails (remove from inbox but keep in All Mail)."""
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        modify_request = {
            'ids': message_ids,
            'removeLabelIds': ['INBOX']
        }
        
        state.gmail_service.users().messages().batchModify(
            userId='me', body=modify_request).execute()
        
        logger.info(f"Archived {len(message_ids)} messages")
        return f"Successfully archived {len(message_ids)} emails"
        
    except Exception as e:
        logger.error(f"Batch archive error: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
def batch_mark_as_read(message_ids: List[str]) -> str:
    """Mark multiple emails as read."""
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        modify_request = {
            'ids': message_ids,
            'removeLabelIds': ['UNREAD']
        }
        
        state.gmail_service.users().messages().batchModify(
            userId='me', body=modify_request).execute()
        
        logger.info(f"Marked {len(message_ids)} messages as read")
        return f"Successfully marked {len(message_ids)} emails as read"
        
    except Exception as e:
        logger.error(f"Batch mark read error: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
def batch_mark_as_unread(message_ids: List[str]) -> str:
    """Mark multiple emails as unread."""
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        modify_request = {
            'ids': message_ids,
            'addLabelIds': ['UNREAD']
        }
        
        state.gmail_service.users().messages().batchModify(
            userId='me', body=modify_request).execute()
        
        logger.info(f"Marked {len(message_ids)} messages as unread")
        return f"Successfully marked {len(message_ids)} emails as unread"
        
    except Exception as e:
        logger.error(f"Batch mark unread error: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
def batch_restore_from_trash(message_ids: List[str]) -> str:
    """Restore multiple emails from trash."""
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        modify_request = {
            'ids': message_ids,
            'addLabelIds': ['INBOX'],
            'removeLabelIds': ['TRASH']
        }
        
        state.gmail_service.users().messages().batchModify(
            userId='me', body=modify_request).execute()
        
        logger.info(f"Restored {len(message_ids)} messages from trash")
        return f"Successfully restored {len(message_ids)} emails from trash"
        
    except Exception as e:
        logger.error(f"Batch restore error: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
def batch_empty_trash() -> str:
    """Empty the entire trash folder."""
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        # Get all messages in trash
        results = state.gmail_service.users().messages().list(
            userId='me', labelIds=['TRASH'], maxResults=500).execute()
        
        messages = results.get('messages', [])
        if not messages:
            return "Trash is already empty"
        
        message_ids = [msg['id'] for msg in messages]
        
        # Permanently delete all trash messages
        delete_request = {'ids': message_ids}
        state.gmail_service.users().messages().batchDelete(
            userId='me', body=delete_request).execute()
        
        logger.info(f"Emptied trash: deleted {len(message_ids)} messages permanently")
        return f"Emptied trash: {len(message_ids)} emails deleted permanently"
        
    except Exception as e:
        logger.error(f"Empty trash error: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
def batch_operations_summary(message_ids: List[str]) -> str:
    """Get summary of what batch operations would affect."""
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        if not message_ids:
            return "No message IDs provided"
        
        # Get details for a few sample messages
        sample_size = min(5, len(message_ids))
        sample_emails = []
        
        for i in range(sample_size):
            msg = state.gmail_service.users().messages().get(
                userId='me', id=message_ids[i], format='metadata').execute()
            
            headers = {h['name']: h['value'] for h in msg['payload']['headers']}
            sample_emails.append({
                'id': msg['id'],
                'subject': headers.get('Subject', '')[:50] + '...',
                'from': headers.get('From', ''),
                'labels': msg.get('labelIds', [])
            })
        
        summary = {
            'total_emails': len(message_ids),
            'sample_emails': sample_emails,
            'message_ids': message_ids[:10] if len(message_ids) > 10 else message_ids,
            'note': f"Showing {sample_size} sample emails out of {len(message_ids)} total"
        }
        
        return json.dumps(summary, indent=2)
        
    except Exception as e:
        logger.error(f"Batch summary error: {str(e)}")
        return f"Error: {str(e)}" 