"""Hero tool: telemetry.read_o2 — cabin oxygen / air-quality reading (pinned tool)."""
def run(args):
    return ("ppO2 20.4 kPa (nominal 19.5-23.1) | CO2 4.1 mmHg rising | "
            "cabin air 'stuffy' confirmed: CO2 trend up, scrubber bed near saturation.")
