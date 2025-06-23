import re

# ==========================
# 🎤 TONE ANALYSIS UTILITY
# ==========================
def analyze_tone(message: str) -> str:
    """Analyze the emotional tone of the user's message."""
    msg = message.lower().strip()

    sad_words = ["sad", "down", "depressed", "unhappy", "crying", "overwhelmed", "low"]
    happy_words = ["happy", "excited", "amazing", "fantastic", "good", "joyful", "grateful", "peaceful", "motivated"]
    tired_words = ["tired", "sleepy", "exhausted", "drained", "burnt out", "no energy"]
    angry_words = ["angry", "mad", "furious", "irritated", "frustrated", "annoyed", "enraged"]
    lonely_words = ["lonely", "alone", "isolated", "no one understands", "no one to talk to"]

    if any(word in msg for word in sad_words):
        return "sad"
    elif any(word in msg for word in happy_words):
        return "happy"
    elif any(word in msg for word in tired_words):
        return "tired"
    elif any(word in msg for word in angry_words):
        return "angry"
    elif any(word in msg for word in lonely_words):
        return "lonely"

    return "neutral"


def get_tone_emoji(tone: str) -> str:
    """Return an emoji that best suits the detected tone."""
    emojis = {
        "happy": "🌞",
        "sad": "😞",
        "tired": "🌙",
        "angry": "🔥",
        "lonely": "🌷",
        "neutral": "🌱",
    }
    return emojis.get(tone, "🌷")


def get_tone_based_confirmation_message(tone: str) -> str:
    """Check with the user if we've detected their emotion correctly."""
    confirmations = {
        "happy": "🌞 I sense you’re feeling happy — am I right?",
        "sad": "😞 It seems like you’re feeling a bit down — am I right?",
        "tired": "🌙 You seem tired. Do you want to talk about it?",
        "angry": "🔥 It looks like you’re feeling frustrated or angry — am I right?",
        "lonely": "🌷 It feels like you’re feeling a bit lonely — am I right?",
        "neutral": "🌱 I’m here for you. Do you want to talk more about how you’re feeling?",
    }
    return confirmations.get(tone, "🌷 Do you want to tell me how you’re feeling?")


def get_tone_based_message(tone: str) -> str:
    """Return a warm, supportive reply based on the detected emotion."""
    messages = {
        "happy": "🌞 That’s beautiful to hear! Let’s make this moment even brighter together.",
        "sad": "🌷 I’m really sorry you’re feeling this way. You’re not alone, and brighter moments will come. 💙 Do you want to tell me why you’re feeling this way?",
        "tired": "🌙 It sounds like you’ve been carrying a lot. Remember, rest is vital for strength. Would you like a quick breathing exercise or a moment to slow down? 🌱",
        "angry": "🔥 It’s okay to be frustrated. You’re heard, and your feelings matter. Would you like to tell me what happened? 💙",
        "lonely": "🌷 Feeling lonely is one of the heaviest feelings to bear. You’re not alone, and I’m here with you. Would you like to share more about it? 🌱",
        "neutral": "🌱 Thanks for sharing. I’m here to listen if you’d like to say more.",
    }
    return messages.get(tone, "🌷 I’m here for you — always. 🌱")


# ==========================
# 🌷 NEXT STEP:
# ==========================
# In your bot.py, when you call the tone analysis:
# 1. Analyze the user’s message
# 2. Ask for confirmation ("I sense you're feeling X, am I right?")
# 3. If confirmed, send the supportive reply.
#
# This allows a more human-like, empathetic conversation flow.
