#!/usr/bin/env python3
"""
Gmail Calendar Integration - Basic Functions
Add this to your main Gmail MCP server
"""

import json
import logging
import base64
from datetime import datetime, timedelta
from typing import Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app import mcp
import app.state as state
from app.handlers.auth import ensure_authenticated

logger = logging.getLogger('gmail-mcp')

# Global calendar service
calendar_service = None

def ensure_calendar_service():
    """Initialize calendar service if not already done."""
    global calendar_service
    if calendar_service is None and state.credentials:
        calendar_service = build('calendar', 'v3', credentials=state.credentials)
    return calendar_service is not None

@mcp.tool()
def get_calendar_events(days_ahead: int = 7, max_results: int = 20, 
                       calendar_id: str = 'primary') -> str:
    """Get upcoming calendar events.
    
    Args:
        days_ahead: Number of days to look ahead (default: 7)
        max_results: Maximum number of events to return (default: 20)
        calendar_id: Calendar ID to query (default: 'primary')
    """
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    if not ensure_calendar_service():
        return "Error: Calendar service not available. Make sure calendar scope is included in authentication."
    
    try:
        # Calculate time range
        now = datetime.utcnow()
        time_min = now.isoformat() + 'Z'
        time_max = (now + timedelta(days=days_ahead)).isoformat() + 'Z'
        
        logger.info(f"Fetching calendar events from {time_min} to {time_max}")
        
        # Get events
        events_result = calendar_service.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        # Format events for response
        formatted_events = []
        for event in events:
            # Handle different time formats
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            event_data = {
                'id': event['id'],
                'summary': event.get('summary', 'No Title'),
                'description': event.get('description', ''),
                'start': start,
                'end': end,
                'location': event.get('location', ''),
                'attendees': [
                    {
                        'email': attendee.get('email'),
                        'response': attendee.get('responseStatus', 'needsAction'),
                        'organizer': attendee.get('organizer', False)
                    }
                    for attendee in event.get('attendees', [])
                ],
                'creator': event.get('creator', {}).get('email', ''),
                'organizer': event.get('organizer', {}).get('email', ''),
                'status': event.get('status', 'confirmed'),
                'html_link': event.get('htmlLink', ''),
                'meeting_link': event.get('hangoutLink', ''),
                'recurring': event.get('recurrence') is not None
            }
            formatted_events.append(event_data)
        
        result = {
            'calendar_id': calendar_id,
            'time_range': {
                'start': time_min,
                'end': time_max,
                'days_ahead': days_ahead
            },
            'total_events': len(formatted_events),
            'events': formatted_events
        }
        return json.dumps(result, indent=2)
    except HttpError as error:
        logger.error(f"Calendar API error: {error}")
        return f"Calendar API error: {error}"
    except Exception as e:
        logger.error(f"Calendar error: {str(e)}")
        return f"Error: {str(e)}"
        
