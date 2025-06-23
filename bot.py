import os
import re
import json
import asyncio
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from langdetect import detect, LangDetectException
from openai import OpenAI, OpenAIError

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
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN is not defined in .env.")
if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY is not defined in .env.")

bot = Bot(token=TELEGRAM_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

DB_FILE = "database.json"
user_emotion_state = {}

# ==========================
# 🌱 DATABASE UTILS
# ==========================
def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def initialize_user(user_id):
    data = load_data()
    if str(user_id) not in data:
        data[str(user_id)] = {
            "name": None,
            "goals": [],
            "activities": {},
            "sleep_time": None,
            "wake_time": None,
            "last_active_date": None,
            "streak_count": 0
        }
        save_data(data)

def save_user_activities(user_id, activities):
    data = load_data()
    initialize_user(user_id)
    data[str(user_id)]["activities"] = activities
    save_data(data)

def get_user_data(user_id):
    data = load_data()
    initialize_user(user_id)
    return data[str(user_id)]

# ==========================
# 🌎 LANGUAGE + TONE UTILS
# ==========================
GENZ_HINGLISH_SLANG = {
    "hn", "hm", "yup", "lmao", "lol", "brb", "idk", "omg",
    "kya", "kyu", "mene", "kaha", "shi", "acha", "nahi", "thik", "ha", "haan", "ok", "okay"
}

def detect_user_language(text):
    words = set(text.lower().split())
    if words & GENZ_HINGLISH_SLANG:
        return "en"
    try:
        detected_lang = detect(text)
        if detected_lang not in ["en", "hi"]:  # Force fallback to English for short/slang text
            return "en"
        return detected_lang
    except LangDetectException:
        return "en"

def is_professional_query(text):
    return bool(re.search(
        r'\b(business|career|startup|project|plan|goal|strategy|job|internship|company)\b',
        text.lower()
    ))

def get_mood_emoji(text):
    text = text.lower()
    if any(word in text for word in ["sad", "depressed", "cry"]):
        return "🌧️"
    if any(word in text for word in ["happy", "excited", "good"]):
        return "🌷"
    return "😊"

# ==========================
# 💡 AI REPLIES
# ==========================
def get_ai_reply(prompt, lang="en", max_tokens=1000):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()
    except OpenAIError as e:
        return f"⚡️ OpenAI error: {e}"
    except Exception as e:
        return f"❗ Unexpected error: {e}"

def route_message(text):
    lang = detect_user_language(text)
    if is_professional_query(text):
        pro_prompt = (
            f"You are a knowledgeable and friendly AI mentor.\n"
            f"Reply in this language: {lang}.\n"
            f"👉 Be long, detailed (15-20 sentences), clear line spacing, bullets, arrows, emojis.\n"
            f"👉 Provide practical steps, examples, tips, no generic advice.\n"
            f"👉 Format like ChatGPT: easy to read, no dense text walls.\n"
            f"The user said: {text}"
        )
        return get_ai_reply(pro_prompt, lang, max_tokens=3000)
    casual_prompt = (
        f"You are a sweet, kind AI friend.\n"
        f"Reply in this language: {lang}.\n"
        f"👉 Short, friendly (2-4 sentences), with emojis.\n"
        f"👉 Add '🌱 How does that feel to you?' if emotional words detected.\n"
        f"The user said: {text}"
    )
    reply = get_ai_reply(casual_prompt, lang, max_tokens=500)
    return reply + " " + get_mood_emoji(text)

# ==========================
# 🧹 CLEAN REPLY
# ==========================
def clean_reply(text):
    cleaned = re.sub(r"(?m)^\s*(sw|sk|fi|id)[:!.,]*\s*", "", text)
    cleaned = re.sub(r"\b(sw|sk|fi|id)\b", "", cleaned)
    cleaned = re.sub(r" +", " ", cleaned)
    return cleaned.strip()

# ==========================
# 🤖 TELEGRAM HANDLERS
# ==========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.chat_id)
    initialize_user(user_id)
    await update.message.reply_text(
        "👋 *Welcome to Vyaara!* 🌷\n\nI’m your AI companion — your guide, mentor, teacher, and friend! 🌞\n\n"
        "🌟 I can help you:\n"
        "✅ Build habits & track daily activities\n"
        "✅ Stay motivated with milestones & celebrations\n"
        "✅ Understand and respond to your emotions\n"
        "✅ Guide you through journaling & reflection\n"
        "✅ Be your safe space when you’re feeling low\n\n"
        "🌷 What’s your name?",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.strip()
    user_id = str(update.message.chat_id)
    initialize_user(user_id)

    if any(greet in user_message.lower() for greet in ["hi", "hello", "hey", "wassup"]):
        await start(update, context)
        return

    if any(keyword in user_message.lower() for keyword in ["study at", "workout at", "meal at", "other at"]):
        activities = {}
        patterns = {
            "study": r"study at (\d{1,2}(:\d{2})? ?(am|pm)?)",
            "workout": r"workout at (\d{1,2}(:\d{2})? ?(am|pm)?)",
            "meal": r"meal at (\d{1,2}(:\d{2})? ?(am|pm)?)",
            "other": r"other at (\d{1,2}(:\d{2})? ?(am|pm)?)",
        }
        for act, pat in patterns.items():
            match = re.search(pat, user_message, re.IGNORECASE)
            if match:
                time_str = match.group(1)
                try:
                    activities[act] = datetime.strptime(time_str, "%I:%M %p").strftime("%H:%M")
                except:
                    activities[act] = datetime.strptime(time_str, "%I %p").strftime("%H:%M")
        save_user_activities(user_id, activities)
        await update.message.reply_text("✅ Your daily routine is saved. 🌷 I'll send you gentle reminders!")
        return

    reply = route_message(user_message)
    reply = clean_reply(reply)
    await update.message.reply_text(reply, parse_mode="Markdown")

# ==========================
# 🚀 RUN BOT
# ==========================
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("✅ Vyaara bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
