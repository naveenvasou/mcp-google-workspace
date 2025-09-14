# server.py
from mcp.server.fastmcp import FastMCP
import gmail as gw
import gcalendar as cl
from typing import List, Dict, Any, Optional
# Create FastMCP server instance
mcp = FastMCP("google-workspace")

### GMAIL ###
@mcp.tool()
def list_recent_email(max_results: int = 5) -> List[Dict[str, Any]]:
    """
    List recent emails from Gmail.

    Args:
        max_results (int): Number of recent emails to fetch.

    Returns:
        List[Dict[str, Any]]: A list of email metadata dictionaries with keys:
            - id (str): The Gmail message ID
            - threadId (str): The thread ID the message belongs to
            - subject (str): The email subject line
            - from (str): The sender information
            - body (str): The entire body of the email
    """
    return gw.list_recent_emails(max_results=max_results)

@mcp.tool()
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
    return gw.search_emails(keyword=keyword,
    from_email=from_email,
    subject=subject,
    is_unread=is_unread,
    after=after,   # format YYYY/MM/DD
    before=before,  # format YYYY/MM/DD
    user_id=user_id,
    max_results=max_results)

@mcp.tool()
def send_email(
    to: str,
    subject: str,
    body: str,
    attachment_paths: Optional[List[str]] = None,
) -> dict:
    """
    Send an email with optional attachments using Gmail API.

    Args:
        to (str): Recipient email address
        subject (str): Subject line of the email
        body (str): Plain text body of the email
        attachment_paths (List[str], optional): File paths for attachments

    Returns:
        dict: Gmail API response containing message details
    """
    return gw.send_email(
    to=to,
    subject=subject,
    body=body,
    attachment_paths=attachment_paths
    )
    
### CALENDAR ###
@mcp.tool()
def list_events(max_results: int = 10, time_min: str = None, time_max: str = None) -> List[Dict[str, Any]]:
    """
    List upcoming Google Calendar events within an optional date range.

    Args:
        max_results (int): Maximum number of events to return.
        time_min (str, optional): Start of the time window in ISO 8601 format (e.g., "2025-09-14T09:00:00Z").
        time_max (str, optional): End of the time window in ISO 8601 format.

    Returns:
        List[Dict[str, Any]]: A list of event objects. 
            Each event dictionary contains keys such as:
              - "id" (str): Unique event ID.
              - "summary" (str): Event title.
              - "start" (dict): Event start time (ISO datetime).
              - "end" (dict): Event end time (ISO datetime).
              - "attendees" (list, optional): List of attendee dictionaries with "email" and "responseStatus".
    """
    return cl.list_events(max_results=max_results, time_min=time_min, time_max=time_max)


@mcp.tool()
def create_event(summary: str, start: str, end: str, attendees: list = None, description: str = None) -> Dict[str, Any]:
    """
    Create a new Google Calendar event.

    Args:
        summary (str): Title of the event.
        start (str): Start time in ISO 8601 format.
        end (str): End time in ISO 8601 format.
        attendees (list, optional): List of attendee email addresses.
        description (str, optional): Description or notes for the event.

    Returns:
        Dict[str, Any]: The created event object with keys:
            - "id" (str): Event ID.
            - "summary" (str): Event title.
            - "start" (dict): Start time.
            - "end" (dict): End time.
            - "attendees" (list, optional): Attendee details.
    """
    return cl.create_event(summary=summary, start=start, end=end, attendees=attendees, description=description)


@mcp.tool()
def update_event(event_id: str, summary: str = None, start: str = None, end: str = None, attendees: list = None, description: str = None) -> Dict[str, Any]:
    """
    Update an existing Google Calendar event.

    Args:
        event_id (str): ID of the event to update.
        summary (str, optional): Updated title for the event.
        start (str, optional): Updated start time in ISO 8601 format.
        end (str, optional): Updated end time in ISO 8601 format.
        attendees (list, optional): Updated list of attendee email addresses.
        description (str, optional): Updated description for the event.

    Returns:
        Dict[str, Any]: The updated event object with keys:
            - "id" (str): Event ID.
            - "summary" (str): Event title.
            - "start" (dict): Updated start time.
            - "end" (dict): Updated end time.
            - "attendees" (list, optional): Updated attendee details.
    """
    return cl.update_event(event_id=event_id, summary=summary, start=start, end=end, attendees=attendees, description=description)


@mcp.tool()
def delete_event(event_id: str) ->  Dict[str, str]:
    """
    Delete a Google Calendar event.

    Args:
        event_id (str): ID of the event to delete.

    Returns:
        Dict[str, str]: A dictionary confirming deletion with keys:
            - "status" (str): Always "deleted".
            - "event_id" (str): The ID of the deleted event.
    """
    return cl.delete_event(event_id=event_id)



@mcp.tool()
def ping():
    """Ping the server to check connectivity."""
    return gw.ping()


# ----------------------
# Run the server
# ----------------------
if __name__ == "__main__":
    mcp.run()
