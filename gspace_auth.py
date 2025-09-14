
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from dotenv import load_dotenv

load_dotenv()
base_path = os.getcwd()

def get_service(api_name: str, api_version: str, scopes: list):
    
    creds = None
    token_path = os.path.join(base_path, "secrets", f"{api_name}_token.json")   # cached refresh token

    # load saved creds
    if os.path.exists(token_path):
        print("token exist")
        creds = Credentials.from_authorized_user_file(token_path, scopes)

    # if no valid creds, start OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:

            client_file = os.path.join(base_path, "secrets", f"oauth_client.json")
            flow = InstalledAppFlow.from_client_secrets_file(client_file, scopes)
            creds = flow.run_local_server(port=0)   # opens browser for login

        # save creds for next time
        with open(token_path, "w") as f:
            f.write(creds.to_json())

    return build(api_name, api_version, credentials=creds)
