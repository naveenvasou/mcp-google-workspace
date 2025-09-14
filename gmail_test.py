from typing import List, Dict, Any, Optional
import traceback
from gspace_auth import get_service  # your auth helper


def gmail_list_messages(maxResults: int = 20, query: Optional[str] = None) -> Any:
    """List message IDs matching query (or all). Returns list of message ids/threads."""
    try:
        scopes = ["https://www.googleapis.com/auth/gmail.readonly"]
        svc = get_service("gmail", "v1", scopes)
        params = {"userId": "me", "maxResults": maxResults}
        if query:
            params["q"] = query
        resp = svc.users().messages().list(**params).execute()
        return resp.get("messages", [])
    except Exception as e:
        return {"error": str(e), "trace": traceback.format_exc()}
    
print(gmail_list_messages(query="None"))