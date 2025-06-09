
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# 食物推荐数据库
food_recommendations = {
    "spicy": ["Kimchi Stew", "Spicy Hot Pot", "Tteokbokki", "Spicy Fried Chicken"],
    "cold": ["Cold Noodles", "Chilled Tofu", "Fresh Salad"],
    "healthy": ["Grilled Salmon", "Quinoa Salad", "Steamed Vegetables", "Tofu Bowl"],
    "default": ["Bibimbap", "Fried Rice", "Ramen", "Sandwich"]
}

# 自然推荐语构建
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
    delivery = parameters.get("delivery_option", "").lower()  # 例如 delivery / dine-in

    response_text = ""

    if intent == "start.recommendation":
        response_text = "Do you have any food preferences? For example: spicy, healthy, or no preference."

    elif intent in ["spicy.preference", "healthy.preference", "no.preference"]:
        # 没有 delivery 信息时继续追问
        if not delivery:
            response_text = "Do you prefer delivery or dine-in?"
        else:
            if "spicy" in food_pref:
                response_text = build_response(food_recommendations["spicy"], "Here’s a spicy suggestion 🌶️")
            elif "healthy" in food_pref:
                response_text = build_response(food_recommendations["healthy"], "Here’s something healthy 🥗")
            else:
                response_text = build_response(food_recommendations["default"], "Here are some popular picks 🍴")

    elif intent in ["choose.delivery", "choosen.dinein"]:
        if "spicy" in food_pref:
            response_text = build_response(food_recommendations["spicy"], "Spicy and convenient! Try these:")
        elif "healthy" in food_pref:
            response_text = build_response(food_recommendations["healthy"], "Healthy options for your choice:")
        else:
            response_text = build_response(food_recommendations["default"], "Alright! Here are some tasty picks:")

    elif intent == "personalized.recommendation":
        # 多参数推荐逻辑
        if not food_pref:
            response_text = "Do you have any food preferences? For example: spicy, healthy, or no preference."
        elif not weather:
            response_text = "What's the weather like? Cold or hot?"
        else:
            if "spicy" in food_pref:
                response_text = build_response(food_recommendations["spicy"], "Spicy and bold 🌶️")
            elif "healthy" in food_pref:
                response_text = build_response(food_recommendations["healthy"], "Light and healthy 🍃")
            elif weather == "cold":
                response_text = build_response(food_recommendations["spicy"], "Cold day? Try these hot dishes 🔥")
            elif weather == "hot":
                response_text = build_response(food_recommendations["cold"], "Hot weather? Try something refreshing ❄️")
            else:
                response_text = build_response(food_recommendations["default"], "How about these:")

    else:
        response_text = "Sorry, I didn’t understand. Can you try again?"

    return jsonify({"fulfillmentText": response_text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
