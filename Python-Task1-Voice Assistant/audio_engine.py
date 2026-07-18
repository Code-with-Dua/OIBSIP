"""
audio_engine.py - Handles listening and speaking with colored terminal output.
"""

import speech_recognition as sr
import pyttsx3
import threading
from colorama import init, Fore, Style

# Initialize colorama for Windows compatibility
init(autoreset=True)

# Global lock to make the TTS engine thread-safe
_tts_lock = threading.Lock()


def build_tts_engine():
    engine = pyttsx3.init()
    engine.setProperty("rate", 170)
    return engine


def speak(engine, text: str):
    """
    Prints the response in color and speaks it aloud.
    - Successful/normal responses: Green
    - Error / fallback / "didn't catch that" / "not sure how to help": Red
    Uses a thread lock to prevent concurrent TTS calls.
    """
    # Determine color based on content
    if (
        "I'm not sure how to help with that" in text
        or "Sorry, I didn't catch that" in text
        or "Please try rephrasing" in text
        or "Could you please repeat" in text
    ):
        color = Fore.RED  # Error / fallback / didn't hear
    else:
        color = Fore.GREEN  # Successful responses only (hello, time, weather, etc.)

    # Colored print
    print(f"{color}Assistant: {text}{Style.RESET_ALL}")

    # Acquire the lock before using the engine
    with _tts_lock:
        engine.say(text)
        engine.runAndWait()


def listen(recognizer: sr.Recognizer) -> str:
    """
    Listens via microphone and returns lowercase text.
    Returns "" if nothing was understood.
    Prints listening status in Purple and recognized text in Yellow.
    """
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        # Listening status – Purple (heading)
        print(f"{Fore.MAGENTA}Listening...{Style.RESET_ALL}")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
        except sr.WaitTimeoutError:
            return ""

    try:
        text = recognizer.recognize_google(audio)
        # User's spoken text – Yellow
        print(f"{Fore.YELLOW}You said: {text}{Style.RESET_ALL}")
        return text.lower()
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        print(
            f"{Fore.RED}Speech recognition service is unavailable right now.{Style.RESET_ALL}"
        )
        return ""