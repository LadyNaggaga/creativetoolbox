"""Hero tool: jam_judge.score — rubric-based score + a jam-site style blurb."""


def run(args):
    theme = (args or {}).get("theme", "the theme")
    return ("jam_judge: originality=28/30 · polish=27/30 · theme_fit=32/40 · TOTAL=87/100  "
            f"— \"surprisingly spooky little arcade thing; the {theme.lower()} bit lands. more juice next time.\"")
