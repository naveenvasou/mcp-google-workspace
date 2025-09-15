import os
from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from gspace_auth import get_service

TOKEN_PATH = "secrets/token.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def list_sheets(query: Optional[str] = None, page_size: int = 10) -> List[Dict[str, Any]]:
    """
    List available Google Spreadsheet, optionally filter by name.

    Args:
        query (str, optional): Search query to filter Spreadsheet by title (case-insensitive).
        page_size (int): Maximum number of Spreadsheet to return.

    Returns:
        List[Dict[str, Any]]: A list of Spreadsheet metadata objects.
          Each dictionary contains:
            - "id" (str): Document ID.
            - "name" (str): Document title.
    """
    try:
        service = get_service(api_name="drive", api_version="v3", scopes=["https://www.googleapis.com/auth/drive.metadata.readonly"])
        q = "mimeType='application/vnd.google-apps.spreadsheet'"
        if query:
            q += f" and name contains '{query}'"
        results = service.files().list(
            q=q, pageSize=page_size, fields="files(id, name)"
        ).execute()
        return results.get("files", [])
    except HttpError as error:
        raise Exception(f"Error listing Spreadsheet: {error}")

def create_spreadsheet(title: str, sheet_titles: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Create a new Google Spreadsheet.

    Args:
        title (str): The name of the spreadsheet.
        sheet_titles (List[str], optional): List of sheet names to create.

    Returns:
        Dict[str, Any]: Spreadsheet metadata including spreadsheetId and URL.
    """
    service = get_service(api_name="sheets", api_version="v4", scopes=SCOPES)
    body = {
        "properties": {"title": title},
        "sheets": [{"properties": {"title": t}} for t in (sheet_titles or ["Sheet1"])]
    }
    return service.spreadsheets().create(body=body, fields="spreadsheetId,spreadsheetUrl").execute()


def read_sheet(spreadsheet_id: str, range_name: str) -> List[List[Any]]:
    """
Read values from a Google Spreadsheet.

Args:
    spreadsheet_id (str): The ID of the spreadsheet.
    range_name (str): The A1 notation of the range to read.
        - If you provide a specific range (e.g., "Sheet1!A1:C10"), only that
          block of cells will be returned.
        - If you provide only the sheet name (e.g., "Sheet1"), the API will
          return all values from the used range of that sheet (all rows and
          columns that contain data).

Returns:
    List[List[Any]]: A list of rows, where each row is represented as a list
    of cell values. Empty cells may be omitted. For example:
        [
            ["Name", "Age"],
            ["Alice", "25"],
            ["Bob", "30"]
        ]
"""
    service =  get_service(api_name="sheets", api_version="v4", scopes=SCOPES)
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=range_name
    ).execute()
    return result.get("values", [])


def write_sheet(spreadsheet_id: str, range_name: str, values: List[List[Any]]) -> Dict[str, Any]:
    """
    Write values to a spreadsheet.

    Args:
        spreadsheet_id (str): The ID of the spreadsheet.
        range_name (str): The A1 notation of the range (e.g., "Sheet1!A1").
        values (List[List[Any]]): 2D array of values to write.

    Returns:
        Dict[str, Any]: API response including updated range and row count.
    """
    service = get_service(api_name="sheets", api_version="v4", scopes=SCOPES)
    body = {"values": values}
    return service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption="RAW",
        body=body
    ).execute()


def append_sheet(spreadsheet_id: str, range_name: str, values: List[List[Any]]) -> Dict[str, Any]:
    """
    Append new rows of data to the end of a Google Sheet without overwriting existing values.

    Args:
        spreadsheet_id (str): The ID of the target spreadsheet.
        range_name (str): The A1 notation of the target columns 
        (e.g., "Sheet1!A:C"). The values will be appended 
        after the last non-empty row in this range.
        values (List[List[Any]]): 2D list of rows to append, 
        where each inner list represents one row.

    Returns:
        Dict[str, Any]: API response containing metadata about the operation, including:
        - "spreadsheetId" (str): Spreadsheet ID.
        - "tableRange" (str): The range of existing data before the append.
        - "updates" (dict): Update details such as updated range, rows, and columns.
    """
    service =  get_service(api_name="sheets", api_version="v4", scopes=SCOPES)
    body = {"values": values}
    return service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body=body
    ).execute()


def delete_sheet(spreadsheet_id: str, sheet_id: int) -> Dict[str, Any]:
    """
    Delete a specific sheet from a spreadsheet.

    Args:
        spreadsheet_id (str): The ID of the spreadsheet.
        sheet_id (int): The ID of the sheet tab to delete.

    Returns:
        Dict[str, Any]: API response confirming the deletion.
    """
    service =  get_service(api_name="sheets", api_version="v4", scopes=SCOPES)
    requests = [{"deleteSheet": {"sheetId": sheet_id}}]
    body = {"requests": requests}
    return service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id, body=body
    ).execute()
