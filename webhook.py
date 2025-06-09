from flask import Flask, request, jsonify
import json
import random
import datetime
import os

app = Flask(__name__)

# ------------------- Enhanced Food Data -------------------
FOOD_ITEMS = [
    {"name": "Cold noodles", "weather": "hot", "type": "spicy", "goal": "light"},
    {"name": "Fruit salad", "weather": "hot", "type": "sweet", "goal": "light"},
    {"name": "Iced tea with sandwich", "weather": "hot", "type": "neutral", "goal": "light"},
    {"name": "Hot pot", "weather": "cold", "type": "spicy", "goal": "warm"},
    {"name": "Kimchi stew", "weather": "cold", "type": "spicy", "goal": "warm"},
    {"name": "Ramen", "weather": "cold", "type": "salty", "goal": "warm"},
    {"name": "Bibimbap", "weather": "neutral", "type": "spicy", "goal": "balance"},
    {"name": "Fried rice", "weather": "neutral", "type": "salty", "goal": "energy"},
    {"name": "Grilled chicken", "weather": "neutral", "type": "protein", "goal": "muscle"}
]

USER_DATA_FILE = "user_data.json"

# ------------------- Load or Save User Data -------------------
def load_user_data():
    try:
        with open(USER_DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_user_data(data):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ------------------- Scoring-based Recommendation -------------------
def score_food(item, preference, goal):
    score = 0
    if preference and preference.lower() in item["type"]:
        score += 2
    if goal and goal.lower() in item["goal"]:
        score += 1
    return score

# ------------------- Main Webhook Route -------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        print("Webhook hit!")
        req = request.get_json(force=True)
        print("Request JSON:", req)

        intent = req.get("queryResult", {}).get("intent", {}).get("displayName")
        parameters = req.get("queryResult", {}).get("parameters", {})
        user_id = req.get("originalDetectIntentRequest", {}).get("payload", {}).get("userId", "default")

        user_data = load_user_data()
        if user_id not in user_data:
            user_data[user_id] = {"history": []}

        weather = parameters.get("weather_type", "neutral")
        preference = parameters.get("food_preference", "")
        goal = parameters.get("health_goal", "")
        recent_meal = parameters.get("recent_meal", "")

        # Filter and score food
        filtered = [f for f in FOOD_ITEMS if f["weather"] == weather]
        scored = sorted(filtered, key=lambda x: score_food(x, preference, goal), reverse=True)

        # Avoid recently eaten food
        recommendations = [f["name"] for f in scored if f["name"] != recent_meal]
        final_recommend = recommendations[:3] if recommendations else ["Bibimbap"]

        # Save history
        user_data[user_id]["history"].append({
            "time": str(datetime.datetime.now()),
            "recommendation": final_recommend
        })
        save_user_data(user_data)

        return jsonify({
            "fulfillmentText": f"Based on your preferences, I recommend: {', '.join(final_recommend)}"
        }), 200

    except Exception as e:
        print("Error occurred:", e)
        return jsonify({
            "fulfillmentText": "Sorry, an error occurred in the backend."
        }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
