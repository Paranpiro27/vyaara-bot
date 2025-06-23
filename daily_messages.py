import os
import asyncio
import logging
import random
from dotenv import load_dotenv
from telegram import Bot
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ==========================
# ⚙️ CONFIGURE LOGGING
# ==========================
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ==========================
# 🌍 LOAD ENVIRONMENT
# ==========================
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")
SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME")
SHEET_NAME = os.getenv("SHEET_NAME", "Sheet1")

if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN is NOT defined in .env.")

# ==========================
# ⚡️ AUTHENTICATE WITH GOOGLE SHEETS
# ==========================
creds = Credentials.from_service_account_file(
    GOOGLE_CREDENTIALS_JSON,
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive",
    ]
)

client = gspread.authorize(creds)
sheet = client.open(SPREADSHEET_NAME).worksheet(SHEET_NAME)

# ==========================
# 👥 GET ALL USER IDS
# ==========================
def get_all_user_ids():
    """Retrieve unique user ids from the sheet."""
    records = sheet.get_all_records()
    ids = {str(record.get("User ID")) for record in records if record.get("User ID")}
    return ids

# ==========================
# 🌅 MESSAGE TEMPLATES
# ==========================
GOOD_MORNING_MESSAGES = [
    "☀️ Good morning! 🌷 Today is a fresh canvas. Whatever you create, make it beautiful.",
    "🌅 A new day is here, and so are new possibilities. Stay hopeful and strong! 🌱",
    "☕️ Good morning! Remember: The sun shines for you, and so do I. 🌷",
]

GOOD_NIGHT_MESSAGES = [
    "🌙 Good night, beautiful soul. 🌷 Rest well — tomorrow is a new chapter, and you deserve it.",
    "🌷 It's okay to slow down and rest. You're doing your best, and that's enough. 🌙",
    "🌅 The stars are shining for you tonight. Let them guide you to peace and rest. 🌷",
]

# ==========================
# ⚡ SEND MESSAGE
# ==========================
async def send_message(bot, chat_id, text):
    """Send a message via the bot."""
    try:
        await bot.send_message(chat_id=chat_id, text=text)
    except Exception as e:
        logger.error(f"❌ Could not send message to {chat_id}: {e}")

# ==========================
# 🌅 GOOD MORNING
# ==========================
async def send_good_morning(bot):
    """Send a warm morning message to all registered ids."""
    ids = get_all_user_ids()
    for chat_id in ids:
        try:
            chat_id_int = int(chat_id)
            message = random.choice(GOOD_MORNING_MESSAGES)
            await send_message(bot, chat_id_int, message)
        except ValueError:
            logger.warning(f"❌ Skipped invalid Chat ID (Not an integer): {chat_id}")

# ==========================
# 🌙 GOOD NIGHT
# ==========================
async def send_good_night(bot):
    """Send a warm night message to all registered ids."""
    ids = get_all_user_ids()
    for chat_id in ids:
        try:
            chat_id_int = int(chat_id)
            message = random.choice(GOOD_NIGHT_MESSAGES)
            await send_message(bot, chat_id_int, message)
        except ValueError:
            logger.warning(f"❌ Skipped invalid Chat ID (Not an integer): {chat_id}")

# ==========================
# ⚡ MAIN FUNCTION
# ==========================
if __name__ == '__main__':
    """Run as a standalone script for manual testing."""
    async def main():
        bot = Bot(token=TELEGRAM_TOKEN)
        logger.info("🌅 Testing both messages now...")
        ids = get_all_user_ids()
        logger.info(f"👥 IDs found: {ids}")

        await send_good_morning(bot)
        await send_good_night(bot)

    asyncio.run(main())
