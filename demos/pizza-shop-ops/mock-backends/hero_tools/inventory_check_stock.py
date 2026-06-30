"""Hero tool: inventory.check_stock — current stock for an ingredient."""
def run(args):
    item = (args or {}).get("item", "that item")
    return f"{item}: 3.2 kg on hand (about 9 pies' worth) — enough for the rush, but reorder before close."
