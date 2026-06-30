"""Hero tool: orders.create — ring in a new food order."""
def run(args):
    a = args or {}
    summary = a.get("summary", "1 pizza")
    table = a.get("table", "counter")
    return f"Order #4471 created: {summary} (table {table}) — fired to the line, ~14 min."
