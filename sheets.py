import os
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
from datetime import datetime

# 🌿 Load environment variables
load_dotenv()

# 📁 Load config values from .env
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")  # e.g. path/to/credentials.json
SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME", "Vyaara Journal")
SHEET_NAME = os.getenv("SHEET_NAME", "Sheet1")

# 🔐 Authenticate with Google Sheets
creds = Credentials.from_service_account_file(
    GOOGLE_CREDENTIALS_JSON,
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive",
    ]
)
client = gspread.authorize(creds)

# 📘 Access the right sheet
sheet = client.open(SPREADSHEET_NAME).worksheet(SHEET_NAME)

# 💾 Save a new message row (with optional emoji parsing/sentiment)
def save_message(date, user_id, message, sentiment="neutral"):
    """Append a journal entry to Google Sheets."""
    try:
        sheet.append_row([date, str(user_id), message, sentiment])
    except Exception as e:
        print(f"❌ Failed to save message for {user_id}: {e}")

# 📥 Get all unique user IDs
def get_all_user_ids():
    """Fetch unique user IDs from the sheet."""
    ids = set()
    try:
        records = sheet.get_all_records()
        for record in records:
            user_id = str(record.get("User Id") or record.get("User ID") or "").strip()
            if user_id:
                ids.add(user_id)
    except Exception as e:
        print(f"❌ Failed to fetch user IDs: {e}")
    return list(ids)

# 🧪 Test mode
if __name__ == "__main__":
    test_ids = get_all_user_ids()
    if test_ids:
        print(f"✅ Found {len(test_ids)} user(s): {test_ids}")
    else:
        print("⚠️ No user IDs found. Please check your sheet setup.")
