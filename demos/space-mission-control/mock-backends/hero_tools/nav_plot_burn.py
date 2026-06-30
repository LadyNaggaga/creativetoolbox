"""Hero tool: nav.plot_burn — compute an orbit-change burn."""
def run(args):
    target = (args or {}).get("target", "lower orbit")
    return (f"Burn plan for {target}: prograde/retrograde dV 18.3 m/s, "
            f"burn duration 42 s, ignition T+00:11:30 over the Pacific. Reaffirm before commit.")
