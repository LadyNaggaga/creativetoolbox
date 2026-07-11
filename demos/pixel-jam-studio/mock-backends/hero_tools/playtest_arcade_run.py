"""Hero tool: playtest_arcade.run — headless playtest of the current build."""


def run(args):
    a = args or {}
    iteration = int(a.get("iter", 1))
    # iteration 1 = quirky, iteration 2 = solid — shows the patch loop
    if iteration <= 1:
        return "playtest: fps=59.2, fun=6.4/10, crashes=0, notes=\"enemies clump on left; item spawn feels stingy\""
    return "playtest: fps=60.0, fun=8.7/10, crashes=0, notes=\"clean run, good juice, ghosts feel fair\""
