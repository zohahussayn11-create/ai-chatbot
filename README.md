# AI Chatbot

A web-based AI chatbot with a chat interface, built with Flask and vanilla JavaScript.
Currently in progress — this README will be updated as the project develops.

## Status: Week 1 complete (Foundations)

**What works so far:**
- A styled chat window UI (message bubbles, input box, send button) built with HTML/CSS flexbox
- Frontend JavaScript that adds messages to the chat window in real time
- A Flask backend connected to the frontend via a `/chat` POST route
- Messages round-trip from browser → Flask → back to browser as JSON

**What's not built yet:**
- No real AI responses yet — the backend currently just echoes back what you typed
- No conversation memory (each message is independent)
- Not deployed — runs locally only

## Tech stack

- **Backend:** Python, Flask
- **Frontend:** HTML, CSS (flexbox), vanilla JavaScript (`fetch` API)
- **Planned:** Anthropic/OpenAI API, SQLite (optional), deployment on Render/Railway

## Running it locally

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
flask run
```

Then open http://127.0.0.1:5000 in your browser.

## Project structure

```
├── app.py                 # Flask routes
├── templates/
│   ├── home.html          # Main chat UI
│   └── about.html         # About page
├── static/
│   ├── style.css          # Chat window styling
│   └── script.js          # Frontend interactivity + fetch logic
└── venv/                  # Not tracked in git (see .gitignore)
```

## Next up (Week 2)

Connecting the `/chat` route to a real AI API instead of the current echo response.