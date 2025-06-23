import os
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv
from telegram import Bot
from database import get_all_user_ids, get_user_data, get_user_milestones

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
if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN is NOT defined in .env.")
bot = Bot(token=TELEGRAM_TOKEN)

# ==========================
# 🎉 DEFAULT MILESTONE MESSAGES
# ==========================
DEFAULT_MILESTONES = {
    7: ("🌷 It's been 1 week, {name}! Thanks for sharing this space with me. 🌱 You're growing every day!"),
    30: ("🌳 It's been a whole month, {name}! 🌈 I'm so proud of your resilience and warmth. Keep going!"),
    100: ("🌟 100 days together, {name}! What a beautiful milestone. 🌺 Stay strong and hopeful — I'm with you!"),
}

BADGES = {
    7: ("🏅", None),    # You can add custom sticker files
    30: ("🌳", None),
    100: ("🌟", None),
}

# ==========================
# ⚡ SEND MILESTONE MESSAGE
# ==========================
async def send_milestone_message(chat_id: str, text: str, sticker_id: str = None) -> None:
    """Send milestone text and optional sticker to the user."""
    try:
        await bot.send_message(chat_id=chat_id, text=text)
        logger.info(f"✅ Sent milestone text to {chat_id}")

        if sticker_id:
            await bot.send_sticker(chat_id=chat_id, sticker=sticker_id)
            logger.info(f"✅ Sent milestone sticker to {chat_id}")

    except Exception as e:
        logger.error(f"❌ Could not send milestone message to {chat_id}: {e}")

# ==========================
# 🎯 GENERATE MILESTONE MESSAGE
# ==========================
def milestone_message(days_since_joined: int, user_name: str, user_milestones: dict) -> (str, str):
    """Return a milestone message and sticker if applicable."""
    available_dates = user_milestones.get("custom_dates", [])
    available_conversations = user_milestones.get("custom_conversations", [])

    milestones = set(DEFAULT_MILESTONES.keys())
    for milestone in milestones:
        if days_since_joined == milestone:
            text_template = DEFAULT_MILESTONES.get(milestone) or "🌷 {name}, we've hit a special milestone: {milestone}! 🌟"
            text = text_template.format(name=user_name, milestone=milestone)
            sticker_id = BADGES.get(milestone, (None, None))[1]
            return text, sticker_id

    return None, None

# ==========================
# 🎉 MAIN ENTRYPOINT
# ==========================
async def send_milestones():
    """Check user milestones and send celebratory messages."""
    ids = get_all_user_ids()
    for chat_id in ids:
        user_data = get_user_data(chat_id)

        if user_data:
            user_name = user_data.get("name", "")
            milestones = get_user_milestones(chat_id)

            days_since_joined = milestones.get("days_since_start", 0)

            text, sticker_id = milestone_message(days_since_joined, user_name, user_data.get("milestones", {}))

            if text:
                await send_milestone_message(chat_id, text, sticker_id)

# ==========================
# ⚡ TESTING
# ==========================
if __name__ == '__main__':
    """Run milestone.py standalone for testing."""
    async def main():
        await send_milestones()
    asyncio.run(main())
