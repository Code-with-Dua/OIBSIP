"""
main.py - Entry point for the Advanced Voice Assistant with a colorful header.
"""

import speech_recognition as sr
from colorama import init, Fore, Style
from audio_engine import build_tts_engine, speak, listen
from command_parser import handle_command

# Initialize colorama for Windows
init(autoreset=True)


def print_header():
    """Prints a nice header for the Voice Assistant in orange."""
    border_color = Fore.LIGHTYELLOW_EX
    text_color = Fore.LIGHTYELLOW_EX

    print(border_color + "=" * 50 + Style.RESET_ALL)
    print(text_color + "            🎤 Voice Assistant" + Style.RESET_ALL)
    print(border_color + "=" * 50 + Style.RESET_ALL)
    print()  # blank line


def main():
    engine = build_tts_engine()
    recognizer = sr.Recognizer()

    # Print the fancy header (not spoken)
    print_header()

    # 👇 REMOVED the spoken greeting – no more "Advanced voice assistant ready..."
    # speak(engine, "Advanced voice assistant ready...")  # commented out

    while True:
        command = listen(recognizer)
        response, should_exit = handle_command(command, engine)
        speak(engine, response)
        if should_exit:
            break


if __name__ == "__main__":
    main()
