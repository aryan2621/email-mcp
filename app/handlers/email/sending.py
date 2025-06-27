import base64
import json
import logging
from typing import Optional, List
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
import mimetypes
from email import encoders
import os
import re
from googleapiclient.errors import HttpError

from app import mcp
import app.state as state
from app.handlers.auth import ensure_authenticated
from app.utils.email import extract_body

logger = logging.getLogger('gmail-mcp')


def text_to_html(text: Optional[str]) -> str:
    """Convert plain text to HTML with proper paragraph formatting."""
    if not text:
        return '<p></p>'
    
    # Split on double line breaks for paragraphs
    paragraphs = re.split(r'\n\s*\n', text.strip())
    
    html_parts = []
    for paragraph in paragraphs:
        if paragraph.strip():
            # Clean each paragraph
            clean_para = re.sub(r'\s+', ' ', paragraph.strip())
            html_parts.append(f'<p>{clean_para}</p>')
    
    return '\n'.join(html_parts) if html_parts else '<p></p>'


def html_to_plain_text(html: str) -> str:
    """Convert HTML back to plain text for fallback."""
    if not html:
        return ''
    
    # Simple HTML to text conversion
    text = re.sub(r'<p[^>]*>', '', html)
    text = re.sub(r'</p>', '\n\n', text)
    text = re.sub(r'<br[^>]*>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)  # Remove all other HTML tags
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  # Clean up extra newlines
    
    return text.strip()


@mcp.tool()
def send_gmail_email(to: str, subject: str, body: str, cc: Optional[str] = None, 
                    bcc: Optional[str] = None) -> str:
    """Send email via Gmail using HTML formatting by default.
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email content (will be converted to HTML automatically)
        cc: CC recipients (optional)
        bcc: BCC recipients (optional)
    """
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        # Convert text to HTML
        html_body = text_to_html(body)
        plain_body = html_to_plain_text(html_body)
        
        profile = state.gmail_service.users().getProfile(userId='me').execute()
        from_email = profile.get('emailAddress')
        
        logger.info(f"Sending email from {from_email} to {to}")
        
        # Create EmailMessage
        message = EmailMessage()
        
        # Set content (HTML primary, plain text fallback)
        message.set_content(plain_body)  # Plain text fallback
        message.add_alternative(html_body, subtype='html')  # HTML version (primary)
        
        # Set headers
        message["To"] = to
        message["From"] = from_email
        message["Subject"] = subject
        if cc: message["Cc"] = cc
        if bcc: message["Bcc"] = bcc
        
        # Encode message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {"raw": encoded_message}
        
        # Send message
        result = state.gmail_service.users().messages().send(userId="me", body=create_message).execute()
        
        logger.info(f'Email sent successfully! Message Id: {result["id"]}')
        return f'Email sent successfully! Message Id: {result["id"]}'
        
    except HttpError as error:
        logger.error(f"HttpError occurred: {error}")
        return f"Gmail API error: {error}"
    except Exception as e:
        logger.error(f"General error: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
def send_gmail_reply(message_id: str, body: str, reply_all: bool = False) -> str:
    """Reply to an existing email using HTML formatting.
    
    Args:
        message_id: ID of the message to reply to
        body: Reply content (will be converted to HTML automatically)
        reply_all: Whether to reply to all recipients
    """
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        # Convert text to HTML
        html_body = text_to_html(body)
        plain_body = html_to_plain_text(html_body)

        # Get sender email
        profile = state.gmail_service.users().getProfile(userId='me').execute()
        from_email = profile.get('emailAddress')
        
        # Get original message
        original = state.gmail_service.users().messages().get(userId='me', id=message_id).execute()
        headers = {h['name']: h['value'] for h in original['payload']['headers']}
        
        # Create reply message using EmailMessage
        message = EmailMessage()
        
        # Set content
        message.set_content(plain_body)
        message.add_alternative(html_body, subtype='html')
        
        # Set reply headers
        message['From'] = from_email
        message['To'] = headers.get('From')
        
        if reply_all and headers.get('To'):
            all_recipients = []
            if headers.get('To'):
                all_recipients.extend(headers['To'].split(','))
            if headers.get('Cc'):
                all_recipients.extend(headers['Cc'].split(','))
            # Remove sender from CC list
            cc_list = [addr.strip() for addr in all_recipients if addr.strip() != headers.get('From')]
            if cc_list:
                message['Cc'] = ','.join(cc_list)
        
        subject = headers.get('Subject', '')
        if not subject.startswith('Re: '):
            subject = f"Re: {subject}"
        message['Subject'] = subject
        message['In-Reply-To'] = headers.get('Message-ID')
        message['References'] = headers.get('References', '') + ' ' + headers.get('Message-ID', '')
        
        # Encode and create payload
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        msg_body = {'raw': encoded_message, 'threadId': original['threadId']}
        
        result = state.gmail_service.users().messages().send(userId='me', body=msg_body).execute()
        
        logger.info(f"Reply sent successfully. Message ID: {result['id']}")
        return f"Reply sent successfully! Message ID: {result['id']}"
        
    except Exception as e:
        logger.error(f"Send reply error: {str(e)}")
        return f"Error sending reply: {str(e)}"


@mcp.tool()
def forward_gmail_email(message_id: str, to: str, body: str, cc: Optional[str] = None) -> str:
    """Forward an existing email using HTML formatting.
    
    Args:
        message_id: ID of the message to forward
        to: Forward recipient
        body: Additional message content (will be converted to HTML)
        cc: CC recipients (optional)
    """
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        # Convert text to HTML
        html_body = text_to_html(body)
        plain_body = html_to_plain_text(html_body)
        
        # Get sender email
        profile = state.gmail_service.users().getProfile(userId='me').execute()
        from_email = profile.get('emailAddress')
        
        # Get original message
        original = state.gmail_service.users().messages().get(userId='me', id=message_id, format='full').execute()
        headers = {h['name']: h['value'] for h in original['payload']['headers']}
        original_body = extract_body(original['payload'])
        
        # Create forward text
        forward_text = f"\n\n---------- Forwarded message ---------\n"
        forward_text += f"From: {headers.get('From', '')}\n"
        forward_text += f"Date: {headers.get('Date', '')}\n"
        forward_text += f"Subject: {headers.get('Subject', '')}\n"
        forward_text += f"To: {headers.get('To', '')}\n\n"
        forward_text += original_body
        
        # Create HTML version of forward
        forward_html = f"""
        <div style="margin-top: 20px; border-top: 1px solid #ccc; padding-top: 10px;">
        <p><strong>---------- Forwarded message ---------</strong></p>
        <p><strong>From:</strong> {headers.get('From', '')}</p>
        <p><strong>Date:</strong> {headers.get('Date', '')}</p>
        <p><strong>Subject:</strong> {headers.get('Subject', '')}</p>
        <p><strong>To:</strong> {headers.get('To', '')}</p>
        <div style="margin-top: 10px;">{original_body}</div>
        </div>
        """
        
        # Create EmailMessage
        message = EmailMessage()
        
        # Combine body with forward content
        full_plain_body = plain_body + forward_text
        full_html_body = html_body + forward_html
        
        message.set_content(full_plain_body)
        message.add_alternative(full_html_body, subtype='html')
        
        # Set headers
        message['From'] = from_email
        message['To'] = to
        if cc:
            message['Cc'] = cc
        
        subject = headers.get('Subject', '')
        if not subject.startswith('Fwd: '):
            subject = f"Fwd: {subject}"
        message['Subject'] = subject
        
        # Encode and send
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        msg_body = {'raw': encoded_message}
        result = state.gmail_service.users().messages().send(userId='me', body=msg_body).execute()
        
        logger.info(f"Email forwarded successfully. Message ID: {result['id']}")
        return f"Email forwarded successfully! Message ID: {result['id']}"
        
    except Exception as e:
        logger.error(f"Forward email error: {str(e)}")
        return f"Error forwarding email: {str(e)}"


@mcp.tool()
def send_gmail_email_with_attachments(to: str, subject: str, body: str, 
                                    attachment_paths: List[str], 
                                    cc: Optional[str] = None, 
                                    bcc: Optional[str] = None) -> str:
    """Send email with file attachments using HTML formatting.
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email content (will be converted to HTML automatically)
        attachment_paths: List of file paths to attach
        cc: CC recipients (optional)
        bcc: BCC recipients (optional)
    """
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        # Convert text to HTML
        html_body = text_to_html(body)
        plain_body = html_to_plain_text(html_body)

        # Get sender email
        profile = state.gmail_service.users().getProfile(userId='me').execute()
        from_email = profile.get('emailAddress')
        
        # Create multipart message for attachments
        message = MIMEMultipart()
        message["To"] = to
        message["From"] = from_email
        message["Subject"] = subject
        if cc: message["Cc"] = cc
        if bcc: message["Bcc"] = bcc
        
        # Create alternative part for HTML + text
        alt_part = MIMEMultipart('alternative')
        alt_part.attach(MIMEText(plain_body, 'plain', 'utf-8'))
        alt_part.attach(MIMEText(html_body, 'html', 'utf-8'))
        message.attach(alt_part)
        
        # Add attachments
        for file_path in attachment_paths:
            if not os.path.exists(file_path):
                return f"Error: File not found: {file_path}"
            
            # Guess MIME type
            content_type, encoding = mimetypes.guess_type(file_path)
            if content_type is None or encoding is not None:
                content_type = 'application/octet-stream'
            
            main_type, sub_type = content_type.split('/', 1)
            
            # Read and attach file
            with open(file_path, 'rb') as f:
                attachment = MIMEBase(main_type, sub_type)
                attachment.set_payload(f.read())
                encoders.encode_base64(attachment)
                
                filename = os.path.basename(file_path)
                attachment.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{filename}"'
                )
                message.attach(attachment)
        
        # Encode and send
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'raw': encoded_message}
        
        result = state.gmail_service.users().messages().send(userId="me", body=create_message).execute()
        
        logger.info(f'Email with {len(attachment_paths)} attachments sent! Message Id: {result["id"]}')
        return f'Email with {len(attachment_paths)} attachments sent! Message Id: {result["id"]}'
        
    except Exception as e:
        logger.error(f"Send with attachments error: {str(e)}")
        return f"Error: {str(e)}"


