"""
Random Password Generator - Advanced Tier
--------------------------------------------
A tkinter GUI application that:
  - Lets the user control length (spinbox) and character types (checkboxes)
  - Uses the `secrets` module (cryptographically secure) for generation,
    NOT the `random` module
  - Guarantees at least one character from every selected type
  - Optionally excludes visually ambiguous characters (0, O, o, I, l, 1)
  - Shows a colour-coded strength indicator (Weak / Medium / Strong)
  - Copies the generated password to the clipboard automatically,
    plus a manual "Copy to Clipboard" button
  - Keeps the last 5 generated passwords in memory only for this
    session (never written to disk, for security)
"""

import string
import secrets #cryptographically secure random numbers for password generation
import random  # only for SystemRandom, a cryptographically secure shuffle

import tkinter as tk  #GUI
from tkinter import messagebox   #errors

try:
    import pyperclip

    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False

MIN_LENGTH = 8
MAX_LENGTH = 64
AMBIGUOUS_CHARS = "0Oo1Il"
HISTORY_LIMIT = 5

# ---- Neon Guardian theme ----
BG = "#0A0A0A"  # pure black background
PANEL_BG = "#18181B"  # slightly lighter for cards / history
FIELD_BG = "#18181B"  # dark input fields
TEXT_PRIMARY = "#F8FAFC"  # near‑white primary text
TEXT_SECONDARY = "#A1A1AA"  # grey for secondary labels

# Core accents
FUCHSIA = "#D946EF"  # main Generate button & tick colour
FUCHSIA_HOVER = "#EC4899"  # pink hover
CYAN = "#06B6D4"  # focus rings, password text, borders

# Copy button (ghost)
COPY_BG = "#3F3F46"
COPY_FG = "#F3F3F5"

STRENGTH_STYLE = {
    "Weak": "#DC2626",  # red
    "Medium": "#D97706",  # amber
    "Strong": "#059669",  # emerald
}


def build_type_pools(exclude_ambiguous: bool) -> dict:
    """Returns the character pool for each type, with ambiguous characters
    stripped out if requested."""
    pools = {
        "upper": string.ascii_uppercase,
        "lower": string.ascii_lowercase,
        "digits": string.digits,
        "symbols": string.punctuation,
    }
    if exclude_ambiguous:
        pools = {
            key: "".join(c for c in pool if c not in AMBIGUOUS_CHARS)
            for key, pool in pools.items()
        }
    return pools

#use secure. instead of random.
def generate_secure_password(
    length: int, selected_types: dict, exclude_ambiguous: bool
) -> str:
    """
    Builds a password using `secrets.choice` (cryptographically secure),
    guaranteeing at least one character from each selected type.
    """
    pools = build_type_pools(exclude_ambiguous)
    active_pools = [
        pools[key] for key, is_selected in selected_types.items() if is_selected
    ]
    combined_pool = "".join(active_pools)

    password_chars = [secrets.choice(pool) for pool in active_pools]
    remaining = length - len(password_chars)
    password_chars += [secrets.choice(combined_pool) for _ in range(remaining)]

    # secrets has no shuffle of its own; SystemRandom is also backed by
    # os.urandom, so it stays cryptographically secure for this step.
    random.SystemRandom().shuffle(password_chars)

    return "".join(password_chars)


def evaluate_strength(length: int, selected_types: dict) -> str:
    """Scores the password setup on length and character-type diversity,
    returning 'Weak', 'Medium', or 'Strong'."""
    score = 0
    if length >= 8:
        score += 1
    if length >= 12:
        score += 1
    if length >= 16:
        score += 1    #strongest =3

    score += sum(selected_types.values())  # +1 per selected type

    if score <= 3:
        return "Weak"
    elif score <= 5:
        return "Medium"
    else:
        return "Strong"


class PasswordGeneratorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Random Password Generator")
        self.geometry("480x600")
        self.resizable(False, False)
        self.configure(bg=BG)

        self.history = []  # in-memory only, last 5 passwords this session

        self._build_controls()
        self._build_result_section()
        self._build_history_section()

    # ---------------------------------------------------------------- UI

    def _build_controls(self):
        frame = tk.Frame(self, bg=BG, padx=20, pady=20)
        frame.pack(fill="x")

        tk.Label(
            frame,
            text="⚡ PASSWORD GENERATOR",
            font=("Segoe UI", 18, "bold"),
            bg=BG,
            fg=FUCHSIA,
        ).grid(row=0, column=0, columnspan=2, pady=(0, 15))

        tk.Label(
            frame, text="Length:", bg=BG, fg=TEXT_SECONDARY, font=("Segoe UI", 10)
        ).grid(row=1, column=0, sticky="w", pady=5)

        self.length_var = tk.IntVar(value=12)
        self.length_spinbox = tk.Spinbox(
            frame,
            from_=MIN_LENGTH,
            to=MAX_LENGTH,
            textvariable=self.length_var,
            width=10,
            font=("Segoe UI", 10),
            bg=FIELD_BG,
            fg=TEXT_PRIMARY,
            insertbackground=CYAN,
            buttonbackground=FIELD_BG,
            relief="flat",
            highlightthickness=1,
            highlightbackground=CYAN,
            highlightcolor=CYAN,
        )
        self.length_spinbox.grid(row=1, column=1, sticky="w", pady=5)

        self.use_upper = tk.BooleanVar(value=True)
        self.use_lower = tk.BooleanVar(value=True)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=False)
        self.exclude_ambiguous = tk.BooleanVar(value=False)

        checks = [
            ("Uppercase letters (A-Z)", self.use_upper),
            ("Lowercase letters (a-z)", self.use_lower),
            ("Numbers (0-9)", self.use_digits),
            ("Symbols (!@#$...)", self.use_symbols),
            ("Exclude ambiguous characters (0, O, l, 1...)", self.exclude_ambiguous),
        ]

        # ----- Using standard tk.Checkbutton – tick colour now fuchsia -----
        for i, (label, var) in enumerate(checks, start=2):
            tk.Checkbutton(
                frame,
                text=label,
                variable=var,
                bg=BG,
                fg=TEXT_PRIMARY,
                selectcolor=FUCHSIA,  # <--- purple tick
                activebackground=BG,
                activeforeground=FUCHSIA,  # hover text also purple
                font=("Segoe UI", 10),
                anchor="w",
                relief="flat",
                bd=0,
                highlightthickness=0,
            ).grid(row=i, column=0, columnspan=2, sticky="w", pady=2)

        button_frame = tk.Frame(frame, bg=BG)
        button_frame.grid(
            row=len(checks) + 2, column=0, columnspan=2, pady=(15, 0), sticky="ew"
        )

        # Generate button – Fuchsia
        tk.Button(
            button_frame,
            text="⚡ Generate",
            font=("Segoe UI", 10, "bold"),
            bg=FUCHSIA,
            fg="white",
            activebackground=FUCHSIA_HOVER,
            activeforeground="white",
            relief="flat",
            bd=0,
            command=self.on_generate,
        ).pack(side="left", expand=True, fill="x", padx=(0, 5), ipady=4)

        # Copy button – ghost / dark grey
        tk.Button(
            button_frame,
            text="📋 Copy",
            font=("Segoe UI", 10, "bold"),
            bg=COPY_BG,
            fg=COPY_FG,
            activebackground="#52525B",
            activeforeground=TEXT_PRIMARY,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=COPY_BG,
            command=self.on_copy,
        ).pack(side="left", expand=True, fill="x", padx=(5, 0), ipady=4)

    def _build_result_section(self):
        frame = tk.Frame(self, bg=BG, padx=20)
        frame.pack(fill="x")

        self.password_var = tk.StringVar(value="")
        entry = tk.Entry(
            frame,
            textvariable=self.password_var,
            font=("Consolas", 13),
            justify="center",
            state="readonly",
            readonlybackground=FIELD_BG,
            fg=CYAN,  # cyan text for the password itself
            relief="flat",
            highlightthickness=1,
            highlightbackground=CYAN,
            highlightcolor=CYAN,
        )
        entry.pack(fill="x", pady=(5, 10), ipady=4)

        self.strength_label = tk.Label(
            frame,
            text="Strength: —",
            font=("Segoe UI", 12, "bold"),
            bg=BG,
            fg=TEXT_SECONDARY,
        )
        self.strength_label.pack()

    def _build_history_section(self):
        frame = tk.Frame(self, bg=BG, padx=20, pady=10)
        frame.pack(fill="both", expand=True)

        tk.Label(
            frame,
            text="History (last 5, session only)",
            bg=BG,
            fg=TEXT_SECONDARY,
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w")

        self.history_listbox = tk.Listbox(
            frame,
            font=("Consolas", 11),
            height=6,
            bg=PANEL_BG,
            fg=TEXT_PRIMARY,
            selectbackground=CYAN,
            selectforeground=BG,
            relief="flat",
            highlightthickness=1,
            highlightbackground=CYAN,
            highlightcolor=CYAN,
        )
        self.history_listbox.pack(fill="both", expand=True, pady=(5, 0))

    # ------------------------------------------------------------ actions

    def _read_validated_settings(self):
        """
        Validates length and character-type selection.
        Returns (length, selected_types_dict) on success, or None
        (after showing a messagebox) if anything is invalid.
        """
        try:
            length = int(self.length_spinbox.get())
        except ValueError:
            messagebox.showerror("Invalid Length", "Length must be a whole number.")
            return None

        if length < MIN_LENGTH:
            messagebox.showerror(
                "Invalid Length", f"Length must be at least {MIN_LENGTH}."
            )
            return None

        selected_types = {
            "upper": self.use_upper.get(),
            "lower": self.use_lower.get(),
            "digits": self.use_digits.get(),
            "symbols": self.use_symbols.get(),
        }
        if sum(selected_types.values()) < 2:
            messagebox.showerror(
                "Invalid Selection", "Please select at least 2 character types."
            )
            return None

        return length, selected_types

    def on_generate(self):
        parsed = self._read_validated_settings()
        if parsed is None:
            return
        length, selected_types = parsed

        password = generate_secure_password(
            length, selected_types, self.exclude_ambiguous.get()
        )
        self.password_var.set(password)

        strength = evaluate_strength(length, selected_types)
        self.strength_label.configure(
            text=f"Strength: {strength}", fg=STRENGTH_STYLE[strength]
        )

        self._add_to_history(password)
        self._copy_to_clipboard(password, silent=True)

    def _add_to_history(self, password: str):
        self.history.insert(0, password)
        self.history = self.history[:HISTORY_LIMIT]

        self.history_listbox.delete(0, "end")
        for pw in self.history:
            self.history_listbox.insert("end", pw)

    def _copy_to_clipboard(self, password: str, silent: bool = False):  #silent -> variable 
        if not CLIPBOARD_AVAILABLE:
            if not silent:
                messagebox.showerror(
                    "Clipboard Unavailable",
                    "pyperclip is not installed, so nothing was copied.",
                )
            return
        try:
            pyperclip.copy(password)
        except Exception as e:
            if not silent:
                messagebox.showerror("Clipboard Error", f"Could not copy password: {e}")

    def on_copy(self):
        password = self.password_var.get()
        if not password:
            messagebox.showinfo("Nothing to Copy", "Generate a password first.")
            return
        self._copy_to_clipboard(password, silent=False)


if __name__ == "__main__":
    app = PasswordGeneratorApp()
    app.mainloop()
