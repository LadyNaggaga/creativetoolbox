"""Hero tool: chiptune_jukebox.pick — pick a looping BGM by mood."""

TRACKS = {
    "spooky":  "midnight-arcade-loop.chip (120bpm, Am)",
    "upbeat":  "coin-rush-loop.chip (160bpm, C)",
    "calm":    "moonlit-menu.chip (90bpm, F)",
    "space":   "orbital-drift.chip (110bpm, Dm)",
}


def run(args):
    mood = (args or {}).get("mood", "spooky").lower()
    return f"bgm: {TRACKS.get(mood, TRACKS['spooky'])}"
