"""Hero tool: asset_studio.generate — pick pixel-art sprites for a theme."""

PACKS = {
    "haunted vending machine": {
        "player":     "🥤 blue can, 8x8, 2-frame idle",
        "enemy":      "👻 pixel ghost, 8x8, floaty bob",
        "collectible":"🍫 candy bar, 6x6, sparkle",
        "background": "vending-machine interior, dim purple neon, scanlines",
    },
    "gravity is a lie": {
        "player":     "🧑\u200d🚀 astronaut, 8x8, thruster puff",
        "enemy":      "🪨 asteroid, 10x10, tumble",
        "collectible":"💎 crystal, 6x6, glow",
        "background": "starfield with drifting planetoids",
    },
}


def run(args):
    theme = (args or {}).get("theme", "").lower()
    pack = PACKS.get(theme) or next(iter(PACKS.values()))
    return "sprites: " + "; ".join(f"{k}={v}" for k, v in pack.items())
