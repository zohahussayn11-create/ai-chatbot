import os
import uuid
import requests
from flask import Flask, request, jsonify, session, render_template
from dotenv import load_dotenv
import db  # Day 11 — our sqlite helper module

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent"

SYSTEM_PROMPT = "You are a helpful, friendly assistant."

# Day 11 — create the table on startup (safe to call every time,
# it only creates the table if it doesn't already exist)
db.init_db()


def get_session_id():
    """
    Give each browser session its own id, so multiple users (or tabs)
    don't share the same chat history.
    """
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
    return session["session_id"]


def history_to_gemini_contents(history):
    """
    Gemini's API expects conversation history in this shape:
    [{"role": "user"/"model", "parts": [{"text": "..."}]}, ...]

    Our db.py stores roles as "user"/"assistant" (the Anthropic/OpenAI
    convention), so we translate "assistant" -> "model" here.
    """
    contents = []
    for msg in history:
        role = "model" if msg["role"] == "assistant" else "user"
        contents.append({"role": role, "parts": [{"text": msg["content"]}]})
    return contents


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True)

    if not data or not data.get("message", "").strip():
        return jsonify({"error": "Message cannot be empty"}), 400

    user_message = data["message"].strip()
    session_id = get_session_id()

    # Save the user's message to the database
    db.save_message(session_id, "user", user_message)

    # Load full history from the database (includes the message we just saved)
    history = db.get_history(session_id)
    contents = history_to_gemini_contents(history)

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY,
    }
    payload = {
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": contents,
    }

    try:
        response = requests.post(GEMINI_URL, headers=headers, json=payload, timeout=30)
        response_data = response.json()

        if response.status_code != 200:
            print("Gemini API error:", response_data)
            return jsonify({"error": "The AI service is having trouble right now. Please try again."}), 502

        reply_text = response_data["candidates"][0]["content"]["parts"][0]["text"]

    except requests.exceptions.RequestException as e:
        print("Request failed:", e)
        return jsonify({"error": "The AI service is having trouble right now. Please try again."}), 502
    except (KeyError, IndexError) as e:
        print("Unexpected response shape:", e, response_data)
        return jsonify({"error": "Something went wrong. Please try again."}), 500

    # Save the assistant's reply too, so it's part of history next time
    db.save_message(session_id, "assistant", reply_text)

    return jsonify({"reply": reply_text})


@app.route("/history", methods=["GET"])
def history():
    """Optional: lets the frontend reload past messages on page refresh."""
    session_id = get_session_id()
    return jsonify({"history": db.get_history(session_id)})


@app.route("/new-chat", methods=["POST"])
def new_chat():
    """Optional: a 'New chat' button can hit this to clear history."""
    session_id = get_session_id()
    db.clear_history(session_id)
    return jsonify({"status": "cleared"})


if __name__ == "__main__":
    app.run(debug=True)