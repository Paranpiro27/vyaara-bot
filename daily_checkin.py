import os
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv
from telegram import Bot
from database import get_all_user_ids, get_user_data

# ==========================
# ⚙️ CONFIGURE LOGGING
# ==========================
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ==========================
# 🌍 LOAD ENV
# ==========================
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN is NOT defined in .env.")
bot = Bot(token=TELEGRAM_TOKEN)

# ==========================
# 💙 DAILY CHECK-IN MESSAGES
# ==========================
CHECKIN_MESSAGES = [
    "🌱 Just checking in — drink some water and take a deep breath! 💙",
    "☕ You're doing great today. I’m proud of you.",
    "🌺 Remember: Every step you take counts.",
    "🌅 Take a moment to acknowledge one thing you're grateful for.",
    "🌷 You matter. Whatever you're feeling is okay.",
    "🌳 Stay grounded and present. You’re growing every day.",
]

# ==========================
# ⏳ SEND DAILY CHECK-INS
# ==========================
async def send_check_in_message(chat_id, text):
    """Send a daily check-in message with warmth and care."""
    try:
        await bot.send_message(chat_id=chat_id, text=text)
        logger.info(f"✅ Sent daily check-in to {chat_id}")
    except Exception as e:
        logger.error(f"❌ Could not send check-in to {chat_id}: {e}")

# ==========================
# 🎯 MAIN FUNCTION
# ==========================
async def send_daily_check_ins():
    """Send daily check-in messages to all registered user ids."""
    ids = get_all_user_ids()
    for chat_id in ids:
        user_data = get_user_data(chat_id)

        sentiment = user_data.get("last_sentiment", "neutral").lower() if user_data else "neutral"

        if sentiment in ["negative", "sad", "lonely", "tired", "depressed"]:
            text = (
                "💙 It's okay to have hard days. Remember, you’re not alone — you matter and you’re loved. 🌷\n"
                "If you’d like, I’m here to listen, or we can try a quick relaxation exercise together. 🌱"
            )
        elif sentiment in ["positive", "happy", "excited"]:
            text = (
                "🌷 You’re doing so well! Keep nurturing yourself and sharing that beautiful energy. 🌞\n"
                "I’m proud of every step you’re taking. 🌱"
            )
        else:
            text = CHECKIN_MESSAGES[datetime.now().day % len(CHECKIN_MESSAGES)]

        await send_check_in_message(chat_id, text)

# ==========================
# ⚡ TESTING LOOP
# ==========================
if __name__ == '__main__':
    """Run daily_checkin.py standalone for testing."""
    async def main():
        await send_daily_check_ins()
    asyncio.run(main())
