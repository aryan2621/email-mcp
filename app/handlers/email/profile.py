import json
import logging

from googleapiclient.errors import HttpError

from app import mcp
import app.state as state
from app.handlers.auth import ensure_authenticated

logger = logging.getLogger('gmail-mcp')

@mcp.tool()
def get_gmail_profile() -> str:
    """
    Get Gmail profile information for the authenticated user.
    
    Returns:
        str: JSON string with profile information or error message.
    """
    if not ensure_authenticated():
        return "Error: Authentication required. Please run authenticate_gmail tool first."
    
    try:
        logger.info("Getting Gmail profile information")
        
        profile = state.gmail_service.users().getProfile(userId='me').execute()
        
        profile_data = {
            'email_address': profile.get('emailAddress'),
            'messages_total': profile.get('messagesTotal'),
            'threads_total': profile.get('threadsTotal'),
            'history_id': profile.get('historyId')
        }
        
        logger.info(f"Successfully retrieved profile for: {profile_data['email_address']}")
        return json.dumps(profile_data, indent=2)
        
    except HttpError as error:
        logger.error(f"Gmail API error: {error}")
        return f"Error: {str(error)}"
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return f"Error: {str(e)}" 