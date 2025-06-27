import base64
import re
from typing import Any, Dict, List, Optional
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def validate_email(email: str) -> tuple[bool, str]:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        tuple[bool, str]: (is_valid, error_message)
    """
    if not email or not email.strip():
        return False, "Email address is required. Please provide a valid email address."
    
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email.strip()):
        return False, "Invalid email format. Please provide a valid email address."
    
    return True, ""


def parse_email(msg: Dict[str, Any], include_body: bool = True) -> Dict[str, Any]:
    """Parse Gmail message into structured format"""
    headers = msg.get('payload', {}).get('headers', [])
    header_dict = {h['name']: h['value'] for h in headers}
    
    email_data = {
        'id': msg['id'],
        'thread_id': msg['threadId'],
        'subject': header_dict.get('Subject', ''),
        'from': header_dict.get('From', ''),
        'to': header_dict.get('To', ''),
        'cc': header_dict.get('Cc', ''),
        'date': header_dict.get('Date', ''),
        'snippet': msg.get('snippet', ''),
        'labels': msg.get('labelIds', [])
    }
    
    if include_body:
        email_data['body'] = extract_body(msg.get('payload', {}))
    
    return email_data

def extract_body(payload: Dict[str, Any]) -> str:
    """Extract email body from payload"""
    body = ""
    
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                data = part['body']['data']
                body = base64.urlsafe_b64decode(data).decode('utf-8')
                break
            elif part['mimeType'] == 'text/html' and not body:
                data = part['body']['data']
                body = base64.urlsafe_b64decode(data).decode('utf-8')
    else:
        if payload.get('body', {}).get('data'):
            data = payload['body']['data']
            body = base64.urlsafe_b64decode(data).decode('utf-8')
    
    return body

def create_email_message(to: str, subject: str, body: str, cc: Optional[str] = None, 
                        bcc: Optional[str] = None, html_body: Optional[str] = None) -> str:
    """Create email message in RFC 2822 format"""
    if html_body:
        message = MIMEMultipart('alternative')
        text_part = MIMEText(body, 'plain')
        html_part = MIMEText(html_body, 'html')
        message.attach(text_part)
        message.attach(html_part)
    else:
        message = MIMEText(body)
    
    message['to'] = to
    message['subject'] = subject
    if cc:
        message['cc'] = cc
    if bcc:
        message['bcc'] = bcc


def get_attachments_info(msg: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get information about email attachments"""
    attachments = []
    payload = msg.get('payload', {})
    
    if 'parts' in payload:
        for part in payload['parts']:
            if part.get('filename'):
                attachment = {
                    'filename': part['filename'],
                    'mime_type': part['mimeType'],
                    'size': part.get('body', {}).get('size', 0),
                    'attachment_id': part.get('body', {}).get('attachmentId')
                }
                attachments.append(attachment)
    
    return attachments 