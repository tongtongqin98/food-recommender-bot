
from flask import Flask, request, jsonify
import os
import random

app = Flask(__name__)

# 食物推荐数据库
food_recommendations = {
    "spicy": ["Kimchi Stew", "Spicy Hot Pot", "Tteokbokki", "Spicy Fried Chicken"],
    "cold": ["Cold Noodles", "Chilled Tofu", "Fresh Salad"],
    "healthy": ["Grilled Salmon", "Quinoa Salad", "Steamed Vegetables", "Tofu Bowl"],
    "rice": ["Bibimbap", "Fried Rice", "Omurice", "Curry Rice"],
    "pasta": ["Spaghetti Bolognese", "Carbonara", "Cream Pasta", "Pesto Pasta"],
    "fastfood": ["Cheeseburger", "Fried Chicken", "French Fries", "Hot Dog"],
    "default": ["Ramen", "Sandwich", "Dumplings", "Donburi"]
}

def build_response(recommendations, context=""):
    if not recommendations:
        return "Hmm... I couldn't find anything tasty right now. 😢"
    picks = random.sample(recommendations, min(3, len(recommendations)))
    phrase = f"{context} You might enjoy {picks[0]}"
    if len(picks) > 1:
        phrase += f", or maybe {', '.join(picks[1:])}."
    return phrase

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()
    print("Webhook hit!")
    print("Request JSON:", req)

    intent = req.get("queryResult", {}).get("intent", {}).get("displayName", "")
    parameters = req.get("queryResult", {}).get("parameters", {})

    food_pref = parameters.get("food_preference", "")
    weather = parameters.get("weather_type", "")
    delivery = parameters.get("delivery_option", "")

    food_pref = food_pref.lower() if food_pref else ""
    weather = weather.lower() if weather else ""
    delivery = delivery.lower() if delivery else ""

    response_text = ""

    if intent == "start.recommendation":
        response_text = "Do you have any food preferences? For example: spicy, healthy, rice, pasta, or no preference."

    elif intent in [
        "spicy.preference", "healthy.preference", "no.preference",
        "rice.preference", "pasta.preference", "fastfood.preference"
    ]:
        if not delivery:
            response_text = "Got it! Do you prefer delivery or dine-in?"
        else:
            if "spicy" in food_pref:
                response_text = build_response(food_recommendations["spicy"], "Here’s a spicy suggestion 🌶️")
            elif "healthy" in food_pref:
                response_text = build_response(food_recommendations["healthy"], "Healthy and delicious 🥗")
            elif "rice" in food_pref:
                response_text = build_response(food_recommendations["rice"], "How about these rice dishes 🍚")
            elif "pasta" in food_pref:
                response_text = build_response(food_recommendations["pasta"], "Pasta lovers might enjoy 🍝")
            elif "fast" in food_pref:
                response_text = build_response(food_recommendations["fastfood"], "Fast and tasty 🍔")
            else:
                response_text = build_response(food_recommendations["default"], "Here are some options 🍽️")

    elif intent in ["choose.delivery", "choosen.dinein"]:
        if "spicy" in food_pref:
            response_text = build_response(food_recommendations["spicy"], "Spicy and convenient! Try these:")
        elif "healthy" in food_pref:
            response_text = build_response(food_recommendations["healthy"], "Healthy options for your choice:")
        elif "rice" in food_pref:
            response_text = build_response(food_recommendations["rice"], "Try these delicious rice meals:")
        elif "pasta" in food_pref:
            response_text = build_response(food_recommendations["pasta"], "Pasta suggestions for you:")
        elif "fast" in food_pref:
            response_text = build_response(food_recommendations["fastfood"], "Fast food for your cravings:")
        else:
            response_text = build_response(food_recommendations["default"], "Alright! Here are some tasty picks:")

    elif intent == "weather.based":
        if weather == "cold":
            response_text = build_response(food_recommendations["spicy"], "It's cold! Warm up with 🔥")
        elif weather == "hot":
            response_text = build_response(food_recommendations["cold"], "Hot weather? Try something refreshing ❄️")
        else:
            response_text = build_response(food_recommendations["default"], "Here are some ideas for today 🍽️")

    elif intent == "personalized.recommendation":
        if not food_pref:
            response_text = "Do you have any food preferences? For example: spicy, healthy, rice, pasta, or fast food."
        elif not weather:
            response_text = "What's the weather like? Cold or hot?"
        else:
            if "spicy" in food_pref:
                response_text = build_response(food_recommendations["spicy"], "Spicy and bold 🌶️")
            elif "healthy" in food_pref:
                response_text = build_response(food_recommendations["healthy"], "Light and healthy 🍃")
            elif "rice" in food_pref:
                response_text = build_response(food_recommendations["rice"], "Here’s something rice-based 🍚")
            elif "pasta" in food_pref:
                response_text = build_response(food_recommendations["pasta"], "Craving pasta? Try these 🍝")
            elif "fast" in food_pref:
                response_text = build_response(food_recommendations["fastfood"], "Quick and delicious 🍟")
            elif weather == "cold":
                response_text = build_response(food_recommendations["spicy"], "Cold day? Try these hot dishes 🔥")
            elif weather == "hot":
                response_text = build_response(food_recommendations["cold"], "Hot weather? Try something refreshing ❄️")
            else:
                response_text = build_response(food_recommendations["default"], "How about these:")

    else:
        response_text = "Sorry, I didn’t understand. Can you try again?"

    print("Replying with:", response_text)
    return jsonify({"fulfillmentText": response_text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
