import os
from typing import List, Optional, Dict, Any
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from gspace_auth import get_service

CALENDAR_SCOPES = [
    "https://www.googleapis.com/auth/calendar"
]


def list_events(max_results: int = 10, time_min: Optional[str] = None, time_max: Optional[str] = None) -> List[Dict[str, Any]]:
    """List upcoming Google Calendar events"""
    service = get_service("calendar", "v3", CALENDAR_SCOPES)

    events_result = service.events().list(
        calendarId="primary",
        timeMin=time_min,
        timeMax=time_max,
        maxResults=max_results,
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    return events_result.get("items", [])


def create_event(summary: str, start: str, end: str, attendees: Optional[List[str]] = None, description: Optional[str] = None) -> Dict[str, Any]:
    """Create a new Google Calendar event"""
    service = get_service("calendar", "v3", CALENDAR_SCOPES)

    event_body = {
        "summary": summary,
        "description": description,
        "start": {"dateTime": start, "timeZone": "UTC"},
        "end": {"dateTime": end, "timeZone": "UTC"},
    }

    if attendees:
        event_body["attendees"] = [{"email": a} for a in attendees]

    event = service.events().insert(calendarId="primary", body=event_body).execute()
    return event


def update_event(event_id: str, summary: Optional[str] = None, start: Optional[str] = None, end: Optional[str] = None, attendees: Optional[List[str]] = None, description: Optional[str] = None) -> Dict[str, Any]:
    """Update an existing event"""
    service = get_service("calendar", "v3", CALENDAR_SCOPES)

    event = service.events().get(calendarId="primary", eventId=event_id).execute()

    if summary:
        event["summary"] = summary
    if description:
        event["description"] = description
    if start:
        event["start"] = {"dateTime": start, "timeZone": "UTC"}
    if end:
        event["end"] = {"dateTime": end, "timeZone": "UTC"}
    if attendees:
        event["attendees"] = [{"email": a} for a in attendees]

    updated_event = service.events().update(calendarId="primary", eventId=event_id, body=event).execute()
    return updated_event


def delete_event(event_id: str) -> Dict[str, str]:
    """Delete a Google Calendar event"""
    service = get_service("calendar", "v3", CALENDAR_SCOPES)

    service.events().delete(calendarId="primary", eventId=event_id).execute()
    return {"status": "deleted", "event_id": event_id}

