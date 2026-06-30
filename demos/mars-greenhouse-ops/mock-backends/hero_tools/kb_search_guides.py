"""Hero tool: kb.search_guides — planting / plant-care guide lookup."""
def run(args):
    topic = (args or {}).get("topic", "this crop")
    return (f"Guide for {topic}: sow basil 6 mm deep, 20 cm spacing, germinates in 5-7 days at 21 C. "
            f"Pinch the tips at 15 cm for bushier plants and a bigger harvest.")
