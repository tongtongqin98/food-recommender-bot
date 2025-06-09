from flask import Flask, request, jsonify
import json
import random
import datetime
import os

app = Flask(__name__)

# ------------------- Enhanced Food Data -------------------
FOOD_ITEMS = [
    {
        "name": "Cold noodles",
        "weather": ["hot"],
        "type": ["spicy", "light"],
        "goal": ["light"],
        "time": ["lunch", "dinner"],
        "calories": 350
    },
    {
        "name": "Fruit salad",
        "weather": ["hot"],
        "type": ["sweet", "light"],
        "goal": ["lose weight"],
        "time": ["breakfast", "lunch"],
        "calories": 250
    },
    {
        "name": "Iced tofu soup",
        "weather": ["hot"],
        "type": ["salty"],
        "goal": ["light"],
        "time": ["lunch"],
        "calories": 300
    },
    {
        "name": "Kimchi stew",
        "weather": ["cold"],
        "type": ["spicy"],
        "goal": ["warm"],
        "time": ["dinner"],
        "calories": 500
    },
    {
        "name": "Ramen",
        "weather": ["cold"],
        "type": ["salty"],
        "goal": ["warm", "energy"],
        "time": ["lunch", "dinner"],
        "calories": 650
    },
    {
        "name": "Grilled salmon",
        "weather": ["neutral", "cold"],
        "type": ["protein", "salty"],
        "goal": ["muscle"],
        "time": ["lunch", "dinner"],
        "calories": 480
    },
    {
        "name": "Bibimbap",
        "weather": ["neutral"],
        "type": ["spicy", "rice"],
        "goal": ["balance"],
        "time": ["lunch", "dinner"],
        "calories": 550
    },
    {
        "name": "Avocado toast",
        "weather": ["neutral", "hot"],
        "type": ["light", "vegetarian"],
        "goal": ["healthy", "lose weight"],
        "time": ["breakfast"],
        "calories": 300
    },
    {
        "name": "Chicken breast with broccoli",
        "weather": ["neutral", "cold"],
        "type": ["protein"],
        "goal": ["muscle", "healthy"],
        "time": ["lunch", "dinner"],
        "calories": 400
    },
    {
        "name": "Sweet and sour pork",
        "weather": ["neutral"],
        "type": ["sweet", "meat"],
        "goal": ["energy"],
        "time": ["dinner"],
        "calories": 700
    }
]

USER_DATA_FILE = "user_data.json"

def load_user_data():
    try:
        with open(USER_DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_user_data(data):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def score_food(item, weather, preference, goal, time):
    score = 0
    if weather and weather in item["weather"]:
        score += 1
    if preference:
        score += 2 if preference in item["type"] else 0
    if goal:
        score += 2 if goal in item["goal"] else 0
    if time:
        score += 1 if time in item["time"] else 0
    if item["calories"] <= 600:
        score += 1
    return score

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
        time = parameters.get("meal_time", "lunch")

        scored_items = [
            (item, score_food(item, weather, preference, goal, time))
            for item in FOOD_ITEMS
            if item["name"] != recent_meal
        ]

        top_items = sorted(scored_items, key=lambda x: x[1], reverse=True)[:3]
        names = [item["name"] for item in top_items]

        user_data[user_id]["history"].append({
            "time": str(datetime.datetime.now()),
            "recommendation": names
        })
        save_user_data(user_data)

        response_text = f"Based on your preferences, I recommend: {', '.join(names)}."
        return jsonify({"fulfillmentText": response_text}), 200

    except Exception as e:
        print("Error occurred:", e)
        return jsonify({
            "fulfillmentText": "Sorry, an error occurred in the backend."
        }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