@mcp.tool()
def create_event_from_email(message_id: str, event_title: Optional[str] = None,
                           start_datetime: Optional[str] = None,
                           end_datetime: Optional[str] = None,
                           location: Optional[str] = None,
                           description: Optional[str] = None,
                           attendees: Optional[list] = None) -> str:
    """Create calendar event from email content.
    
    Args:
        message_id: Gmail message ID to extract info from
        event_title: Override title (uses email subject if not provided)
        start_datetime: ISO format datetime (e.g., '2025-06-23T10:00:00')
        end_datetime: ISO format datetime (e.g., '2025-06-23T11:00:00') 
        location: Event location (extracted from email if not provided)
        description: Event description (uses email body if not provided)
        attendees: List of email addresses (uses email To/CC if not provided)
    """
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    if not ensure_calendar_service():
        return "Error: Calendar service not available."
    
    try:
        # Get email details using existing function
        email_details = state.gmail_service.users().messages().get(
            userId='me', id=message_id, format='full').execute()
        
        # Extract email headers
        headers = {h['name']: h['value'] for h in email_details['payload']['headers']}
        
        # Extract email body (reuse existing function if available)
        def extract_email_body(payload):
            body = ""
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        data = part['body']['data']
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
                        break
            elif payload.get('body', {}).get('data'):
                data = payload['body']['data']
                body = base64.urlsafe_b64decode(data).decode('utf-8')
            return body
        
        email_body = extract_email_body(email_details['payload'])
        
        # Use provided values or extract from email
        title = event_title or headers.get('Subject', 'Meeting from Email')
        desc = description or f"Created from email:\n\nSubject: {headers.get('Subject', '')}\nFrom: {headers.get('From', '')}\n\n{email_body[:500]}..."
        
        # Extract attendees from email if not provided
        if not attendees:
            attendees = []
            # Add sender
            if headers.get('From'):
                # Extract email from "Name <email>" format
                sender_email = headers['From']
                if '<' in sender_email:
                    sender_email = sender_email.split('<')[1].split('>')[0]
                attendees.append(sender_email)
            
            # Add To recipients
            if headers.get('To'):
                to_emails = headers['To'].split(',')
                for email in to_emails:
                    clean_email = email.strip()
                    if '<' in clean_email:
                        clean_email = clean_email.split('<')[1].split('>')[0]
                    attendees.append(clean_email)
        
        # Create event object
        event = {
            'summary': title,
            'description': desc,
            'attendees': [{'email': email.strip()} for email in attendees if email.strip()],
        }
        
        # Add location if provided
        if location:
            event['location'] = location
        
        # Handle datetime
        if start_datetime and end_datetime:
            # Ensure timezone format
            if not start_datetime.endswith('Z') and '+' not in start_datetime:
                start_datetime += 'Z'
            if not end_datetime.endswith('Z') and '+' not in end_datetime:
                end_datetime += 'Z'
                
            event['start'] = {'dateTime': start_datetime}
            event['end'] = {'dateTime': end_datetime}
        else:
            # Default to 1 hour meeting starting in 1 hour
            now = datetime.utcnow()
            start_time = now + timedelta(hours=1)
            end_time = start_time + timedelta(hours=1)
            
            event['start'] = {'dateTime': start_time.isoformat() + 'Z'}
            event['end'] = {'dateTime': end_time.isoformat() + 'Z'}
        
        # Create the event
        created_event = calendar_service.events().insert(
            calendarId='primary',
            body=event,
            sendUpdates='all'  # Send invites to attendees
        ).execute()
        
        # Format response
        result = {
            'event_id': created_event['id'],
            'event_title': created_event['summary'],
            'start_time': created_event['start'].get('dateTime'),
            'end_time': created_event['end'].get('dateTime'),
            'attendees_count': len(attendees),
            'calendar_link': created_event.get('htmlLink'),
            'source_email_id': message_id,
            'source_email_subject': headers.get('Subject', '')
        }
        return json.dumps(result, indent=2) 
    except Exception as e:
        logger.error(f"Error creating event from email: {str(e)}")
        return f"Error: {str(e)}"

