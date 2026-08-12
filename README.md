# AI Chatbot

A web-based AI chatbot with a chat interface, built with Flask and vanilla JavaScript, powered by Google's Gemini API, with conversation history that persists across server restarts.

## Status: Week 2 complete (The AI Brain)

**What works so far:**
- A styled chat window UI (message bubbles, input box, send button) built with HTML/CSS flexbox
- Frontend JavaScript that adds messages to the chat window in real time
- A Flask backend connected to the frontend via a `/chat` POST route
- **Real AI responses** via the Gemini API (`gemini-3.6-flash`) — no more echo, the bot actually replies
- **Conversation memory** — the bot remembers earlier messages within a session
- **Persistent storage (SQLite)** — chat history is saved to a database and survives server restarts, not just kept in memory
- Basic error handling around the API call (empty messages, failed requests)

**What's not built yet:**
- No system prompt / defined persona yet (bot has a generic default personality)
- No input validation or rate limiting (can send empty spam-clicks or huge messages untested)
- No loading indicator or timestamps in the UI yet
- Not deployed — runs locally only

## Tech stack

- **Backend:** Python, Flask
- **Frontend:** HTML, CSS (flexbox), vanilla JavaScript (`fetch` API)
- **AI:** Google Gemini API, called directly via `requests` (REST API, no SDK)
- **Database:** SQLite, via Python's built-in `sqlite3` module
- **Environment management:** `python-dotenv` for keeping the API key out of source control
- **Planned:** deployment on Render/Railway

## Architecture

The browser never talks to the Gemini API directly — every message goes through the Flask server, which keeps the API key private and handles memory and error handling.

\```
[Browser: HTML/CSS/JS] <-- user types message
        |  (fetch POST request with the message)
        v
[Flask server: Python] <-- receives message, loads history from SQLite
        |  (sends full conversation history to Gemini)
        v
[Gemini API] <-- generates a response
        |
        v
[Flask saves the reply to SQLite, sends it back to browser as JSON]
        |
        v
[Browser displays the AI's reply in the chat window]
\```

## How chat history works

Each browser session gets a unique `session_id`. Every message — from the user and from the AI — gets saved as a row in a `messages` table in `chat_history.db`. On each new message, the full conversation history for that session is loaded from the database and sent along to Gemini, since LLM APIs are stateless and don't remember anything unless the history is sent back every time.

Gemini expects roles as `"user"` and `"model"`. The app translates the more conventional `"assistant"` label into `"model"` right before sending, so the database itself doesn't need to know which AI provider is being used.

## Running it locally

\```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
\```

Create a `.env` file in the project root:

\```
GEMINI_API_KEY=your-key-here
\```

Then run:

\```bash
flask run
\```

Open http://127.0.0.1:5000 in your browser.

## Project structure

\```
├── app.py                          # Flask routes, session handling, Gemini API calls
├── db.py                           # SQLite helper functions (init, save, get, clear history)
├── chat_history.db                 # SQLite database (auto-created, not tracked in git)
├── templates/
│   ├── home.html                   # Main chat UI
│   └── about.html                  # About page
├── static/
│   ├── style.css                   # Chat window styling
│   └── script.js                   # Frontend interactivity + fetch logic
├── test_api_gemini_requests.py     # Standalone script for testing the Gemini API directly
├── requirements.txt
├── .env                             # API key (not tracked in git)
└── venv/                            # Not tracked in git (see .gitignore)
\```

## What I learned this week

- How LLM APIs are stateless, and how to manually manage conversation history
- Working with SQLite directly through Python's `sqlite3` module — creating tables, inserting rows, running queries
- Translating between different API conventions (Gemini's `user`/`model` roles vs. the more common `user`/`assistant`)
- Debugging real issues along the way: a missing package, a template filename mismatch, and switching the whole backend from a planned Anthropic integration to Gemini once I confirmed which key I actually had
- Keeping API keys out of source control with `.env` and `.gitignore`

## Next up (Week 3)

- Give the bot a defined personality via a system prompt
- UI polish: loading indicator, timestamps, mobile-friendly styling
- Input validation & rate limiting (disable Send while waiting for a reply)
- Deploy to a live public URL (Render or Railway)