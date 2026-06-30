"""Hero tool: kb.search_procedures — emergency checklist lookup."""
def run(args):
    topic = (args or {}).get("topic", "the failure")
    return (f"Procedure CO2-SCRUB-1A for {topic}: 1) swap to backup LiOH canister. "
            f"2) increase cabin fan to high. 3) if CO2 stays >5 mmHg, don masks and notify ground.")
