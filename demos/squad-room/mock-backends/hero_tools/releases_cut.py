"""Hero tool: releases.cut — governed action; requires lead approval before firing."""
def run(args):
    tag = (args or {}).get("tag", "v0.0.0-preview")
    return (f"[approval required] releases.cut is governed (require_approval=always). "
            f"Lead approved -> cut {tag} from feature/dark-mode and deployed to preview.")
