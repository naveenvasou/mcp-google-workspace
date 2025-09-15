import os
from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from gspace_auth import get_service


# -------------------------
# Google Docs Helper Functions
# -------------------------

DOCS_SCOPES = ["https://www.googleapis.com/auth/documents"]

def list_docs(query: Optional[str] = None, page_size: int = 10) -> List[Dict[str, Any]]:
    """
    List available Google Docs, optionally filter by name.

    Args:
        query (str, optional): Search query to filter docs by title (case-insensitive).
        page_size (int): Maximum number of docs to return.

    Returns:
        List[Dict[str, Any]]: A list of doc metadata objects.
          Each dictionary contains:
            - "id" (str): Document ID.
            - "name" (str): Document title.
    """
    try:
        service = get_service(api_name="drive", api_version="v3", scopes=["https://www.googleapis.com/auth/drive.metadata.readonly"])
        q = "mimeType='application/vnd.google-apps.document'"
        if query:
            q += f" and name contains '{query}'"
        results = service.files().list(
            q=q, pageSize=page_size, fields="files(id, name)"
        ).execute()
        return results.get("files", [])
    except HttpError as error:
        raise Exception(f"Error listing documents: {error}")


def create_doc(title: str) -> Dict[str, Any]:
    """
    Create a new Google Doc with the given title.

    Args:
        title (str): Title of the new document.

    Returns:
        Dict[str, Any]: Metadata of the created document.
          Contains:
            - "documentId" (str): The new document’s ID.
            - "title" (str): Title of the document.
    """
    try:
        service = get_service(api_name="docs", api_version="v1",scopes=DOCS_SCOPES)
        doc = service.documents().create(body={"title": title}).execute()
        return {"documentId": doc.get("documentId"), "title": doc.get("title")}
    except HttpError as error:
        raise Exception(f"Error creating document: {error}")


def read_doc(document_id: str) -> str:
    """
    Read the full text content of a Google Doc.

    Args:
        document_id (str): The ID of the document to read.

    Returns:
        str: The extracted plain text content of the document.
    """
    try:
        service = get_service(api_name="docs", api_version="v1",scopes=DOCS_SCOPES)
        doc = service.documents().get(documentId=document_id).execute()
        content = []
        for element in doc.get("body", {}).get("content", []):
            if "paragraph" in element:
                for elem in element["paragraph"].get("elements", []):
                    text = elem.get("textRun", {}).get("content")
                    if text:
                        content.append(text)
        return "".join(content).strip()
    except HttpError as error:
        raise Exception(f"Error reading document: {error}")


def update_doc(document_id: str, text: str, location: str = "end") -> Dict[str, Any]:
    """
    Insert or replace text in a Google Doc.

    Args:
        document_id (str): The ID of the document to update.
        text (str): Text to insert.
        location (str): Where to insert text:
            - "end": Append to end of document.
            - "start": Insert at beginning.
            - "<index>": Insert at a given index position.

    Returns:
        Dict[str, Any]: API response confirming the update.
    """
    try:
        service = get_service(api_name="docs", api_version="v1",scopes=DOCS_SCOPES)
        if location == "start":
            requests = [{"insertText": {"location": {"index": 1}, "text": text}}]
        elif location == "end":
            doc = service.documents().get(documentId=document_id).execute()
            end_index = doc.get("body").get("content")[-1]["endIndex"]
            requests = [{"insertText": {"location": {"index": end_index - 1}, "text": text}}]
        elif location.isdigit():
            requests = [{"insertText": {"location": {"index": int(location)}, "text": text}}]
        else:
            raise ValueError("Invalid location. Use 'start', 'end', or a numeric index.")

        return service.documents().batchUpdate(
            documentId=document_id, body={"requests": requests}
        ).execute()
    except HttpError as error:
        raise Exception(f"Error updating document: {error}")


def delete_doc(document_id: str) -> Dict[str, Any]:
    """
    Delete a Google Doc.

    Args:
        document_id (str): The ID of the document to delete.

    Returns:
        Dict[str, Any]: API response confirming deletion.
    """
    try:
        service = get_service(api_name="docs", api_version="v1",scopes=DOCS_SCOPES)
        return service.files().delete(fileId=document_id).execute()
    except HttpError as error:
        raise Exception(f"Error deleting document: {error}")
