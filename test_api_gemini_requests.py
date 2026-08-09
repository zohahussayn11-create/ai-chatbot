# A tiny, standalone script — no Flask here.
# This version talks to Gemini using plain HTTP requests instead of
# Google's SDK, so we don't need the 'google-genai' package at all
# (avoids the cryptography/Rust build issue on your machine).

import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")

# This is Gemini's REST API endpoint for generating content.
# Notice the model name is right in the URL — that's how you pick which model to use.
url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent"

headers = {
    "Content-Type": "application/json",
    "x-goog-api-key": api_key
}

# This is the exact JSON shape Gemini's API expects.
# 'contents' is a list because multi-turn conversations go here later (Day 10).
payload = {
    "contents": [
        {
            "parts": [
                {"text": "Say hello and tell me one fun fact about flexbox."}
            ]
        }
    ]
}

response = requests.post(url, headers=headers, json=payload)
data = response.json()

# Print the raw response so we can see exactly what came back —
# useful for debugging if something goes wrong.
print("Status code:", response.status_code)
print("Raw response:", data)
print()

# Gemini's reply text is nested a few levels deep in the JSON response.
reply_text = data["candidates"][0]["content"]["parts"][0]["text"]
print(reply_text)