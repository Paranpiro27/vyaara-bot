import asyncio
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from telegram import Bot
from database import load_data

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
    raise ValueError("❌ TELEGRAM_TOKEN is not defined in .env.")

bot = Bot(token=TELEGRAM_TOKEN)

# ==========================
# 📤 SEND MESSAGE UTILITY
# ==========================
async def send_message(chat_id, text):
    try:
        await bot.send_message(chat_id=chat_id, text=text)
    except Exception as e:
        logger.error(f"❌ Could not send message to {chat_id}: {e}")

# ==========================
# ☀️ GREETINGS
# ==========================
async def send_good_morning(user_id, chat_id):
    await send_message(chat_id, "☀️ Good morning! 🌷 Let’s make this day beautiful and productive. You're strong and capable!")

async def send_good_night(user_id, chat_id):
    await send_message(chat_id, "🌙 Good night! 😴 You’ve worked hard today. Remember, rest is vital for a brighter tomorrow. 🌱 Sweet dreams!")

# ==========================
# ⏰ ACTIVITY REMINDERS
# ==========================
async def send_activity_reminders(user_id, chat_id, activities):
    now = datetime.now().strftime("%H:%M")
    for activity, activity_time in activities.items():
        if now == activity_time:
            await send_message(chat_id, f"🌷 It's time for {activity}! Stay focused and enjoy it.")

# ==========================
# 🔄 MAIN SCHEDULER LOGIC
# ==========================
async def run_scheduler():
    data = load_data()
    for user_id, user_data in data.items():
        chat_id = user_id
        sleep_time = user_data.get("sleep_time")
        wake_time = user_data.get("wake_time")
        activities = user_data.get("activities", {})

        now = datetime.now().strftime("%H:%M")
        if wake_time == now:
            await send_good_morning(user_id, chat_id)
        if sleep_time == now:
            await send_good_night(user_id, chat_id)

        await send_activity_reminders(user_id, chat_id, activities)

# ==========================
# 🕰️ SCHEDULER LOOP
# ==========================
def start_scheduler():
    async def scheduler_loop():
        while True:
            await run_scheduler()
            await asyncio.sleep(60)
    asyncio.run(scheduler_loop())
