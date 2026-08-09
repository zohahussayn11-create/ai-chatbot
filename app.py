import os
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Load the .env file so GEMINI_API_KEY becomes available via os.environ.
load_dotenv()

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent"


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": user_message}
                ]
            }
        ]
    }

    gemini_response = requests.post(GEMINI_URL, headers=headers, json=payload)
    gemini_data = gemini_response.json()

    reply_text = gemini_data["candidates"][0]["content"]["parts"][0]["text"]

    return jsonify({'reply': reply_text})


app.run(debug=True)