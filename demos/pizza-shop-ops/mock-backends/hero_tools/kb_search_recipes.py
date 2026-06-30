"""Hero tool: kb.search_recipes — recipe / dough formula lookup."""
def run(args):
    dish = (args or {}).get("dish", "the dough")
    return (f"Recipe for {dish}: 00 flour, 62% hydration, 2.8% salt, 0.2% fresh yeast; "
            f"bulk 2h then ball, proof 6-8h at room temp. Bake 90s at 475F.")
