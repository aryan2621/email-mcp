import os
import json
import logging
from typing import List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from app import mcp
import app.state as state

logger = logging.getLogger('gmail-mcp')

CREDENTIALS_DIR = "credentials"
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/spreadsheets'
]

def _get_credential_path(email: str) -> str:
    """Gets the full path for a credential file."""
    return os.path.join(CREDENTIALS_DIR, f"{email}.json")

def ensure_authenticated() -> bool:
    """Ensure we have a valid and active authentication."""
    if state.gmail_service is None or state.credentials is None:
        return False
    # Check if token is still valid
    if state.credentials.expired and state.credentials.refresh_token:
        try:
            state.credentials.refresh(Request())
            logger.info("Refreshed expired token.")
        except Exception as e:
            logger.error(f"Failed to refresh token: {e}")
            state.gmail_service = None
            state.credentials = None
            return False
    return True

@mcp.tool()
def add_account() -> str:
    """
    Adds a new Google account by authenticating with OAuth2 and saves its credentials.
    This will open a browser window for you to authorize the application.
    """
    try:
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_CLIENT_SECRET')

        if not client_id or not client_secret:
            return "Error: Missing GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET env vars."

        client_config = {
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost"]
            }
        }
        
        flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
        creds = flow.run_local_server(port=0)

        # Get user's email to use as the filename
        service = build('gmail', 'v1', credentials=creds)
        profile = service.users().getProfile(userId='me').execute()
        email = profile.get('emailAddress')

        if not email:
            return "Error: Could not retrieve email address from Google account."

        # Save the credentials
        creds_path = _get_credential_path(email)
        with open(creds_path, 'w') as token_file:
            token_file.write(creds.to_json())

        logger.info(f"Successfully added and saved credentials for {email}")
        
        # Automatically switch to the newly added account
        return switch_account(email)

    except Exception as e:
        logger.error(f"Failed to add account: {e}")
        return f"Error adding account: {e}"

@mcp.tool()
def list_accounts() -> List[str]:
    """Lists all authenticated Google accounts."""
    if not os.path.exists(CREDENTIALS_DIR):
        return []
    
    accounts = [f.replace(".json", "") for f in os.listdir(CREDENTIALS_DIR) if f.endswith(".json")]
    logger.info(f"Found accounts: {accounts}")
    return accounts

@mcp.tool()
def switch_account(email: str) -> str:
    """
    Switches the active Google account to the specified email.
    The account must have been previously added with `add_account`.
    """
    creds_path = _get_credential_path(email)
    if not os.path.exists(creds_path):
        return f"Error: Account '{email}' not found. Please add it first using `add_account`."

    try:
        creds = Credentials.from_authorized_user_file(creds_path, SCOPES)
        
        # Refresh token if necessary
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Save the refreshed credentials
            with open(creds_path, 'w') as token_file:
                token_file.write(creds.to_json())

        state.credentials = creds
        state.gmail_service = build('gmail', 'v1', credentials=creds)
        state.active_account = email

        profile = state.gmail_service.users().getProfile(userId='me').execute()
        logger.info(f"Switched to account: {profile.get('emailAddress')}")
        return f"Successfully switched to {profile.get('emailAddress')}"

    except Exception as e:
        logger.error(f"Failed to switch account: {e}")
        return f"Error switching account: {e}"

@mcp.tool()
def remove_account(email: str) -> str:
    """
    Removes a saved Google account's credentials.
    """
    creds_path = _get_credential_path(email)
    if not os.path.exists(creds_path):
        return f"Error: Account '{email}' not found."

    try:
        os.remove(creds_path)
        
        # If the removed account was the active one, log out
        if state.active_account == email:
            state.credentials = None
            state.gmail_service = None
            state.active_account = None
            logger.info(f"Removed active account: {email}. You are now logged out.")
            return f"Successfully removed {email}. You are now logged out."

        logger.info(f"Removed account: {email}")
        return f"Successfully removed {email}."
        
    except Exception as e:
        logger.error(f"Failed to remove account: {e}")
        return f"Error removing account: {e}"

@mcp.tool()
def check_gmail_scopes() -> str:
    """Check current Gmail API scopes and permissions."""
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    try:
        # Check if we can access profile (basic scope test)
        profile = state.gmail_service.users().getProfile(userId='me').execute()
        
        # Check current token scopes
        if hasattr(state.credentials, 'scopes'):
            current_scopes = state.credentials.scopes
        else:
            current_scopes = ["Unable to determine scopes"]
        
        # Try to access different Gmail functions to test permissions
        tests = {
            "read_profile": "✅ SUCCESS",
            "list_messages": "❌ NOT TESTED",
            "send_permission": "❌ NOT TESTED"
        }
        
        # Test list messages
        try:
            state.gmail_service.users().messages().list(userId='me', maxResults=1).execute()
            tests["list_messages"] = "✅ SUCCESS"
        except Exception as e:
            tests["list_messages"] = f"❌ FAILED: {str(e)}"
        
        # We can't really test send without sending, but we can check the service
        try:
            # This should not fail if we have proper scopes
            service_info = str(state.gmail_service._resourceDesc.get('resources', {}).keys())
            if 'messages' in service_info:
                tests["send_permission"] = "✅ Service has messages resource"
            else:
                tests["send_permission"] = "❌ Missing messages resource"
        except Exception as e:
            tests["send_permission"] = f"❌ Error: {str(e)}"
        
        result = {
            "authenticated_email": profile.get('emailAddress'),
            "current_scopes": current_scopes,
            "permission_tests": tests,
            "required_scopes": SCOPES
        }
        
        logger.info(f"Scope check results: {json.dumps(result, indent=2)}")
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Scope check error: {str(e)}")
        return f"Error checking scopes: {str(e)}" 