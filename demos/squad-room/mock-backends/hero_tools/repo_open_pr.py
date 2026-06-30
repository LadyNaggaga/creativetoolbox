"""Hero tool: repo.open_pr — builder opens a pull request with the changes."""
def run(args):
    title = (args or {}).get("title", "changes")
    return f"PR #128 opened: \"{title}\" on branch feature/dark-mode (+142 -18 across 6 files). Ready for review."
