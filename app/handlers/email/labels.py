#!/usr/bin/env python3
"""
Gmail Label/Folder Management Functions
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
def list_gmail_labels() -> str:
    """List all Gmail labels/folders."""
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        results = state.gmail_service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        
        # Organize labels by type
        system_labels = []
        user_labels = []
        
        for label in labels:
            label_info = {
                'id': label['id'],
                'name': label['name'],
                'type': label['type'],
                'messages_total': label.get('messagesTotal', 0),
                'messages_unread': label.get('messagesUnread', 0)
            }
            
            if label['type'] == 'system':
                system_labels.append(label_info)
            else:
                user_labels.append(label_info)
        
        result = {
            'total_labels': len(labels),
            'system_labels': system_labels,
            'user_labels': user_labels
        }
        
        logger.info(f"Retrieved {len(labels)} labels")
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"List labels error: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
def create_gmail_label(name: str, visibility: str = "labelShow", 
                      message_visibility: str = "show") -> str:
    """Create a new Gmail label.
    
    Args:
        name: Label name
        visibility: "labelShow" (visible) or "labelHide" (hidden)
        message_visibility: "show" (show messages) or "hide" (hide messages)
    """
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        label_object = {
            'name': name,
            'labelListVisibility': visibility,
            'messageListVisibility': message_visibility
        }
        
        result = state.gmail_service.users().labels().create(
            userId='me', body=label_object).execute()
        
        logger.info(f"Created label '{name}' with ID: {result['id']}")
        return f"Label '{name}' created successfully! ID: {result['id']}"
        
    except HttpError as e:
        if e.resp.status == 409:
            return f"Error: Label '{name}' already exists"
        logger.error(f"Create label error: {str(e)}")
        return f"Error: {str(e)}"
    except Exception as e:
        logger.error(f"Create label error: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
def update_gmail_label(label_id: str, name: Optional[str] = None,
                      visibility: Optional[str] = None,
                      message_visibility: Optional[str] = None) -> str:
    """Update an existing Gmail label."""
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        # Get current label info
        current_label = state.gmail_service.users().labels().get(
            userId='me', id=label_id).execute()
        
        # Build update object
        label_object = {
            'id': label_id,
            'name': name or current_label['name'],
            'labelListVisibility': visibility or current_label.get('labelListVisibility', 'labelShow'),
            'messageListVisibility': message_visibility or current_label.get('messageListVisibility', 'show')
        }
        
        result = state.gmail_service.users().labels().update(
            userId='me', id=label_id, body=label_object).execute()
        
        logger.info(f"Updated label {label_id}")
        return f"Label updated successfully! Name: {result['name']}"
        
    except Exception as e:
        logger.error(f"Update label error: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
def delete_gmail_label(label_id: str) -> str:
    """Delete a Gmail label."""
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        # Get label name before deletion
        label = state.gmail_service.users().labels().get(userId='me', id=label_id).execute()
        label_name = label['name']
        
        # Delete label
        state.gmail_service.users().labels().delete(userId='me', id=label_id).execute()
        
        logger.info(f"Deleted label '{label_name}' (ID: {label_id})")
        return f"Label '{label_name}' deleted successfully!"
        
    except Exception as e:
        logger.error(f"Delete label error: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
def add_label_to_emails(message_ids: List[str], label_ids: List[str]) -> str:
    """Add labels to multiple emails."""
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        # Batch modify messages
        modify_request = {
            'ids': message_ids,
            'addLabelIds': label_ids
        }
        
        result = state.gmail_service.users().messages().batchModify(
            userId='me', body=modify_request).execute()
        
        logger.info(f"Added labels to {len(message_ids)} messages")
        return f"Successfully added labels to {len(message_ids)} emails"
        
    except Exception as e:
        logger.error(f"Add labels error: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
def remove_label_from_emails(message_ids: List[str], label_ids: List[str]) -> str:
    """Remove labels from multiple emails."""
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        modify_request = {
            'ids': message_ids,
            'removeLabelIds': label_ids
        }
        
        result = state.gmail_service.users().messages().batchModify(
            userId='me', body=modify_request).execute()
        
        logger.info(f"Removed labels from {len(message_ids)} messages")
        return f"Successfully removed labels from {len(message_ids)} emails"
        
    except Exception as e:
        logger.error(f"Remove labels error: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
def move_emails_to_label(message_ids: List[str], target_label_id: str, 
                        remove_inbox: bool = True) -> str:
    """Move emails to a specific label (like moving to folder)."""
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        modify_request = {
            'ids': message_ids,
            'addLabelIds': [target_label_id]
        }
        
        # Remove from inbox if specified
        if remove_inbox:
            modify_request['removeLabelIds'] = ['INBOX']
        
        result = state.gmail_service.users().messages().batchModify(
            userId='me', body=modify_request).execute()
        
        action = "moved to" if remove_inbox else "copied to"
        logger.info(f"{action.title()} {len(message_ids)} messages to label {target_label_id}")
        return f"Successfully {action} {len(message_ids)} emails"
        
    except Exception as e:
        logger.error(f"Move emails error: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
def get_emails_by_label(label_id: str, max_results: int = 10) -> str:
    """Get emails from a specific label."""
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        # List messages with specific label
        results = state.gmail_service.users().messages().list(
            userId='me', labelIds=[label_id], maxResults=max_results).execute()
        
        messages = results.get('messages', [])
        emails = []
        
        for message in messages:
            msg = state.gmail_service.users().messages().get(
                userId='me', id=message['id'], format='metadata').execute()
            
            headers = {h['name']: h['value'] for h in msg['payload']['headers']}
            
            email_data = {
                'id': msg['id'],
                'thread_id': msg['threadId'],
                'subject': headers.get('Subject', ''),
                'from': headers.get('From', ''),
                'date': headers.get('Date', ''),
                'snippet': msg.get('snippet', ''),
                'labels': msg.get('labelIds', [])
            }
            emails.append(email_data)
        
        result = {
            'label_id': label_id,
            'total_messages': len(emails),
            'messages': emails
        }
        
        logger.info(f"Retrieved {len(emails)} emails from label {label_id}")
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Get emails by label error: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
def find_label_by_name(label_name: str) -> str:
    """Find label ID by name."""
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        results = state.gmail_service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        
        matching_labels = []
        for label in labels:
            if label_name.lower() in label['name'].lower():
                matching_labels.append({
                    'id': label['id'],
                    'name': label['name'],
                    'type': label['type']
                })
        
        if not matching_labels:
            return f"No labels found matching '{label_name}'"
        
        logger.info(f"Found {len(matching_labels)} matching labels")
        return json.dumps(matching_labels, indent=2)
        
    except Exception as e:
        logger.error(f"Find label error: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
def archive_emails(message_ids: List[str]) -> str:
    """Archive emails (remove from inbox)."""
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        modify_request = {
            'ids': message_ids,
            'removeLabelIds': ['INBOX']
        }
        
        result = state.gmail_service.users().messages().batchModify(
            userId='me', body=modify_request).execute()
        
        logger.info(f"Archived {len(message_ids)} messages")
        return f"Successfully archived {len(message_ids)} emails"
        
    except Exception as e:
        logger.error(f"Archive emails error: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
def mark_emails_as_read(message_ids: List[str]) -> str:
    """Mark emails as read."""
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        modify_request = {
            'ids': message_ids,
            'removeLabelIds': ['UNREAD']
        }
        
        result = state.gmail_service.users().messages().batchModify(
            userId='me', body=modify_request).execute()
        
        logger.info(f"Marked {len(message_ids)} messages as read")
        return f"Successfully marked {len(message_ids)} emails as read"
        
    except Exception as e:
        logger.error(f"Mark as read error: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
def mark_emails_as_unread(message_ids: List[str]) -> str:
    """Mark emails as unread."""
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        modify_request = {
            'ids': message_ids,
            'addLabelIds': ['UNREAD']
        }
        
        result = state.gmail_service.users().messages().batchModify(
            userId='me', body=modify_request).execute()
        
        logger.info(f"Marked {len(message_ids)} messages as unread")
        return f"Successfully marked {len(message_ids)} emails as unread"
        
    except Exception as e:
        logger.error(f"Mark as unread error: {str(e)}")
        return f"Error: {str(e)}" 