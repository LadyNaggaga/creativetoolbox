"""
The scenario. Each turn = a relatable user message + the natural-language intent the agent
expresses to tool_search + the tool it then calls.

In SCRIPTED mode (default, zero model key) the player sends these real queries to the emulator,
so the MATCHES and RESULTS are genuinely produced by the emulator's ranking — only the intent
strings are pre-written. In LIVE mode a real model writes these itself.

Replace this with your theme's 3-5 turns. Make each turn need a DIFFERENT capability so
tool_search fires with different queries. Include one 'obvious to a human, needs discovery for the
model' moment — that's the screenshot.
"""

TURNS = [
    {
        "user": "the cabin feels stuffy up here — is the air actually okay?",
        "intent": "check breathable cabin oxygen air quality and life support status",
        "call": {"name": "telemetry.read_o2", "arguments": {}},
    },
    {
        "user": "we need to drop into a lower orbit before the next pass",
        "intent": "plan an engine burn to lower our orbit altitude",
        "call": {"name": "nav.plot_burn", "arguments": {"target": "lower orbit"}},
    },
    {
        "user": "power's getting tight with all the heaters running",
        "intent": "rebalance the electrical power budget and shed non-critical load",
        "call": {"name": "power.balance_load", "arguments": {}},
    },
    {
        "user": "wait — what's the procedure if the CO2 scrubber fails?",
        "intent": "look up the emergency checklist procedure for a scrubber failure",
        "call": {"name": "kb.search_procedures", "arguments": {"topic": "CO2 scrubber failure"}},
    },
    {
        "user": "ok, tell Houston we're on top of it",
        "intent": "send a status message down to houston ground control",
        "call": {"name": "comms.send_ground",
                 "arguments": {"message": "Cabin air trending up on CO2; running scrub procedure, all nominal."}},
    },
]
