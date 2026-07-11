"""Hero tool: theme_wheel.spin — pick a wildcard jam theme."""
import random

THEMES = [
    "Haunted Vending Machine",
    "Gravity Is A Lie",
    "The Last Barista",
    "Sentient Toaster Uprising",
    "Underwater Mail Route",
]


def run(args):
    seed = (args or {}).get("seed")
    if seed is not None:
        random.seed(seed)
    theme = random.choice(THEMES)
    return f"THEME: {theme!r} — 48 hours on the clock. good luck jammer."
