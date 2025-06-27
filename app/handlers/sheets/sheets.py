#!/usr/bin/env python3
"""
Google Sheets Integration - Basic Functions
"""

import json
import logging
from typing import Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app import mcp
import app.state as state
from app.handlers.auth import ensure_authenticated

logger = logging.getLogger('gmail-mcp')

# Global sheets service
sheets_service = None

def ensure_sheets_service():
    """Initialize sheets service if not already done."""
    global sheets_service
    if sheets_service is None and state.credentials:
        try:
            sheets_service = build('sheets', 'v4', credentials=state.credentials)
            logger.info("Google Sheets service initialized.")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets service: {e}")
            # This might happen if the 'sheets' scope is missing.
            return False
    return sheets_service is not None

@mcp.tool()
def create_spreadsheet(title: str) -> str:
    """Creates a new Google Spreadsheet.
    
    Args:
        title: The title of the new spreadsheet.
    """
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    if not ensure_sheets_service():
        return "Error: Sheets service not available. Make sure 'https://www.googleapis.com/auth/spreadsheets' scope is included in authentication."
    
    try:
        spreadsheet = {
            'properties': {
                'title': title
            }
        }
        sheet = sheets_service.spreadsheets().create(body=spreadsheet, fields='spreadsheetId,spreadsheetUrl').execute()
        
        result = {
            'spreadsheet_id': sheet.get('spreadsheetId'),
            'spreadsheet_url': sheet.get('spreadsheetUrl'),
            'title': title
        }
        logger.info(f"Created new spreadsheet '{title}' with ID: {result['spreadsheet_id']}")
        return json.dumps(result, indent=2)

    except HttpError as error:
        logger.error(f"Sheets API error in create_spreadsheet: {error}")
        return f"Sheets API error: {error}"
    except Exception as e:
        logger.error(f"Error creating spreadsheet: {str(e)}")
        return f"Error: {str(e)}"

@mcp.tool()
def append_to_sheet(spreadsheet_id: str, values: list, sheet_name: str = 'Sheet1') -> str:
    """Appends a row of values to a Google Sheet.
    
    Args:
        spreadsheet_id: The ID of the spreadsheet to append to.
        values: A list of values for the new row. E.g., ["Event Title", "John Doe", "2025-07-01"]
        sheet_name: The name of the sheet (tab) to append to. Defaults to 'Sheet1'.
    """
    if not ensure_authenticated():
        return "Error: Authentication required."
    
    if not ensure_sheets_service():
        return "Error: Sheets service not available."
        
    try:
        body = {
            'values': [values]  # The API expects a list of rows
        }
        
        # The range is just the sheet name to append to the first empty row
        result = sheets_service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}", # Append to the table, Sheets API finds the first empty row.
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body=body).execute()
        
        logger.info(f"Appended {len(values)} cells to sheet '{sheet_name}' in spreadsheet {spreadsheet_id}.")
        
        response = {
            "spreadsheet_id": spreadsheet_id,
            "updates": result.get('updates')
        }
        return json.dumps(response, indent=2)

    except HttpError as error:
        logger.error(f"Sheets API error in append_to_sheet: {error}")
        return f"Sheets API error: {error}"
    except Exception as e:
        logger.error(f"Error appending to sheet: {str(e)}")
        return f"Error: {str(e)}"

def _get_sheet_id_by_name(spreadsheet_id: str, sheet_name: str) -> Optional[int]:
    """Helper to get the integer sheetId from its name."""
    if not sheets_service:
        return None
    try:
        spreadsheet_metadata = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheets = spreadsheet_metadata.get('sheets', [])
        for sheet in sheets:
            if sheet.get('properties', {}).get('title') == sheet_name:
                return sheet.get('properties', {}).get('sheetId')
        return None
    except HttpError as error:
        logger.error(f"API error getting sheet ID: {error}")
        return None

@mcp.tool()
def delete_sheet_row(spreadsheet_id: str, row_number: int, sheet_name: str = 'Sheet1') -> str:
    """Deletes a specific row from a Google Sheet.

    Args:
        spreadsheet_id: The ID of the spreadsheet.
        row_number: The number of the row to delete (1-indexed).
        sheet_name: The name of the sheet (tab) to delete from. Defaults to 'Sheet1'.
    """
    if not ensure_authenticated():
        return "Error: Authentication required."

    if not ensure_sheets_service():
        return "Error: Sheets service not available."

    try:
        sheet_id = _get_sheet_id_by_name(spreadsheet_id, sheet_name)
        if sheet_id is None:
            return f"Error: Sheet with name '{sheet_name}' not found in spreadsheet '{spreadsheet_id}'."

        requests = [{
            'deleteDimension': {
                'range': {
                    'sheetId': sheet_id,
                    'dimension': 'ROWS',
                    'startIndex': row_number - 1,  # API is 0-indexed
                    'endIndex': row_number
                }
            }
        }]

        body = {
            'requests': requests
        }
        
        response = sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=body
        ).execute()

        logger.info(f"Deleted row {row_number} from sheet '{sheet_name}' in spreadsheet {spreadsheet_id}.")

        return json.dumps({
            "status": "success",
            "message": f"Row {row_number} deleted successfully from '{sheet_name}'.",
            "spreadsheet_id": spreadsheet_id,
            "response": response
        }, indent=2)

    except HttpError as error:
        logger.error(f"Sheets API error in delete_sheet_row: {error}")
        return f"Sheets API error: {error}"
    except Exception as e:
        logger.error(f"Error deleting sheet row: {str(e)}")
        return f"Error: {str(e)}" 