@mcp.tool()
def create_calendar_event(title: str, start_datetime: str, end_datetime: str,
                           attendees: Optional[list] = None,
                           location: Optional[str] = None,
                           description: Optional[str] = None,
                           timezone: str = 'Asia/Kolkata') -> str:
    """Create a new calendar event from scratch.
    
    Args:
        title: The title of the event. (Required)
        start_datetime: Start time in ISO format (e.g., '2025-06-23T10:00:00'). (Required)
        end_datetime: End time in ISO format (e.g., '2025-06-23T11:00:00'). (Required)
        attendees: List of email addresses to invite.
        location: Event location.
        description: Event description.
        timezone: IANA timezone name (e.g., "Europe/Zurich"). Defaults to 'Asia/Kolkata'.
    """
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    if not ensure_calendar_service():
        return "Error: Calendar service not available."
    
    try:
        event = {
            'summary': title,
            'start': {
                'dateTime': start_datetime,
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end_datetime,
                'timeZone': timezone,
            },
        }

        if location:
            event['location'] = location
        
        if description:
            event['description'] = description

        if attendees:
            event['attendees'] = [{'email': email.strip()} for email in attendees if email.strip()]
        
        created_event = calendar_service.events().insert(
            calendarId='primary',
            body=event,
            sendUpdates='all'  # Send invites to attendees
        ).execute()

        result = {
            'event_id': created_event['id'],
            'event_title': created_event['summary'],
            'start_time': created_event['start'].get('dateTime'),
            'end_time': created_event['end'].get('dateTime'),
            'attendees_count': len(attendees) if attendees else 0,
            'calendar_link': created_event.get('htmlLink'),
        }
        return json.dumps(result, indent=2)
    except HttpError as error:
        logger.error(f"Calendar API error creating event: {error}")
        return f"Calendar API error: {error}"
    except Exception as e:
        logger.error(f"Error creating calendar event: {str(e)}")
        return f"Error: {str(e)}"

@mcp.tool()
def cancel_calendar_event(event_id: str, calendar_id: str = 'primary', send_updates: str = 'all') -> str:
    """Cancels/deletes a calendar event.

    Args:
        event_id: The ID of the event to cancel.
        calendar_id: The ID of the calendar containing the event. Defaults to 'primary'.
        send_updates: Whether to send notifications to attendees. Can be 'all', 'externalOnly', or 'none'. Defaults to 'all'.
    """
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    if not ensure_calendar_service():
        return "Error: Calendar service not available."

    try:
        calendar_service.events().delete(
            calendarId=calendar_id,
            eventId=event_id,
            sendUpdates=send_updates
        ).execute()

        logger.info(f"Canceled event with ID: {event_id} from calendar: {calendar_id}")
        return json.dumps({
            "status": "success",
            "message": "Event canceled successfully.",
            "event_id": event_id
        }, indent=2)
    except HttpError as error:
        logger.error(f"Calendar API error in cancel_calendar_event: {error}")
        if error.resp.status == 404:
            return f"Error: Event with ID '{event_id}' not found."
        return f"Calendar API error: {error}"
    except Exception as e:
        logger.error(f"Error canceling event: {str(e)}")
        return f"Error: {str(e)}"
        
