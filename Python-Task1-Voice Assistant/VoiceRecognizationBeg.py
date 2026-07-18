"""
Voice Assistant - Beginner Tier
----------------------------------
A voice-controlled assistant that:
  - Listens through the microphone using speech_recognition
  - Responds to "hello" with a greeting
  - Tells the current time and date on request
  - Performs a web search on a spoken topic
  - Asks the user to repeat if it doesn't understand them
  - Speaks every response out loud using pyttsx3

The code is split into two layers on purpose:
  1. Audio layer (speak, listen) - talks to the microphone/speakers.
     This cannot be exercised in an automated test without real audio
     hardware, so it is kept as thin as possible.
  2. Logic layer (handle_command and its helpers) - pure text in,
     text out. This is where almost all of the actual behaviour lives,
     and it can be fully unit-tested without any audio at all.
"""

import datetime
import webbrowser

import speech_recognition as sr
import pyttsx3

GREETING_WORDS = {"hello", "hi", "hey"}
EXIT_WORDS = {"exit", "quit", "stop", "goodbye", "bye"}
SEARCH_TRIGGERS = ["search for ", "search ", "look up ", "google "]


# ============================================================ AUDIO LAYER


def build_tts_engine():
    engine = pyttsx3.init()
    engine.setProperty("rate", 170)
    return engine


def speak(engine, text: str):
    """Prints the response (handy for debugging) and speaks it aloud."""
    print(f"Assistant: {text}")
    engine.say(text)
    engine.runAndWait()


def listen(recognizer: sr.Recognizer) -> str:
    """
    Listens for one phrase from the default microphone and converts it
    to lowercase text.
    Returns "" if nothing was understood, so the caller can react the
    same way whether the mic was silent or the speech was unclear.
    """
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print("Listening...")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
        except sr.WaitTimeoutError:
            return ""

    try:
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text.lower()
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        print("Speech recognition service is unavailable right now.")
        return ""


# ============================================================ LOGIC LAYER


def get_time_response(now: datetime.datetime = None) -> str:
    now = now or datetime.datetime.now()
    return f"The current time is {now.strftime('%I:%M %p')}."


def get_date_response(now: datetime.datetime = None) -> str:
    now = now or datetime.datetime.now()
    return f"Today's date is {now.strftime('%B %d, %Y')}."


def extract_search_topic(command: str):
    """
    Returns the search topic if the command starts with a recognised
    search phrase (e.g. "search for pizza recipes" -> "pizza recipes"),
    or None if it isn't a search command.
    """
    for trigger in SEARCH_TRIGGERS:
        if command.startswith(trigger):
            topic = command[len(trigger) :].strip()
            return topic or None
    return None


def handle_command(command: str, open_browser=webbrowser.open):
    """
    The assistant's decision-making core: given the recognised text,
    decide what to say back and whether the program should exit.

    Returns (response_text, should_exit). Word-level matching is used
    throughout (splitting into `words`) rather than substring checks,
    so that e.g. "desktop wallpapers" doesn't accidentally trigger the
    exit word "stop", and "sometimes" doesn't accidentally trigger "time".
    """
    command = command.lower().strip()

    if not command:
        return "Sorry, I didn't catch that. Could you please repeat that?", False

    words = command.split()

    if EXIT_WORDS & set(words):
        return "Goodbye! Have a great day.", True

    if GREETING_WORDS & set(words):
        return "Hello! How can I help you today?", False

    if "time" in words:
        return get_time_response(), False

    if "date" in words:
        return get_date_response(), False

    topic = extract_search_topic(command)
    if topic:
        open_browser(f"https://www.google.com/search?q={topic}")
        return f"Here are the search results for {topic}.", False

    return (
        "I'm not sure how to help with that yet. You can say hello, "
        "ask for the time or date, or ask me to search something."
    ), False


# ============================================================ MAIN LOOP


def main():
    engine = build_tts_engine()
    recognizer = sr.Recognizer()

    speak(
        engine,
        "Voice assistant is ready. Say hello, ask for the time or "
        "date, or ask me to search something.",
    )

    while True:
        command = listen(recognizer)
        response, should_exit = handle_command(command)
        speak(engine, response)
        if should_exit:
            break


if __name__ == "__main__":
    main()
