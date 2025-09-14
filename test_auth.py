from gspace_auth import get_service

def test_calendar():
    
    scopes = ["https://www.googleapis.com/auth/calendar.readonly"]
    service = get_service("calendar", "v3", scopes)

    events_result = (
        service.events()
        .list(calendarId="primary", maxResults=5, singleEvents=True, orderBy="startTime")
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
        print("No upcoming events found.")
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        print(start, event["summary"])

if __name__ == "__main__":
    test_calendar()