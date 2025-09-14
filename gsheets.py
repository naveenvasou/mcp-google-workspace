import os
from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from gspace_auth import get_service

TOKEN_PATH = "secrets/token.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def create_spreadsheet(title: str, sheet_titles: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Create a new Google Spreadsheet.

    Args:
        title (str): The name of the spreadsheet.
        sheet_titles (List[str], optional): List of sheet names to create.

    Returns:
        Dict[str, Any]: Spreadsheet metadata including spreadsheetId and URL.
    """
    service = get_service(api_name="sheets", api_version="v4", SCOPES=SCOPES)
    body = {
        "properties": {"title": title},
        "sheets": [{"properties": {"title": t}} for t in (sheet_titles or ["Sheet1"])]
    }
    return service.spreadsheets().create(body=body, fields="spreadsheetId,spreadsheetUrl").execute()


def read_sheet(spreadsheet_id: str, range_name: str) -> List[List[Any]]:
    """
    Read values from a spreadsheet.

    Args:
        spreadsheet_id (str): The ID of the spreadsheet.
        range_name (str): The A1 notation of the range (e.g., "Sheet1!A1:C10").

    Returns:
        List[List[Any]]: List of rows, where each row is a list of cell values.
    """
    service = get_service()
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
    service = get_service()
    body = {"values": values}
    return service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption="RAW",
        body=body
    ).execute()


def append_sheet(spreadsheet_id: str, range_name: str, values: List[List[Any]]) -> Dict[str, Any]:
    """
    Append values to the end of a sheet.

    Args:
        spreadsheet_id (str): The ID of the spreadsheet.
        range_name (str): The A1 notation of the target range (e.g., "Sheet1!A:C").
        values (List[List[Any]]): 2D array of values to append.

    Returns:
        Dict[str, Any]: API response with details of the update.
    """
    service = get_service()
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
    service = get_service()
    requests = [{"deleteSheet": {"sheetId": sheet_id}}]
    body = {"requests": requests}
    return service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id, body=body
    ).execute()
