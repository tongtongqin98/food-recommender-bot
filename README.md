# Smart Food Recommendation Chatbot (Flask + Dialogflow)

This project is a smart food recommendation chatbot built using Dialogflow and Flask. It provides meal suggestions based on user preferences, recent meals, and weather conditions.

## Features
- Personalized meal suggestions
- Weather-aware recommendations
- Avoids repeating recently eaten meals
- Saves user history to a local JSON file

## Requirements
- Python 3.7+
- Flask

## Setup Instructions

1. Clone the project and install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Flask webhook locally:
```bash
python webhook.py
```

3. (Optional) Use [ngrok](https://ngrok.com) to expose your local server:
```bash
ngrok http 5000
```

4. Paste your ngrok HTTPS URL into Dialogflow > Fulfillment > Webhook URL

## File Descriptions

- `webhook.py` — Flask backend for Dialogflow webhook
- `user_data.json` — stores user meal history and preferences
- `requirements.txt` — dependency list

## Example Response

If weather is hot and the user recently ate 'Cold noodles', the response might be:
> Based on the weather, I recommend: Fruit salad, Iced tea with sandwich

---
