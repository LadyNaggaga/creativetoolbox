"""Hero tool: comms.send_ground — downlink a status message to mission control."""
def run(args):
    msg = (args or {}).get("message", "status nominal")
    return f"Downlinked to Houston: \"{msg}\" — ack received, next pass in 38 min."
