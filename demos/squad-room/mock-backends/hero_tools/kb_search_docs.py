"""Hero tool: kb.search_docs — researcher finds existing patterns in the codebase/docs."""
def run(args):
    topic = (args or {}).get("topic", "the topic")
    return (f"Found 3 docs on {topic}: ThemeProvider in src/ui/theme.tsx wraps the app; "
            f"colors already read from CSS variables; no dark palette defined yet.")
