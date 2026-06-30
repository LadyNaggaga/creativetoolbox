"""Hero tool: oven.set_temp — guarded action; requires shift-lead approval before firing."""
def run(args):
    a = args or {}
    temp = a.get("temp", 475)
    style = a.get("style", "pizza")
    return (f"[approval required] oven.set_temp is gated (require_approval=always). "
            f"Shift-lead approved -> deck oven preheating to {temp}F for {style}. ETA to temp: 12 min.")
