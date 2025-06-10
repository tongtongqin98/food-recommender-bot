from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# 食物推荐数据库
food_recommendations = {
    "spicy": {
        "default": ["Kimchi Stew", "Tteokbokki", "Spicy Fried Chicken"],
        "chilli": ["Chilli Ramen", "Chilli Chicken Bowl"],
        "hot": ["Hot Pot", "Spicy Udon"]
    },
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
    phrase = f"{context} You might enjoy {recommendations[0]}"
    if len(recommendations) > 1:
        phrase += f", or maybe {', '.join(recommendations[1:3])}."
    return phrase

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()
    print("Webhook hit!")
    print("Request JSON:", req)

    intent = req.get("queryResult", {}).get("intent", {}).get("displayName", "")
    parameters = req.get("queryResult", {}).get("parameters", {})

    food_pref = parameters.get("food_preference", "").lower()
    weather = parameters.get("weather_type", "").lower()
    delivery = parameters.get("delivery_option", "").lower()
    spicy_type = parameters.get("spicy_type", "").lower()

    response_text = ""

    if intent == "start.recommendation":
        response_text = "Do you have any food preferences? For example: spicy, healthy, rice, pasta, or no preference."

    elif intent == "spicy.preference":
        if spicy_type and spicy_type in food_recommendations["spicy"]:
            response_text = build_response(food_recommendations["spicy"][spicy_type], f"Spicy ({spicy_type}) suggestion 🌶️")
        else:
            response_text = build_response(food_recommendations["spicy"]["default"], "Here’s a spicy suggestion 🌶️")

    elif intent == "healthy.preference":
        response_text = build_response(food_recommendations["healthy"], "Healthy and delicious 🥗")

    elif intent == "no.preference":
        if not food_pref:
            response_text = "Do you have any food preferences? For example: spicy, healthy, rice, pasta, or fast food."
        elif not weather:
            response_text = "What's the weather like? Cold or hot?"
        else:
            if weather == "cold":
                response_text = build_response(food_recommendations["spicy"]["default"], "Cold day? Try these hot dishes 🔥")
            elif weather == "hot":
                response_text = build_response(food_recommendations["cold"], "Hot weather? Try something refreshing ❄️")
            else:
                response_text = build_response(food_recommendations["default"], "Here are some ideas:")

    elif intent in ["rice.preference", "pasta.preference", "fastfood.preference"]:
        key = intent.split(".")[0]  # rice / pasta / fastfood
        if key in food_recommendations:
            response_text = build_response(food_recommendations[key], f"Suggestions for {key} 🍽️")

    elif intent == "choose.delivery" or intent == "choosen.dinein":
        if food_pref in food_recommendations:
            response_text = build_response(food_recommendations[food_pref], f"Here are some {food_pref} dishes:")
        else:
            response_text = build_response(food_recommendations["default"], "Alright! Here are some tasty picks:")

    elif intent == "personalized.recommendation":
        if food_pref in food_recommendations:
            response_text = build_response(food_recommendations[food_pref], f"Tailored pick for {food_pref}:")
        elif weather == "cold":
            response_text = build_response(food_recommendations["spicy"]["default"], "Cold day special 🔥")
        elif weather == "hot":
            response_text = build_response(food_recommendations["cold"], "Cool choices for hot weather ❄️")
        else:
            response_text = build_response(food_recommendations["default"], "How about these:")

    else:
        response_text = "Sorry, I didn’t understand. Can you try again?"

    return jsonify({"fulfillmentText": response_text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
