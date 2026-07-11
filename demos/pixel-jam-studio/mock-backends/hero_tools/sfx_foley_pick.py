"""Hero tool: sfx_foley.pick — pick 8-bit SFX for common events."""


def run(args):
    events = (args or {}).get("events") or ["jump", "coin", "hit"]
    picked = {
        "jump":  "blip-up-C5",
        "coin":  "ding-E6-arpeggio",
        "hit":   "thud-noise-short",
        "menu":  "click-A4",
        "ghost": "wobble-descend",
    }
    out = {e: picked.get(e, "bleep-generic") for e in events}
    return "sfx: " + ", ".join(f"{k}={v}" for k, v in out.items())
