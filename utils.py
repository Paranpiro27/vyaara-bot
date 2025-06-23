from datetime import datetime

# ==========================
# ⏳ UTILITY FUNCTIONS
# ==========================
def convert_to_24h(time_string):
    """Convert a user-input time like '9am' or '9:30 PM' into 'HH:MM' 24h format."""
    time_string = time_string.strip().lower()
    try:
        # Try common formats
        if ":" in time_string:
            return datetime.strptime(time_string, "%I:%M%p").strftime("%H:%M")  # e.g., 9:30pm
        else:
            return datetime.strptime(time_string, "%I%p").strftime("%H:%M")      # e.g., 9am
    except ValueError:
        return None


def get_current_time():
    """Get the current time in 'HH:MM' 24h format."""
    return datetime.now().strftime("%H:%M")


def is_valid_time_string(time_string):
    """Check if the input is a valid time (9am, 9:30 PM, 18:00, etc.)."""
    if not time_string:
        return False
    patterns = ["%I%p", "%I:%M%p", "%H:%M"]
    for pattern in patterns:
        try:
            datetime.strptime(time_string, pattern)
            return True
        except ValueError:
            continue
    return False


def get_friendly_activity_message(activity_name):
    """Return a warm, human-friendly reminder message for the activity."""
    messages = {
        "study": "📚 Time to focus and study. You're doing great — one page at a time! 🌱",
        "workout": "💪 Time for a workout! Stay strong, stay active — you're making yourself proud! 🌟",
        "meal": "🍳 Don't forget to fuel your body. Enjoy this delicious moment. 🌷",
        "other": "🌱 It's time for your activity — stay present and make it count. 🌞",
    }
    return messages.get(activity_name, f"🌷 It's time for {activity_name}! Enjoy it.")
