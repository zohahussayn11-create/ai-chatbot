import os
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

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
    data = request.get_json(silent=True) or {}
    user_message = data.get('message', '').strip()

    # 1. Handle empty input before ever calling the API
    if not user_message:
        return jsonify({'error': "Please type a message before sending."}), 400

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

    try:
        # 2. Always set a timeout so a hung request doesn't hang your server
        gemini_response = requests.post(
            GEMINI_URL, headers=headers, json=payload, timeout=15
        )

        # 3. Raise an exception if Gemini returned a 4xx/5xx status
        gemini_response.raise_for_status()

        gemini_data = gemini_response.json()

        # 4. Guard against an unexpected response shape
        reply_text = gemini_data["candidates"][0]["content"]["parts"][0]["text"]

    except requests.exceptions.Timeout:
        return jsonify({'error': "The AI is taking too long to respond. Please try again."}), 504

    except requests.exceptions.HTTPError:
        # This fires from raise_for_status() above
        status = gemini_response.status_code
        print("GEMINI ERROR STATUS:", status)
        print("GEMINI ERROR BODY:", gemini_response.text)
    
        if status == 401:
            return jsonify({'error': "Server configuration error. Please contact the site owner."}), 500
        elif status == 429:
            return jsonify({'error': "Too many requests right now. Please wait a moment and try again."}), 429
        else:
            return jsonify({'error': "The AI service returned an error. Please try again."}), 502

    except requests.exceptions.RequestException:
        # Catches connection errors, DNS failures, etc.
        return jsonify({'error': "Couldn't reach the AI service. Check your connection and try again."}), 502

    except (KeyError, IndexError):
        # gemini_data came back but not in the shape we expected
        return jsonify({'error': "Got an unexpected response from the AI. Please try again."}), 502

    return jsonify({'reply': reply_text})


if __name__ == '__main__':
    app.run(debug=True)