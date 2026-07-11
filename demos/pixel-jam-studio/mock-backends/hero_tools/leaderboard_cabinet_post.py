"""Hero tool: leaderboard_cabinet.post — ship the game to the arcade cabinet."""


def run(args):
    a = args or {}
    title = a.get("title", "Untitled Jam Game")
    return f"leaderboard_cabinet: ✔ posted \"{title}\" to slot #042 — 3 jammers already watching."
