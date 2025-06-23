import re
from langdetect import detect, LangDetectException
from openai import OpenAIError

# ==========================
# 🌎 LANGUAGE + TONE UTILS
# ==========================

GENZ_HINGLISH_SLANG = {
    "hn", "hm", "yup", "lmao", "lol", "brb", "idk", "omg", "wassup",
    "kya", "kyu", "mene", "kaha", "shi", "acha", "nahi", "thik", "ha", "haan", "ok", "okay"
}

def detect_user_language(text):
    try:
        # If slang or Hinglish-like words present, force English
        words = set(re.findall(r'\b\w+\b', text.lower()))
        if words & GENZ_HINGLISH_SLANG:
            return "en"

        detected = detect(text)
        # If detected language is not en or hi and text is short, fallback to English
        if detected not in ["en", "hi"] and len(text.split()) <= 5:
            return "en"
        return detected
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
# 💡 AI PROMPT BUILDERS
# ==========================

def build_professional_prompt(text, lang):
    return (
        f"You are a knowledgeable and friendly AI mentor.\n"
        f"Reply in this language: {lang}.\n\n"
        f"👉 Be long and detailed (15-20 sentences).\n"
        f"👉 Use clear line spacing.\n"
        f"👉 Include bullets (•), arrows (→), numbered lists where helpful.\n"
        f"👉 Add suitable emojis to make the reply lively.\n"
        f"👉 Provide practical steps, examples, and actionable tips.\n"
        f"👉 Avoid generic advice, make it specific and engaging.\n"
        f"👉 Format like ChatGPT: clear, friendly, easy to read.\n\n"
        f"The user said: {text}"
    )

def build_casual_prompt(text, lang):
    return (
        f"You are a sweet, kind AI friend.\n"
        f"Reply in this language: {lang}.\n\n"
        f"👉 Keep it short and warm (2-4 sentences).\n"
        f"👉 Add friendly emojis.\n"
        f"👉 Add a reflection line like '🌱 How does that feel to you?' if emotional words detected.\n\n"
        f"The user said: {text}"
    )

# ==========================
# 🧹 CLEAN REPLY
# ==========================

def clean_reply(text):
    # Remove unwanted prefixes like sw, sk, fi, id at start of lines
    cleaned = re.sub(r"(?m)^\s*(sw|sk|fi|id)[:!.,]*\s*", "", text)
    # Remove isolated occurrences anywhere
    cleaned = re.sub(r"\b(sw|sk|fi|id)\b", "", cleaned)
    # Remove extra spaces
    cleaned = re.sub(r" +", " ", cleaned)
    return cleaned.strip()

# ==========================
# 🌟 ROUTING REPLY
# ==========================

def route_message(client, text):
    lang = detect_user_language(text)

    if is_professional_query(text):
        pro_prompt = build_professional_prompt(text, lang)
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": pro_prompt}],
                temperature=0.9,
                max_tokens=3000
            )
            return clean_reply(response.choices[0].message.content.strip())
        except OpenAIError as e:
            return f"⚡ OpenAI error: {e}"
        except Exception as e:
            return f"❗ Unexpected error: {e}"

    casual_prompt = build_casual_prompt(text, lang)
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": casual_prompt}],
            temperature=0.9,
            max_tokens=500
        )
        reply = response.choices[0].message.content.strip()
        return clean_reply(reply) + " " + get_mood_emoji(text)
    except OpenAIError as e:
        return f"⚡ OpenAI error: {e}"
    except Exception as e:
        return f"❗ Unexpected error: {e}"
