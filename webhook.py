from flask import Flask, request, jsonify
import json
import random
import datetime

app = Flask(__name__)

# ------------------- Mock Data -------------------
# Sample food items
FOOD_DATABASE = {
    "hot_weather": ["Cold noodles", "Fruit salad", "Iced tea with sandwich"],
    "cold_weather": ["Hot pot", "Kimchi stew", "Ramen"],
    "neutral": ["Bibimbap", "Fried rice", "Grilled chicken"]
}

# ------------------- Load or Save User Data -------------------
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

# ------------------- Main Webhook Route -------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        print("Webhook hit!")

        print("Request headers:", dict(request.headers))
        print("Request content type:", request.content_type)
        print("Raw data:", request.data)
        
        req = request.get_json(force=True)
        print("Request JSON:", req)

        intent = req.get("queryResult", {}).get("intent", {}).get("displayName")
        parameters = req.get("queryResult", {}).get("parameters", {})
        user_id = req.get("originalDetectIntentRequest", {}).get("payload", {}).get("userId", "default")

        # Load user data
        user_data = load_user_data()
        if user_id not in user_data:
            user_data[user_id] = {"history": []}

        # Extract weather and preferences
        weather = parameters.get("weather_type", "neutral")
        preference = parameters.get("food_preference", "")
        recent_meal = parameters.get("recent_meal", "")

        # Filter food based on weather
        food_options = FOOD_DATABASE.get(weather, FOOD_DATABASE["neutral"])

        # Avoid repeating recent meals
        if recent_meal in food_options:
            food_options = [f for f in food_options if f != recent_meal]

        # Randomly select 3 options
        recommendation = random.sample(food_options, min(3, len(food_options)))

        # Save history
        user_data[user_id]["history"].append({
            "time": str(datetime.datetime.now()),
            "recommendation": recommendation
        })
        save_user_data(user_data)

        return jsonify({
            "fulfillmentText": f"Based on the weather, I recommend: {', '.join(recommendation)}"
        }),200

    except Exception as e:
        print("Error:", e)
        return jsonify({
            "fulfillmentText": "Sorry, something went wrong."
        }), 200

if __name__ == "__main__":
    app.run(port=5000)