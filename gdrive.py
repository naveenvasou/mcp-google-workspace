import os
import io
from typing import List, Dict, Any, Optional
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError
from gspace_auth import get_service

# Centralized scopes (least-privilege set, you can replace with ["https://www.googleapis.com/auth/drive"])
DRIVE_SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive.metadata.readonly",
]

def list_files(page_size: int = 10) -> List[Dict[str, Any]]:
    """
    List files from Google Drive.

    Args:
        page_size (int): Maximum number of files to return.

    Returns:
        List[Dict[str, Any]]: List of file metadata dictionaries, each with:
            - "id" (str): File ID
            - "name" (str): File name
            - "mimeType" (str): File type
    """
    try:
        service = get_service("drive", "v3", scopes=["https://www.googleapis.com/auth/drive.metadata.readonly"])
        results = service.files().list(
            pageSize=page_size,
            fields="files(id, name, mimeType)"
        ).execute()
        return results.get("files", [])
    except HttpError as error:
        raise Exception(f"Error listing files: {error}")


def search_files(query: str, page_size: int = 10) -> List[Dict[str, Any]]:
    """
    Search for files in Google Drive matching a query.

    Args:
        query (str): Search expression in Drive query format
                     (e.g., "name contains 'report' and mimeType='application/pdf'")
        page_size (int): Maximum number of results to return.

    Returns:
        List[Dict[str, Any]]: Matching file metadata dictionaries.
    """
    try:
        service = get_service("drive", "v3", scopes=["https://www.googleapis.com/auth/drive.metadata.readonly"])
        results = service.files().list(
            q=query,
            pageSize=page_size,
            fields="files(id, name, mimeType)"
        ).execute()
        return results.get("files", [])
    except HttpError as error:
        raise Exception(f"Error searching files: {error}")


def upload_file(file_path: str, mime_type: str, folder_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Upload a file to Google Drive.

    Args:
        file_path (str): Path to the local file.
        mime_type (str): MIME type of the file (e.g., "application/pdf").
        folder_id (str, optional): Folder ID to upload into. Defaults to My Drive.

    Returns:
        Dict[str, Any]: Uploaded file metadata with "id" and "name".
    """
    try:
        service = get_service("drive", "v3", scopes=["https://www.googleapis.com/auth/drive.file"])
        file_metadata = {"name": os.path.basename(file_path)}
        if folder_id:
            file_metadata["parents"] = [folder_id]

        media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id, name"
        ).execute()
        return file
    except HttpError as error:
        raise Exception(f"Error uploading file: {error}")


def download_file(file_id: str, destination_path: str) -> str:
    """
    Download a file from Google Drive.

    Args:
        file_id (str): The ID of the file to download.
        destination_path (str): Local path where the file will be saved.

    Returns:
        str: Path to the downloaded file.
    """
    try:
        service = get_service("drive", "v3", scopes=["https://www.googleapis.com/auth/drive.readonly"])
        request = service.files().get_media(fileId=file_id)
        with io.FileIO(destination_path, "wb") as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
        return destination_path
    except HttpError as error:
        raise Exception(f"Error downloading file: {error}")


def delete_file(file_id: str) -> Dict[str, Any]:
    """
    Delete a file from Google Drive.

    Args:
        file_id (str): The ID of the file to delete.

    Returns:
        Dict[str, Any]: Empty response if successful.
    """
    try:
        service = get_service("drive", "v3", scopes=["https://www.googleapis.com/auth/drive.file"])
        return service.files().delete(fileId=file_id).execute()
    except HttpError as error:
        raise Exception(f"Error deleting file: {error}")