# Keep the attachment functions unchanged as they don't deal with email body formatting
@mcp.tool()
def get_email_attachments(message_id: str) -> str:
    """Get list of attachments for a specific email."""
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        # Get message
        message = state.gmail_service.users().messages().get(userId='me', id=message_id).execute()
        
        attachments = []
        payload = message.get('payload', {})
        
        def extract_attachments(parts):
            for part in parts:
                if part.get('filename'):
                    attachment_info = {
                        'filename': part['filename'],
                        'mime_type': part['mimeType'],
                        'size': part.get('body', {}).get('size', 0),
                        'attachment_id': part.get('body', {}).get('attachmentId')
                    }
                    attachments.append(attachment_info)
                
                # Check nested parts
                if 'parts' in part:
                    extract_attachments(part['parts'])
        
        # Extract from parts
        if 'parts' in payload:
            extract_attachments(payload['parts'])
        
        logger.info(f"Found {len(attachments)} attachments in message {message_id}")
        return json.dumps(attachments, indent=2)
        
    except Exception as e:
        logger.error(f"Get attachments error: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
def download_gmail_attachment(message_id: str, attachment_id: str, filename: str, 
                             download_path: str = "./downloads") -> str:
    """Download a specific attachment from an email."""
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        # Create download directory
        os.makedirs(download_path, exist_ok=True)
        
        # Get attachment
        attachment = state.gmail_service.users().messages().attachments().get(
            userId='me', messageId=message_id, id=attachment_id).execute()
        
        # Decode attachment data
        file_data = base64.urlsafe_b64decode(attachment['data'])
        
        # Save file
        file_path = os.path.join(download_path, filename)
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        file_size = len(file_data)
        logger.info(f"Downloaded {filename} ({file_size} bytes) to {file_path}")
        return f"Downloaded {filename} ({file_size} bytes) to {file_path}"
        
    except Exception as e:
        logger.error(f"Download attachment error: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
def get_attachment_metadata(message_id: str) -> str:
    """Get detailed metadata for all attachments in an email."""
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        message = state.gmail_service.users().messages().get(userId='me', id=message_id).execute()
        
        attachments = []
        payload = message.get('payload', {})
        
        def process_parts(parts, level=0):
            for i, part in enumerate(parts):
                if part.get('filename'):
                    # Get attachment details
                    attachment_data = {
                        'filename': part['filename'],
                        'mime_type': part['mimeType'],
                        'size_bytes': part.get('body', {}).get('size', 0),
                        'attachment_id': part.get('body', {}).get('attachmentId'),
                        'part_id': part.get('partId'),
                        'headers': part.get('headers', []),
                        'level': level,
                        'index': i
                    }
                    
                    # Convert size to human readable
                    size_bytes = attachment_data['size_bytes']
                    if size_bytes < 1024:
                        size_str = f"{size_bytes} B"
                    elif size_bytes < 1024*1024:
                        size_str = f"{size_bytes/1024:.1f} KB"
                    else:
                        size_str = f"{size_bytes/(1024*1024):.1f} MB"
                    
                    attachment_data['size_human'] = size_str
                    attachments.append(attachment_data)
                
                # Process nested parts
                if 'parts' in part:
                    process_parts(part['parts'], level + 1)
        
        if 'parts' in payload:
            process_parts(payload['parts'])
        
        result = {
            'message_id': message_id,
            'total_attachments': len(attachments),
            'attachments': attachments
        }
        
        logger.info(f"Retrieved metadata for {len(attachments)} attachments")
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Get attachment metadata error: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
def download_all_attachments(message_id: str, download_path: str = "./downloads") -> str:
    """Download all attachments from an email."""
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        # Get attachment list
        attachments_json = get_email_attachments(message_id)
        attachments = json.loads(attachments_json)
        
        if not attachments:
            return "No attachments found in this email."
        
        downloaded = []
        failed = []
        
        for attachment in attachments:
            try:
                result = download_gmail_attachment(
                    message_id, 
                    attachment['attachment_id'], 
                    attachment['filename'],
                    download_path
                )
                downloaded.append(attachment['filename'])
            except Exception as e:
                failed.append(f"{attachment['filename']}: {str(e)}")
        
        summary = f"Downloaded {len(downloaded)} attachments"
        if failed:
            summary += f", {len(failed)} failed"
        
        result = {
            'summary': summary,
            'downloaded': downloaded,
            'failed': failed,
            'download_path': download_path
        }
        
        logger.info(summary)
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Download all attachments error: {str(e)}")
        return f"Error: {str(e)}"