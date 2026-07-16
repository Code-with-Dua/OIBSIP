"""
Random Password Generator - Beginner Tier
--------------------------------------------
Command-line tool that:
  - Prompts for a desired password length (minimum 8 enforced)
  - Prompts which character types to include (at least 2 required)
  - Generates a password guaranteed to contain every selected type
  - Validates all input with helpful error messages
  - Lets the user generate more passwords without restarting

Colours are added with `colorama`, which translates ANSI colour codes
into the right calls for Windows Command Prompt as well as Mac/Linux
terminals - plain ANSI codes alone don't always render on older cmd.exe.
"""

import random
import string

from colorama import init, Fore, Style

init(autoreset=True)  # every print resets colour automatically afterwards

MIN_LENGTH = 8


def get_valid_length() -> int:
    """Repeatedly asks for a password length until a valid one (>= 8) is given."""
    while True:
        raw_value = input(
            f"{Fore.CYAN}Password length (minimum {MIN_LENGTH}): {Style.RESET_ALL}"
        ).strip()
        try:
            length = int(raw_value)
        except ValueError:
            print(
                f"{Fore.RED}  ❌ '{raw_value}' is not a valid whole number. Try again.\n"
            )
            continue

        if length < MIN_LENGTH:
            print(
                f"{Fore.RED}  ❌ Length must be at least {MIN_LENGTH} characters. Try again.\n"
            )
            continue

        return length


def get_selected_types() -> dict:
    """
    Asks the user which character types to include (y/n each).
    Re-prompts the whole set if fewer than 2 types end up selected.
    """
    while True:
        print(f"\n{Fore.CYAN}Which character types should the password include?")
        use_upper = (
            input(f"{Fore.CYAN}  Uppercase letters (A-Z)? (y/n): {Style.RESET_ALL}")
            .strip()
            .lower()
            == "y"
        )
        use_lower = (
            input(f"{Fore.CYAN}  Lowercase letters (a-z)? (y/n): {Style.RESET_ALL}")
            .strip()
            .lower()
            == "y"
        )
        use_digits = (
            input(f"{Fore.CYAN}  Numbers (0-9)? (y/n): {Style.RESET_ALL}")
            .strip()
            .lower()
            == "y"
        )
        use_symbols = (
            input(f"{Fore.CYAN}  Symbols (!@#$...)? (y/n): {Style.RESET_ALL}")
            .strip()
            .lower()
            == "y"
        )

        selected_count = sum([use_upper, use_lower, use_digits, use_symbols])
        if selected_count < 2:
            print(f"{Fore.RED}  ❌ Please select at least 2 character types.\n")
            continue

        return {
            "upper": use_upper,
            "lower": use_lower,
            "digits": use_digits,
            "symbols": use_symbols,
        }


def generate_password(length: int, types: dict) -> str:
    """
    Builds a password of the given length that is guaranteed to contain
    at least one character from every selected type.
    """
    type_pools = {
        "upper": string.ascii_uppercase,
        "lower": string.ascii_lowercase,
        "digits": string.digits,
        "symbols": string.punctuation,
    }

    active_pools = [pool for key, pool in type_pools.items() if types[key]]
    combined_pool = "".join(active_pools)

    # Step 1: guarantee one character from each selected type
    password_chars = [random.choice(pool) for pool in active_pools]

    # Step 2: fill the rest of the length from the combined pool
    remaining = length - len(password_chars)
    password_chars += [random.choice(combined_pool) for _ in range(remaining)]

    # Step 3: shuffle so the guaranteed characters aren't always at the start
    random.shuffle(password_chars)

    return "".join(password_chars)


def main():
    print(Fore.YELLOW + Style.BRIGHT + "=" * 45)
    print(Fore.YELLOW + Style.BRIGHT + "        RANDOM PASSWORD GENERATOR")
    print(Fore.YELLOW + Style.BRIGHT + "=" * 45)

    while True:
        length = get_valid_length()
        types = get_selected_types()

        password = generate_password(length, types)

        print(Fore.YELLOW + "\n" + "-" * 45)
        print(f"{Fore.GREEN}{Style.BRIGHT}  Generated password: {password}")
        print(Fore.YELLOW + "-" * 45)

        again = (
            input(f"\n{Fore.CYAN}Generate another password? (y/n): {Style.RESET_ALL}")
            .strip()
            .lower()
        )
        if again != "y":
            print(f"\n{Fore.YELLOW}Thanks for using the Password Generator. Goodbye!")
            break


if __name__ == "__main__":
    main()