@mcp.tool()
def check_availability(emails: list, start_datetime: str, end_datetime: str,
                      timezone: str = 'UTC') -> str:
    """Check calendar availability for multiple people.
    
    Args:
        emails: List of email addresses to check
        start_datetime: Start time in ISO format (e.g., '2025-06-23T10:00:00')
        end_datetime: End time in ISO format (e.g., '2025-06-23T11:00:00')
        timezone: Timezone (default: 'UTC')
    """
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    if not ensure_calendar_service():
        return "Error: Calendar service not available."
    
    try:
        # Ensure timezone format
        if not start_datetime.endswith('Z') and '+' not in start_datetime:
            start_datetime += 'Z'
        if not end_datetime.endswith('Z') and '+' not in end_datetime:
            end_datetime += 'Z'
        
        logger.info(f"Checking availability for {len(emails)} people from {start_datetime} to {end_datetime}")
        
        # Build freebusy query
        freebusy_query = {
            'timeMin': start_datetime,
            'timeMax': end_datetime,
            'timeZone': timezone,
            'items': [{'id': email} for email in emails]
        }
        
        # Query freebusy information
        freebusy_result = calendar_service.freebusy().query(body=freebusy_query).execute()
        
        # Process results
        availability_results = []
        
        for email in emails:
            calendar_data = freebusy_result.get('calendars', {}).get(email, {})
            busy_periods = calendar_data.get('busy', [])
            errors = calendar_data.get('errors', [])
            
            # Determine if person is available
            is_available = len(busy_periods) == 0 and len(errors) == 0
            
            person_result = {
                'email': email,
                'available': is_available,
                'busy_periods': busy_periods,
                'conflicts': len(busy_periods),
                'errors': errors
            }
            
            # Add conflict details
            if busy_periods:
                person_result['conflict_details'] = []
                for busy in busy_periods:
                    conflict = {
                        'start': busy.get('start'),
                        'end': busy.get('end'),
                        'duration_minutes': _calculate_duration_minutes(
                            busy.get('start'), busy.get('end')
                        )
                    }
                    person_result['conflict_details'].append(conflict)
            
            availability_results.append(person_result)
        
        # Calculate overall availability
        all_available = all(person['available'] for person in availability_results)
        available_count = sum(1 for person in availability_results if person['available'])
        
        # Find alternative times if not all available
        suggestions = []
        if not all_available:
            suggestions = _suggest_alternative_times(
                emails, start_datetime, end_datetime, timezone
            )
        
        result = {
            'query': {
                'start_time': start_datetime,
                'end_time': end_datetime,
                'timezone': timezone,
                'participants': emails
            },
            'summary': {
                'all_available': all_available,
                'available_count': available_count,
                'total_participants': len(emails),
                'conflicts_found': sum(person['conflicts'] for person in availability_results)
            },
            'participants': availability_results,
            'alternative_suggestions': suggestions
        }
        
        logger.info(f"Availability check complete: {available_count}/{len(emails)} available")
        return json.dumps(result, indent=2)
        
    except HttpError as error:
        logger.error(f"Calendar API error: {error}")
        return f"Calendar API error: {error}"
    except Exception as e:
        logger.error(f"Check availability error: {str(e)}")
        return f"Error: {str(e)}"

def _calculate_duration_minutes(start_time: str, end_time: str) -> int:
    """Calculate duration between two ISO datetime strings in minutes."""
    try:
        start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        duration = end - start
        return int(duration.total_seconds() / 60)
    except:
        return 0

def _suggest_alternative_times(emails: list, original_start: str, original_end: str, 
                              timezone: str) -> list:
    """Suggest alternative meeting times when conflicts exist."""
    suggestions = []
    
    try:
        # Parse original times
        start_dt = datetime.fromisoformat(original_start.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(original_end.replace('Z', '+00:00'))
        duration = end_dt - start_dt
        
        # Suggest times: +1 hour, +2 hours, +1 day same time
        alternatives = [
            start_dt + timedelta(hours=1),
            start_dt + timedelta(hours=2), 
            start_dt + timedelta(days=1),
            start_dt + timedelta(days=1, hours=1)
        ]
        
        for alt_start in alternatives:
            alt_end = alt_start + duration
            
            # Quick availability check for suggested time
            try:
                freebusy_query = {
                    'timeMin': alt_start.isoformat(),
                    'timeMax': alt_end.isoformat(),
                    'timeZone': timezone,
                    'items': [{'id': email} for email in emails]
                }
                
                freebusy_result = calendar_service.freebusy().query(body=freebusy_query).execute()
                
                # Check if this time works for everyone
                all_free = True
                for email in emails:
                    calendar_data = freebusy_result.get('calendars', {}).get(email, {})
                    if calendar_data.get('busy', []) or calendar_data.get('errors', []):
                        all_free = False
                        break
                
                if all_free:
                    suggestions.append({
                        'start_time': alt_start.isoformat(),
                        'end_time': alt_end.isoformat(),
                        'available_for_all': True,
                        'suggestion_type': 'alternative_time'
                    })
                    
                    # Limit to 3 suggestions
                    if len(suggestions) >= 3:
                        break
                        
            except Exception:
                continue  # Skip this suggestion if error
                
    except Exception as e:
        logger.error(f"Error generating suggestions: {str(e)}")
    
    return suggestions