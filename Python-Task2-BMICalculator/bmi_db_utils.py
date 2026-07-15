"""
bmi_db_utils.py
----------------
All SQLite database logic for the BMI Calculator (Advanced Tier) lives here,
kept separate from the GUI code. Every function wraps its database work in
try/except so that a database problem (locked file, permissions, corrupt
file, etc.) never crashes the app - callers get a (success, data_or_error)
style result and decide how to show it to the user.
"""

import sqlite3
from datetime import datetime

DB_FILE = "bmi_records.db"


def normalize_username(username: str) -> str:
    """
    Normalizes a name so that different casings of the same name
    (e.g. 'dua', 'DUA', 'Dua') are treated as the same user and stored
    consistently. Trims whitespace and title-cases the result.
    """
    return username.strip().title()


def init_db():
    """
    Creates the bmi_records table if it doesn't already exist.
    Returns (True, None) on success or (False, error_message) on failure.
    """
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS bmi_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    weight REAL NOT NULL,
                    height REAL NOT NULL,
                    bmi REAL NOT NULL,
                    category TEXT NOT NULL,
                    date_recorded TEXT NOT NULL
                )
            """)
        return True, None
    except sqlite3.Error as e:
        return False, f"Could not set up the database: {e}"


def add_record(username: str, weight: float, height: float, bmi: float, category: str):
    """
    Inserts a new BMI record for a user, stamped with the current timestamp.
    Returns (True, None) on success or (False, error_message) on failure.
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute(
                "INSERT INTO bmi_records (username, weight, height, bmi, category, date_recorded) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (username, weight, height, bmi, category, timestamp),
            )
        return True, None
    except sqlite3.Error as e:
        return False, f"Could not save the record: {e}"


def get_users():
    """
    Returns (True, list_of_usernames) on success or (False, error_message) on failure.
    """
    try:
        with sqlite3.connect(DB_FILE) as conn:
            rows = conn.execute(
                "SELECT DISTINCT username FROM bmi_records ORDER BY username COLLATE NOCASE"
            ).fetchall()
        return True, [row[0] for row in rows]
    except sqlite3.Error as e:
        return False, f"Could not load user list: {e}"


def get_records_for_user(username: str):
    """
    Returns (True, list_of_rows) on success or (False, error_message) on failure.
    Each row is (id, weight, height, bmi, category, date_recorded), oldest first.
    """
    try:
        with sqlite3.connect(DB_FILE) as conn:
            rows = conn.execute(
                "SELECT id, weight, height, bmi, category, date_recorded "
                "FROM bmi_records WHERE username = ? COLLATE NOCASE ORDER BY date_recorded ASC",
                (username,),
            ).fetchall()
        return True, rows
    except sqlite3.Error as e:
        return False, f"Could not load history: {e}"
