"""
db.py — SQLite persistence for chat history.

Day 11 goal: instead of keeping conversation history in a Python list
(which disappears every time the Flask server restarts), we store each
message as a row in a SQLite database file.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "chat_history.db")


def get_connection():
    """
    Open a connection to the SQLite database.
    check_same_thread=False lets Flask's dev server (which can handle
    requests on different threads) use this connection safely for our
    simple use case.
    """
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    return conn


def init_db():
    """
    Create the messages table if it doesn't already exist.
    Call this once when the app starts up.
    """
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


def save_message(session_id, role, content):
    """
    Insert one message into the database.
    role is typically 'user' or 'assistant'.
    """
    conn = get_connection()
    conn.execute(
        "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
        (session_id, role, content),
    )
    conn.commit()
    conn.close()


def get_history(session_id):
    """
    Return the full conversation history for a session, oldest first,
    as a list of dicts shaped like: {"role": ..., "content": ...}
    This is the format most AI chat APIs (Claude, OpenAI) expect.
    """
    conn = get_connection()
    rows = conn.execute(
        "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id ASC",
        (session_id,),
    ).fetchall()
    conn.close()
    return [{"role": row["role"], "content": row["content"]} for row in rows]


def clear_history(session_id):
    """
    Optional helper: wipe history for a session (useful for a 'New chat' button).
    """
    conn = get_connection()
    conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()