import os
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent"

# Day 10: a simple in-memory conversation history.
# This is just a Python list living in RAM while the server runs.
# It resets every time you restart Flask, and it's shared by anyone
# using the app (fine for a solo portfolio project, not for multi-user production).
conversation_history = []


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = data.get('message', '').strip()

    if not user_message:
        return jsonify({'error': "Please type a message before sending."}), 400

    # Add the user's new message to the running history
    conversation_history.append({
        "role": "user",
        "parts": [{"text": user_message}]
    })

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    }

    # Day 10: send the FULL history, not just the latest message,
    # so Gemini has context of the whole conversation so far.
    payload = {
        "contents": conversation_history
    }

    try:
        gemini_response = requests.post(
            GEMINI_URL, headers=headers, json=payload, timeout=15
        )
        gemini_response.raise_for_status()
        gemini_data = gemini_response.json()
        reply_text = gemini_data["candidates"][0]["content"]["parts"][0]["text"]

        # Add the bot's reply to the history too, so future requests
        # include it as context.
        conversation_history.append({
            "role": "model",
            "parts": [{"text": reply_text}]
        })

    except requests.exceptions.Timeout:
        return jsonify({'error': "The AI is taking too long to respond. Please try again."}), 504

    except requests.exceptions.HTTPError:
        status = gemini_response.status_code
        if status == 401:
            return jsonify({'error': "Server configuration error. Please contact the site owner."}), 500
        elif status == 429:
            return jsonify({'error': "Too many requests right now. Please wait a moment and try again."}), 429
        else:
            return jsonify({'error': "The AI service returned an error. Please try again."}), 502

    except requests.exceptions.RequestException:
        return jsonify({'error': "Couldn't reach the AI service. Check your connection and try again."}), 502

    except (KeyError, IndexError):
        return jsonify({'error': "Got an unexpected response from the AI. Please try again."}), 502

    return jsonify({'reply': reply_text})


if __name__ == '__main__':
    app.run(debug=True)