# Google Workspace MCP Server

This project exposes Google Workspace APIs as **structured MCP tools**, so you can search emails, manage calendar events, edit documents, handle spreadsheets, and manage files — all through natural language.

---

## Features

-  **Gmail**: Search, read, and send emails with filters for sender, subject, and dates.  
-  **Calendar**: List, create, update, and delete events.  
-  **Docs**: Create new docs, read text, insert/update content, and delete documents.  
-  **Sheets**: Create spreadsheets, read/write cell ranges, and append rows.  
-  **Drive**: Search, upload, download, and delete files.   

All tools return structured JSON outputs — designed for **LLM use**.

---

##  Installation

### Prerequisites
- Python **3.10+**
- [uv](https://github.com/astral-sh/uv) package manager
- A Google Cloud project with OAuth 2.0 Desktop credentials

---

### 1. Clone the Repo
```bash
git clone https://github.com/naveenvasou/mcp-google-workspace.git
cd mcp-google-workspace
```

---

### 2. Setup Secrets
1. In the project root, create a `secrets/` folder:
   ```bash
   mkdir secrets
   ```
2. Download your OAuth client credentials JSON from the [Google Cloud Console](https://console.cloud.google.com/apis/credentials).  
   - Choose **Desktop Application** as the client type.  
   - Save the JSON file into the `secrets/` folder.  
   - Example: `secrets/client_secret.json`  

The server will automatically use this file for authentication and store token caches in `secrets/token.json`.

---

### 3. Enable Required APIs
In your Google Cloud project, enable these APIs:
- [Gmail API](https://console.cloud.google.com/flows/enableapi?apiid=gmail.googleapis.com)  
- [Google Calendar API](https://console.cloud.google.com/flows/enableapi?apiid=calendar-json.googleapis.com)  
- [Google Drive API](https://console.cloud.google.com/flows/enableapi?apiid=drive.googleapis.com)  
- [Google Docs API](https://console.cloud.google.com/flows/enableapi?apiid=docs.googleapis.com)  
- [Google Sheets API](https://console.cloud.google.com/flows/enableapi?apiid=sheets.googleapis.com)  

---

### 4. Run the Server
```bash
uv run server.py
```

The first time you run it, you’ll be prompted to authenticate with your Google account. Tokens will be saved in `secrets/token.json` for reuse.

---

## 💻 Claude Desktop Setup

To connect this server with Claude Desktop:

1. Open **Claude Desktop → Settings → Developer → Edit Config**  
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`  
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. Add the following:
```json
{
  "mcpServers": {
    "google_workspace": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/mcp-google-workspace",
        "server.py"
      ]
    }
  }
}
```

3. Restart Claude Desktop.  
Now you can say:  
- *“Search my unread emails from Alice after Sept 1st”*  
- *“Create a calendar event tomorrow at 3pm with John”*  
- *“Append a new row to Sheet1 in my budget spreadsheet”*  

---

##  Available Tools

### Gmail
- `search_emails` → Find emails with filters (sender, subject, unread, date ranges)  
- `send_email` → Send email with subject, body, recipients, and optional attachments  

### Calendar
- `list_events` → List upcoming events with optional date filtering  
- `create_event` → Add a new event (title, time, attendees)  
- `update_event` → Modify an existing event  
- `delete_event` → Remove an event  

### Docs
- `list_docs` → List available Google Docs  
- `create_doc` → Create a new document  
- `read_doc` → Read plain text content from a doc  
- `update_doc` → Insert/append text  
- `delete_doc` → Delete a document  

### Sheets
- `create_sheet` → Create a new spreadsheet  
- `read_sheet` → Read ranges or full sheets (if only sheet name given, returns all values)  
- `write_sheet` → Overwrite cell ranges  
- `append_sheet` → Append rows at the end  

### Drive
- `list_files` → List files in Drive  
- `search_files` → Search Drive by query (e.g., PDFs with name filter)  
- `upload_file` → Upload a local file  
- `download_file` → Download a file by ID  
- `delete_file` → Delete a file  

### Utility
- `ping` → Health check (returns `"pong "`)

---

## 📂 Project Structure

```
mcp-google-workspace/
├── gworkspace.py   # Gmail helpers
├── gcalendar.py    # Calendar helpers
├── gdocs.py        # Docs helpers
├── gsheets.py      # Sheets helpers
├── gdrive.py       # Drive helpers
├── server.py       # MCP server with @tool definitions
├── gspace_auth.py  # OAuth authentication helper
├── secrets/        # OAuth client_secret.json + token.json
└── README.md
```

---

## ⚠️ Security Notes

- Never commit your `secrets/` folder or `.json` files to GitHub.  
- Tokens are cached locally (`secrets/token.json`) for convenience. Delete it if you change scopes or re-auth is required.  
- Use principle of least privilege (only enable scopes you need).  

---

## 📜 License

MIT License – see [LICENSE](LICENSE).
