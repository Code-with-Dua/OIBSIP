"""
action_handlers.py - All the actual actions (weather, email, reminder, QA, time/date).
"""

import datetime
import time
import threading
import smtplib
import os
import requests
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()


# ---------- TIME & DATE ----------
def get_time_response(now: datetime.datetime = None) -> str:
    now = now or datetime.datetime.now()
    return f"The current time is {now.strftime('%I:%M %p')}."


def get_date_response(now: datetime.datetime = None) -> str:
    now = now or datetime.datetime.now()
    return f"Today's date is {now.strftime('%B %d, %Y')}."


# ---------- EMAIL ----------
def send_email(recipient: str, subject: str = "", body: str = ""):
    sender = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")
    if not sender or not password:
        return "Email credentials not configured in .env file."

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        return f"Email sent to {recipient}."
    except Exception as e:
        return f"Failed to send email: {str(e)}"


# ---------- REMINDER ----------
def set_reminder(duration_str: str, message: str, engine):
    parts = duration_str.split()
    if len(parts) < 2:
        return "I couldn't understand the duration. Please say like '5 minutes'."
    try:
        value = int(parts[0])
    except ValueError:
        return "I couldn't parse the number."
    unit = parts[1].lower()
    if unit.startswith("second"):
        seconds = value
    elif unit.startswith("minute"):
        seconds = value * 60
    elif unit.startswith("hour"):
        seconds = value * 3600
    else:
        return "Supported units: seconds, minutes, hours."

    def reminder_job():
        import audio_engine
        time.sleep(seconds)
        audio_engine.speak(engine, f"Reminder: {message if message else 'Time is up!'}")

    threading.Thread(target=reminder_job, daemon=True).start()
    return f"Reminder set for {duration_str}."


# ---------- WEATHER ----------
def get_weather(location: str = None):
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        return "Weather API key not set in .env file."
    if not location:
        location = "London"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        if data.get("cod") != 200:
            return f"Weather info not found for {location}."
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        return f"The weather in {location} is {desc} with a temperature of {temp}°C."
    except Exception as e:
        return f"Error fetching weather: {str(e)}"


# ---------- QA (General Knowledge) ----------
def fetch_wikipedia_summary(topic: str):
    """Fetch a short summary from Wikipedia for the given topic."""
    if not topic:
        return None
    topic = topic.strip().title()
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic.replace(' ', '_')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("extract"):
                return data["extract"]
            elif data.get("extract_html"):
                text = re.sub(r"<[^>]+>", "", data["extract_html"])
                return text[:500]
        return None
    except:
        return None


def answer_question(query: str):
    """
    Uses DuckDuckGo Instant Answer API, then falls back to Wikipedia.
    """
    # 1. Try DuckDuckGo
    url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        if data.get("AbstractText"):
            return data["AbstractText"]
        elif data.get("Answer"):
            return data["Answer"]
    except:
        pass

    # 2. Fallback: Wikipedia
    # Try to extract a topic (e.g., "France" from "capital of France", etc.)
    of_match = re.search(r"\bof\s+([A-Za-z ]+)", query)
    if of_match:
        topic = of_match.group(1).strip()
    else:
        words = query.split()
        topic = words[-1] if words else None

    if topic:
        wiki_answer = fetch_wikipedia_summary(topic)
        if wiki_answer:
            return wiki_answer[:500] + "..." if len(wiki_answer) > 500 else wiki_answer

    return "I don't have an answer to that."


# ---------- CAPITAL (SPECIFIC) ----------
def get_capital_info(country: str) -> str:
    """
    Returns the capital of a country.

    Primary source: REST Countries API — returns clean structured JSON
    (no API key needed), so there's no prose to regex-parse and no risk
    of picking the wrong sentence out of a Wikipedia summary.

    Fallback: old Wikipedia-summary regex approach, only used if
    REST Countries is unreachable or doesn't recognise the name
    (e.g. a slightly misspelled or unofficial country name).
    """
    if not country:
        return "Please specify a country."

    country_clean = country.strip()

    # --- Primary: REST Countries API (retry on failure) ---
    # fullText=true avoids partial-match ambiguity, e.g. "india" partially
    # matching "British Indian Ocean Territory" (which has no capital set)
    # and silently winning over the real "India" entry.
    #
    # Note: the first connection attempt to restcountries.com occasionally
    # times out / resets on some networks - a quick retry reliably succeeds,
    # so we just retry silently instead of surfacing that to the user.
    url = f"https://restcountries.com/v3.1/name/{country_clean}?fullText=true&fields=name,capital"
    for attempt in range(3):
        try:
            resp = requests.get(url, timeout=6)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list) and len(data) > 0:
                    entry = data[0]
                    capitals = entry.get("capital")
                    official_name = entry.get("name", {}).get("common", country_clean.title())
                    if capitals:
                        return f"The capital of {official_name} is {capitals[0]}."
                # Got a 200 but no usable data (unknown/mistyped country name) -
                # retrying won't help, so stop here and fall back to Wikipedia.
                break
        except Exception:
            continue  # transient network hiccup - try again immediately

    # --- Fallback: Wikipedia summary parsing ---
    return _get_capital_from_wikipedia(country_clean)


def _get_capital_from_wikipedia(country: str) -> str:
    """
    Fallback used only when REST Countries can't answer.
    Fetches Wikipedia and extracts the capital city name using regex
    that handles both common phrasings:
      - "X is the capital of Country"
      - "Country's capital ... is X"   (this is the one that used to fail)
    """
    country = country.strip().title()
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{country.replace(' ', '_')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code != 200:
            return f"I couldn't find information about {country}."

        data = resp.json()
        extract = data.get("extract")
        if not extract:
            return f"I couldn't find a summary for {country}."

        patterns = [
            # "X is the [nation's/country's] capital of Country"
            r'([A-Z][\w\-]+(?:\s[A-Z][\w\-]+)*)\s+is\s+the\s+(?:\w+\'s\s+)?capital(?:\s+city)?(?:,?\s+[^,\.]*)?\s+of\s+' + re.escape(country),
            # "capital of Country is X"
            r'capital\s+of\s+' + re.escape(country) + r'\s+is\s+([A-Z][\w\-]+(?:\s[A-Z][\w\-]+)*)',
            # "Country's capital[, largest city, ...] is X"  <-- handles the France case
            r'capital(?:\s+city)?(?:,\s*[^,\.]+)*(?:\s+and\s+[^,\.]+)?\s+is\s+([A-Z][\w\-]+(?:\s[A-Z][\w\-]+)*)',
            # "X is the [nation's/country's] capital" (no "of Country" attached) <-- handles the Pakistan case
            r'([A-Z][\w\-]+(?:\s[A-Z][\w\-]+)*)\s+is\s+the\s+(?:\w+\'s\s+)?capital(?:\s+city)?\b',
        ]

        for pattern in patterns:
            match = re.search(pattern, extract)
            if match:
                capital = ' '.join(match.group(1).split())
                return f"The capital of {country} is {capital}."

        # No sentence mentions the capital at all (happens for some countries'
        # Wikipedia lead paragraphs, e.g. India) - be honest instead of dumping
        # an unrelated sentence.
        return f"I couldn't find the capital of {country} from the available sources."
    except Exception as e:
        return f"Error: {str(e)}"