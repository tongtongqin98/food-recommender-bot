# user_data.py
import os
import json

USER_DATA_FILE = "user_data.json"

def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_user_data(data):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_recent_meals(user_id):
    data = load_user_data()
    return data.get(user_id, [])

def add_recent_meal(user_id, meal):
    data = load_user_data()
    meals = data.get(user_id, [])
    if meal not in meals:
        meals.append(meal)
    data[user_id] = meals[-5:]  # 只保留最近5个
    save_user_data(data)
