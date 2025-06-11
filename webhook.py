from flask import Flask, request, jsonify
from flask import send_from_directory

from user_data import get_recent_meals, add_recent_meal
import os
import json

app = Flask(__name__)

USER_DATA_FILE = "user_data.json"

@app.route('/picture/<filename>')
def serve_picture(filename):
    return send_from_directory('/Users/qintongtong/Documents/FoodRecommenderBot/picture', filename)

# 用户数据处理函数
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
    "default": ["Ramen", "Sandwich", "Dumplings", "Donburi"],
    "health_goal": {
        "lose weight": ["Quinoa Salad", "Steamed Vegetables", "Tofu Bowl"],
        "gain muscle": ["Grilled Chicken", "Beef Bowl", "Protein Pasta"],
        "stay healthy": ["Grilled Salmon", "Avocado Salad", "Vegetable Soup"]
    },
    "meal_time": {
        "breakfast": ["Toast", "Omelette", "Yogurt Bowl", "Egg Sandwich", "Porridge", "Avocado Toast"],
        "lunch": ["Bibimbap", "Curry Rice", "Chicken Salad", "Ramen"],
        "dinner": ["Salmon Bowl", "Udon", "Grilled Vegetables", "Spaghetti", "Grilled Fish"]
    }
}

# 推荐回复生成（避开最近食物）
def build_response(recommendations, context="", user_id="default"):
    recent = get_recent_meals(user_id)
    filtered = [food for food in recommendations if food not in recent]

    if not filtered:
        first = recommendations[0]
        img_url = f"https://food-recommender-bot.onrender.com/picture/{first.lower().replace(' ', '_')}.jpg"
        return f"{context} But you’ve tried them all recently 😅. How about trying them again? {first}\n[Image]({img_url})"
    
    first = filtered[0]
    add_recent_meal(user_id, first)
    img_url = f"https://food-recommender-bot.onrender.com/picture/{first.lower().replace(' ', '_')}.jpg"
    
    phrase = f"{context} You might enjoy {first}\n[Image]({img_url})"
    if len(filtered) > 1:
        phrase += f", or maybe {', '.join(filtered[1:3])}."
    return phrase

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()
    print("Webhook hit!")
    print("Request JSON:", req)

    intent = req.get("queryResult", {}).get("intent", {}).get("displayName", "")
    parameters = req.get("queryResult", {}).get("parameters", {})
    session = req.get("session", "unknown_session")
    user_id = session.split("/")[-1]  # 用 session id 作为用户唯一标识

    # 参数获取
    food_pref = parameters.get("food_preference", "").lower()
    weather = parameters.get("weather_type", "").lower()
    delivery = parameters.get("delivery_option", "").lower()
    spicy_type = parameters.get("spicy_type", "").lower()
    recent_meal = parameters.get("recent_meal", "").strip()
    health_goal = parameters.get("health_goal", "").lower()
    meal_time = parameters.get("meal_time", "").lower()
  
    # 记录最近吃过的
    if recent_meal:
        add_recent_meal(user_id, recent_meal)
    
    response_text = ""
    
    if intent == "start.recommendation":
        response_text = "Do you have any food preferences? For example: spicy, healthy, rice, pasta, or no preference."

    elif intent == "spicy.preference":
        if spicy_type and spicy_type in food_recommendations["spicy"]:
            response_text = build_response(
                food_recommendations["spicy"][spicy_type],
                f"Spicy ({spicy_type}) suggestion 🌶️",
                user_id
            )
        else:
            response_text = build_response(
                food_recommendations["spicy"]["default"],
                "Here’s a spicy suggestion 🌶️",
                user_id
            )

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
    
    elif intent == "cold.preference":
        response_text = build_response(
            food_recommendations["spicy"]["default"],
            "It’s cold today ❄️. Try these hot dishes 🔥",
            user_id
        )
        
    elif intent in ["rice.preference", "pasta.preference", "fastfood.preference"]:
        key = intent.split(".")[0]  # rice / pasta / fastfood
        if key in food_recommendations:
            response_text = build_response(food_recommendations[key], f"Suggestions for {key} 🍽️")

    elif intent in ["choose.delivery", "choosen.dinein", "followup.delivery.option"]:
        delivery = parameters.get("delivery_option", "").lower()
        recent = get_recent_meals(user_id)

        if delivery == "delivery":
            if food_pref in food_recommendations:
                choices = [m for m in food_recommendations[food_pref] if m not in recent]
                response_text = build_response(choices, f"You chose delivery 🚚. Here are some {food_pref} options:")
            else:
                response_text = build_response(food_recommendations["default"], "You chose delivery 🚚. Here are some tasty picks:")
    
        elif delivery == "dine in":
            if food_pref in food_recommendations:
                choices = [m for m in food_recommendations[food_pref] if m not in recent]
                response_text = build_response(choices, f"You prefer dining in 🍽️. Try these {food_pref} dishes:")
            else:
                response_text = build_response(food_recommendations["default"], "Dining in sounds good 🍽️. Try these dishes:")
    
        else:
            response_text = "Do you prefer delivery or eating in?"

    elif intent == "health.goal.recommendation":
    health_goal_list = req['queryResult']['parameters'].get('health_goal', [])
    health_goal = health_goal_list[0] if health_goal_list else ""
    
    if health_goal in food_recommendations["health_goal"]:
        response_text = build_response(
            food_recommendations["health_goal"][health_goal],
            f"Suggestions for {health_goal} 💪:",
            user_id
        )
    else:
        response_text = {
            "fulfillmentMessages": [
                {"text": {"text": ["Could you tell me your health goal again? Like 'lose weight' or 'build muscle'."]}}
            ]
        }
        return jsonify(response_text)
        
    elif intent == "meal.time.recommendation":
        if meal_time in food_recommendations["meal_time"]:
            response_text = build_response(food_recommendations["meal_time"][meal_time], f"{meal_time.capitalize()} options ☀️:", user_id)
        else:
            response_text = "Is it breakfast, lunch, or dinner time?"

    elif intent == "personalized.recommendation":
        recent = get_recent_meals(user_id)
        if food_pref in food_recommendations:
            choices = [m for m in food_recommendations[food_pref] if m not in recent]
            response_text = build_response(choices, f"Tailored pick for {food_pref}:")
        elif weather == "cold":
            choices = [m for m in food_recommendations["spicy"]["default"] if m not in recent]
            response_text = build_response(choices, "Cold day special 🔥")
        elif weather == "hot":
            choices = [m for m in food_recommendations["cold"] if m not in recent]
            response_text = build_response(choices, "Cool choices for hot weather ❄️")
        else:
            response_text = build_response(food_recommendations["default"], "How about these:")
    
    elif intent == "record.recent.meal":
        if recent_meal:
            add_recent_meal(user_id, recent_meal)
            response_text = f"Thanks! I’ve noted that you had {recent_meal}. I’ll avoid recommending it again."        
        else:
            response_text = "Got it! Could you repeat the food you just had?"
    else:
        response_text = "Sorry, I didn’t understand. Can you try again?"

    return jsonify({"fulfillmentText": response_text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
