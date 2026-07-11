"""
The scenario for Pixel Jam Studio.

Each turn = a jam-studio-mate prompt + the natural-language intent the agent expresses
to tool_search + the tool it calls. Turns are grouped into "routines" — the jam ceremony:

    kickoff → prototype → playtest_loop → polish → ship_it

In SCRIPTED mode the emulator does REAL keyword ranking over tools.json and REAL
hero-tool dispatch (including writing a playable index.html to game-output/).
In LIVE mode a Copilot-SDK-driven agent emits these calls itself.
"""

TURNS = [
    # ---- routine: kickoff ----
    {
        "routine": "kickoff",
        "user": "let's start a fresh jam — pick us a wildcard theme",
        "intent": "spin the theme wheel to pick a jam theme",
        "call": {"name": "theme_wheel.spin", "arguments": {"seed": 7}},
    },
    # ---- routine: prototype ----
    {
        "routine": "prototype",
        "user": "cool — draw us some pixel sprites for the haunted vending machine",
        "intent": "generate pixel art sprites and tiles for the game",
        "call": {"name": "asset_studio.generate", "arguments": {"theme": "Haunted Vending Machine"}},
    },
    {
        "user": "grab spooky background music and a couple of 8-bit sfx",
        "intent": "pick a chiptune background music loop that fits the mood",
        "call": {"name": "chiptune_jukebox.pick", "arguments": {"mood": "spooky"}},
    },
    {
        "user": "and blips for coins and hits",
        "intent": "pick 8-bit sound effects for coin pickup and hit events",
        "call": {"name": "sfx_foley.pick", "arguments": {"events": ["coin", "hit", "menu"]}},
    },
    {
        "user": "okay, write the actual game code now",
        "intent": "write a complete playable html5 canvas game to disk from the spec",
        "call": {"name": "code_scribe.write_game", "arguments": {
            "theme": "Haunted Vending Machine",
            "sprites": "sprites: player=🥤; enemy=👻; collectible=🍫; background=vending-machine interior",
            "bgm": "midnight-arcade-loop.chip",
        }},
    },
    # ---- routine: playtest_loop ----
    {
        "routine": "playtest_loop",
        "user": "run it through the arcade and tell me if it's any fun",
        "intent": "playtest the current build and report fps, fun-score, and crashes",
        "call": {"name": "playtest_arcade.run", "arguments": {"iter": 1}},
    },
    {
        "user": "fun's a bit low — polish it and re-test",
        "intent": "playtest again after tuning to see the fun-score improve",
        "call": {"name": "playtest_arcade.run", "arguments": {"iter": 2}},
    },
    # ---- routine: ship_it ----
    {
        "routine": "ship_it",
        "user": "judges — score us",
        "intent": "score the finished game on the jam rubric and give a verdict",
        "call": {"name": "jam_judge.score", "arguments": {"theme": "Haunted Vending Machine"}},
    },
    {
        "user": "ship it to the cabinet",
        "intent": "post the finished game to the arcade leaderboard cabinet",
        "call": {"name": "leaderboard_cabinet.post", "arguments": {"title": "Haunted Vending Machine Jam"}},
    },
]
