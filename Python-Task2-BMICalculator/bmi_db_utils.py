"""
bmi_db_utils.py
----------------
All SQLite database logic for the BMI Calculator (Advanced Tier) lives here,
kept separate from the GUI code. Every function wraps its database work in
try/except so that a database problem (locked file, permissions, corrupt
file, etc.) never crashes the app - callers get a (success, data_or_error)
style result and decide how to show it to the user.
"""

import sqlite3  #database 
from datetime import datetime  #get date and time

DB_FILE = "bmi_records.db"   #new file 


def normalize_username(username: str) -> str: #username is always string
   
    return username.strip().title()  #strip->trim space #title-> 1st lett big other small


def init_db():   #create table 
   
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS bmi_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, # ++ for unique id
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

    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M") #datetime.now()-> get current date & time  #strftime("%Y-%m-%d %H:%M") formatting
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute(
                "INSERT INTO bmi_records (username, weight, height, bmi, category, date_recorded) " #parameterize query _> no SQL injection
                "VALUES (?, ?, ?, ?, ?, ?)", #fill later
                (username, weight, height, bmi, category, timestamp),
            )
        return True, None
    except sqlite3.Error as e:
        return False, f"Could not save the record: {e}"


def get_users():
   
    try:
        with sqlite3.connect(DB_FILE) as conn:
            rows = conn.execute( # distinct for unique                                #case ignore
                "SELECT DISTINCT username FROM bmi_records ORDER BY username COLLATE NOCASE"
            ).fetchall()    # result in form of list 
            #.fetchone()	Sirf pehla (first) result laao.
        return True, [row[0] for row in rows] #get only name 
    except sqlite3.Error as e:
        return False, f"Could not load user list: {e}"


def get_records_for_user(username: str):
    
    try:
        with sqlite3.connect(DB_FILE) as conn:
            rows = conn.execute(
                "SELECT id, weight, height, bmi, category, date_recorded "
                "FROM bmi_records WHERE username = ? COLLATE NOCASE ORDER BY date_recorded ASC", # assending
                (username,),
            ).fetchall() #show list
        return True, rows
    except sqlite3.Error as e:
        return False, f"Could not load history: {e}"
