"""Hero tool: irrigation.schedule — plan a drip-watering cycle for a bed."""
def run(args):
    bed = (args or {}).get("bed", "bed 3")
    return (f"Watering plan for {bed}: 1.8 L over 12 min of drip at 06:30, "
            f"soil-moisture target 65%. Next cycle in 2 days. Looking good!")
