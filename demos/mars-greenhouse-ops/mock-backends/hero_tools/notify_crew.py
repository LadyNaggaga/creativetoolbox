"""Hero tool: notify.crew — post a friendly status note to the colony board."""
def run(args):
    msg = (args or {}).get("message", "status nominal")
    return f"Posted to the colony board: \"{msg}\" — 3 crew thumbs-up, Mai is bringing the salad bowls."
