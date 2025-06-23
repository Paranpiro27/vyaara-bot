import json
import os
from datetime import datetime, timedelta

DB_FILE = "database.json"

def load_data():
    """Load user data from the JSON database."""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_data(data):
    """Save user data to the JSON database."""
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def initialize_user(user_id):
    """Ensure a user record exists; create if missing."""
    data = load_data()
    user_id = str(user_id)
    if user_id not in data:
        data[user_id] = {
            "name": None,
            "goals": [],
            "activities": {},
            "sleep_time": None,
            "wake_time": None,
            "last_active_date": None,
            "streak_count": 0,
            "milestones": {
                "conversations": 0,
                "start_date": datetime.now().strftime("%Y-%m-%d"),
                "custom_dates": [],
                "custom_conversations": []
            },
            "mood": None
        }
        save_data(data)

def set_user_name(user_id, name):
    data = load_data()
    initialize_user(user_id)
    data[str(user_id)]["name"] = name
    save_data(data)

def add_user_goal(user_id, goal):
    data = load_data()
    initialize_user(user_id)
    data[str(user_id)]["goals"].append(goal)
    save_data(data)

def save_user_activities(user_id, activities):
    data = load_data()
    initialize_user(user_id)
    data[str(user_id)]["activities"] = activities
    save_data(data)

def update_user_streak(user_id):
    data = load_data()
    initialize_user(user_id)
    user_data = data[str(user_id)]
    today = datetime.now().date()
    last_active = user_data.get("last_active_date")

    if last_active:
        last_date = datetime.strptime(last_active, "%Y-%m-%d").date()
        if today == last_date:
            return user_data["streak_count"]
        elif today == last_date + timedelta(days=1):
            user_data["streak_count"] += 1
        else:
            user_data["streak_count"] = 1
    else:
        user_data["streak_count"] = 1

    user_data["last_active_date"] = today.strftime("%Y-%m-%d")
    save_data(data)
    return user_data["streak_count"]

def get_user_data(user_id):
    data = load_data()
    initialize_user(user_id)
    return data[str(user_id)]

def get_all_user_ids():
    data = load_data()
    return list(data.keys())

def get_user_milestones(user_id):
    user_data = get_user_data(user_id)
    milestones = user_data.get("milestones", {})
    convos = milestones.get("conversations", 0)
    start_date = milestones.get("start_date", datetime.now().strftime("%Y-%m-%d"))
    days_since_start = (datetime.now() - datetime.strptime(start_date, "%Y-%m-%d")).days
    return {
        "conversations": convos,
        "days_since_start": days_since_start,
        "custom_dates": milestones.get("custom_dates", []),
        "custom_conversations": milestones.get("custom_conversations", [])
    }
