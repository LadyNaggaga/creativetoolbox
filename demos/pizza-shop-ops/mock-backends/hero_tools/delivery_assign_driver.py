"""Hero tool: delivery.assign_driver — dispatch outgoing orders to a driver."""
def run(args):
    count = (args or {}).get("count", 3)
    return f"Assigned {count} orders to driver Mia on route R7 — dispatched, first drop ETA 18 min."
