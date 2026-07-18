"""
command_parser.py - Understands user intent and routes to actions.
"""

import re
import json
import webbrowser
import os
from action_handlers import (
    get_time_response,
    get_date_response,
    send_email,
    set_reminder,
    get_weather,
    answer_question,
    get_capital_info,
)
from dotenv import load_dotenv

load_dotenv()  # Load .env file

# ---------- CUSTOM COMMANDS ----------
CUSTOM_COMMANDS_FILE = "custom_commands.json"


def load_custom_commands():
    try:
        with open(CUSTOM_COMMANDS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_custom_command(phrase, response):
    commands = load_custom_commands()
    commands[phrase.lower()] = response
    with open(CUSTOM_COMMANDS_FILE, "w") as f:
        json.dump(commands, f, indent=2)


def get_custom_response(command):
    commands = load_custom_commands()
    for phrase, resp in commands.items():
        if phrase in command:
            return resp
    return None


# ---------- INTENTS ----------
INTENTS = [
    {"name": "greeting", "patterns": [r"\b(hello|hi|hey)\b"]},
    {"name": "time", "patterns": [r"\btime\b"]},
    {"name": "date", "patterns": [r"\bdate\b"]},
    {
        "name": "search",
        "patterns": [r"(?:search for|search|look up|google)\s+(?P<topic>.+)"],
    },
    # 👇 Complex email (for custom addresses) - kept for flexibility
    {
        "name": "email",
        "patterns": [
            r"send (?:an )?email to (?P<recipient>.+?)(?: with subject (?P<subject>.+?))?(?: and body (?P<body>.+))?$"
        ],
    },
    # 👇 NEW: Quick email (just say "send email")
    {"name": "quick_email", "patterns": [r"send email$", r"send email hello$"]},
    {
        "name": "reminder",
        "patterns": [
            r"set (?:a )?reminder for (?P<duration>.+?)(?: to (?P<message>.+))?$"
        ],
    },
    {
        "name": "weather",
        "patterns": [r"weather (?:in|for) (?P<location>.+)", r"weather$"],
    },
    {
        "name": "capital",
        "patterns": [
            r"what is the capital of (?P<country>.+)",
            r"capital of (?P<country>.+)",
        ],
    },
    {
        "name": "qa",
        "patterns": [r"(?:what is|who is|tell me about|define)\s+(?P<query>.+)"],
    },
    {
        "name": "add_command",
        "patterns": [r"add (?:a )?command (?P<phrase>.+?) as (?P<response>.+)"],
    },
    {"name": "exit", "patterns": [r"\b(exit|quit|stop|goodbye|bye)\b"]},
]


def parse_intent(command: str):
    command = command.lower().strip()
    for intent in INTENTS:
        for pattern in intent["patterns"]:
            match = re.search(pattern, command)
            if match:
                return {"intent": intent["name"], "entities": match.groupdict()}
    return None


# ---------- MAIN HANDLER ----------
def handle_command(command: str, engine, open_browser=webbrowser.open):
    """
    Returns (response_text, should_exit).
    """
    command = command.lower().strip()
    if not command:
        return "Sorry, I didn't catch that. Could you please repeat that?", False

    # 1. Check custom commands
    custom = get_custom_response(command)
    if custom:
        return custom, False

    # 2. Parse intent
    parsed = parse_intent(command)
    if parsed is None:
        return "I'm not sure how to help with that. Please try rephrasing.", False

    intent = parsed["intent"]
    ents = parsed["entities"]

    # 3. Route to actions
    if intent == "exit":
        return "Goodbye! Have a great day.", True

    elif intent == "greeting":
        return "Hello! How can I help you today?", False

    elif intent == "time":
        return get_time_response(), False

    elif intent == "date":
        return get_date_response(), False

    elif intent == "search":
        topic = ents.get("topic")
        if not topic:
            return "What would you like me to search for?", False
        open_browser(f"https://www.google.com/search?q={topic}")
        return f"Here are the search results for {topic}.", False

    # 👇 Complex email (if you want to specify recipient, subject, body)
    elif intent == "email":
        recipient = ents.get("recipient")
        subject = ents.get("subject") or "No subject"
        body = ents.get("body") or ""
        if not recipient:
            return "Please specify a recipient.", False
        result = send_email(recipient, subject, body)
        return result, False

    # 👇 NEW: Quick email – uses defaults from .env
    elif intent == "quick_email":
        recipient = os.getenv("DEFAULT_EMAIL_RECIPIENT")
        subject = os.getenv("DEFAULT_EMAIL_SUBJECT", "Hello")
        body = os.getenv("DEFAULT_EMAIL_BODY", "This is an automated email.")

        if not recipient:
            return (
                "Default email recipient not set in .env file. Please set DEFAULT_EMAIL_RECIPIENT.",
                False,
            )

        result = send_email(recipient, subject, body)
        return result, False

    elif intent == "reminder":
        duration = ents.get("duration")
        message = ents.get("message") or ""
        if not duration:
            return "Please specify a duration, like '5 minutes'.", False
        result = set_reminder(duration, message, engine)
        return result, False

    elif intent == "weather":
        location = ents.get("location")
        result = get_weather(location)
        return result, False

    elif intent == "capital":
        country = ents.get("country")
        if not country:
            return "Which country's capital would you like to know?", False
        result = get_capital_info(country)
        return result, False

    elif intent == "qa":
        query = ents.get("query")
        if not query:
            return "What do you want to ask?", False
        result = answer_question(query)
        return result, False

    elif intent == "add_command":
        phrase = ents.get("phrase")
        response = ents.get("response")
        if not phrase or not response:
            return "Please provide both a trigger phrase and a response.", False
        save_custom_command(phrase, response)
        return f"Command '{phrase}' added with response '{response}'.", False

    else:
        return "I can't handle that yet.", False
