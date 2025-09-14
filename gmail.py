# gworkspace.py
import os
import io
import base64
import traceback
from typing import List, Dict, Any, Optional

from gspace_auth import get_service  # your auth helper

# Gmail helpers
from email.message import EmailMessage
from googleapiclient.errors import HttpError

GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send"]

def list_recent_emails( max_results: int = 10, query: Optional[str] = None) -> List[Dict[str, Any]]:
    
    gmail_service = get_service(api_name="gmail", api_version="v1", scopes=GMAIL_SCOPES)
    try:
        results = gmail_service.users().messages().list(
            userId="me",
            maxResults=max_results,
            q=query,
            labelIds=["INBOX"]
        ).execute()
        
        messages = results.get("messages", [])
        email_list: List[Dict[str, Any]] = []
        
        for msg in messages:
            msg_detail = gmail_service.users().messages().get(
                userId="me",
                id=msg["id"],
                format="full"
            ).execute()
            
            headers = msg_detail.get("payload", {}).get("headers", [])
            subject = next((h["value"] for h in headers if h["name"] == "Subject"), "")
            sender = next((h["value"] for h in headers if h["name"] == "From"), "")
            
            body = ""
            payload = msg_detail.get("payload", {})
            if "parts" in payload:
                for part in payload["parts"]:
                    if part["mimeType"] == "text/plain":  # prefer plain text
                        body = base64.urlsafe_b64decode(
                            part["body"]["data"].encode("UTF-8")
                        ).decode("UTF-8")
                        break
                    elif part["mimeType"] == "text/html" and not body:
                        body = base64.urlsafe_b64decode(
                            part["body"]["data"].encode("UTF-8")
                        ).decode("UTF-8")
            else:  # simple email
                data = payload.get("body", {}).get("data")
                if data:
                    body = base64.urlsafe_b64decode(data.encode("UTF-8")).decode("UTF-8")
            
            email_list.append({
                "id": msg["id"],
                "threadId": msg_detail.get("threadId", ""),
                "subject": subject,
                "from": sender,
                "body": body
            })
        return email_list
    
    except HttpError as error:
        print(f"An error Ocurred: {error}")
        return []
    
def search_emails(
    keyword: Optional[str] = None,
    from_email: Optional[str] = None,
    subject: Optional[str] = None,
    is_unread: bool = False,
    after: Optional[str] = None,   # format YYYY/MM/DD
    before: Optional[str] = None,  # format YYYY/MM/DD
    user_id: str = "me",
    max_results: int = 10
) -> List[Dict[str, Any]]:
    """
    Search Gmail emails with structured filters instead of raw query strings.

    Args:
        service (Resource): Authorized Gmail API service instance
        keyword (str): General keyword to search anywhere in the email
        from_email (str): Filter emails by sender
        subject (str): Filter emails by subject text
        is_unread (bool): If True, only return unread emails
        after (str): Filter emails after this date (YYYY/MM/DD)
        before (str): Filter emails before this date (YYYY/MM/DD)
        user_id (str): Gmail user ID, use "me" for authenticated user
        max_results (int): Maximum number of emails to return

    Returns:
        List[Dict[str, Any]]: List of email data with subject, sender, body
    """
    try:
        gmail_service = get_service(api_name="gmail", api_version="v1", scopes=GMAIL_SCOPES)
        # Build query string dynamically
        query_parts: List[str] = []

        if keyword:
            query_parts.append(keyword)
        if from_email:
            query_parts.append(f"from:{from_email}")
        if subject:
            query_parts.append(f"subject:{subject}")
        if is_unread:
            query_parts.append("is:unread")
        if after:
            query_parts.append(f"after:{after}")
        if before:
            query_parts.append(f"before:{before}")

        query = " ".join(query_parts).strip()

        # Search Gmail
        results = gmail_service.users().messages().list(
            userId=user_id,
            q=query,
            maxResults=max_results
        ).execute()

        messages = results.get("messages", [])
        email_list: List[Dict[str, Any]] = []

        for msg in messages:
            msg_detail = gmail_service.users().messages().get(
                userId=user_id,
                id=msg["id"],
                format="full"
            ).execute()

            headers = msg_detail.get("payload", {}).get("headers", [])
            subject_val = next((h["value"] for h in headers if h["name"] == "Subject"), "")
            sender = next((h["value"] for h in headers if h["name"] == "From"), "")

            # Extract body
            body = ""
            payload = msg_detail.get("payload", {})
            if "parts" in payload:
                for part in payload["parts"]:
                    if part["mimeType"] == "text/plain":
                        body = base64.urlsafe_b64decode(
                            part["body"]["data"].encode("UTF-8")
                        ).decode("UTF-8")
                        break
                    elif part["mimeType"] == "text/html" and not body:
                        body = base64.urlsafe_b64decode(
                            part["body"]["data"].encode("UTF-8")
                        ).decode("UTF-8")
            else:
                data = payload.get("body", {}).get("data")
                if data:
                    body = base64.urlsafe_b64decode(data.encode("UTF-8")).decode("UTF-8")

            email_list.append({
                "id": msg["id"],
                "threadId": msg_detail.get("threadId", ""),
                "subject": subject_val,
                "from": sender,
                "body": body
            })

        return email_list

    except HttpError as error:
        print(f"An error occurred: {error}")
        return []

def send_email(
    to: str,
    subject: str,
    body: str,
    attachment_paths: Optional[List[str]] = None,
) -> dict:
    """
    Send an email with optional attachments using Gmail API.

    Args:
        service (Resource): Authorized Gmail API service instance
        email_identifier (str): Gmail user ID ("me" for authenticated user)
        to (str): Recipient email address
        subject (str): Subject line of the email
        body (str): Plain text body of the email
        attachment_paths (List[str], optional): File paths for attachments

    Returns:
        dict: Gmail API response containing message details
    """
    try:
        gmail_service = get_service(api_name="gmail", api_version="v1", scopes=GMAIL_SCOPES)
        # Build the email
        email_identifier = "me"
        message = EmailMessage()
        message.set_content(body)
        message["To"] = to
        message["From"] = email_identifier
        message["Subject"] = subject

        # Add attachments if provided
        if attachment_paths:
            for file_path in attachment_paths:
                if not os.path.exists(file_path):
                    print(f"⚠️ Skipping missing file: {file_path}")
                    continue
                with open(file_path, "rb") as f:
                    file_data = f.read()
                    file_name = os.path.basename(file_path)
                message.add_attachment(
                    file_data,
                    maintype="application",
                    subtype="octet-stream",
                    filename=file_name,
                )

        # Encode message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        send_result = (
            gmail_service.users()
            .messages()
            .send(userId=email_identifier, body={"raw": encoded_message})
            .execute()
        )

        print(f"✅ Email sent to {to} (ID: {send_result['id']})")
        return send_result

    except HttpError as error:
        print(f"❌ An error occurred: {error}")
        return f"❌ An error occurred: {error}"
    
def ping():
    """Ping the server to check connectivity."""
    return "PONG"