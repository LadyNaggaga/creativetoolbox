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
        "user": "morning! how's the air in the dome today — are the plants happy?",
        "intent": "check the greenhouse air: CO2, oxygen and humidity for the plants",
        "call": {"name": "sensors.read_air", "arguments": {}},
    },
    {
        "user": "the tomatoes in bed 3 look a little thirsty — can we give them a drink?",
        "intent": "schedule a drip-watering cycle for a planting bed",
        "call": {"name": "irrigation.schedule", "arguments": {"bed": "bed 3"}},
    },
    {
        "user": "the grow-lights are pulling a lot of juice — are we ok on power?",
        "intent": "rebalance the greenhouse power budget across the grow-lights",
        "call": {"name": "power.balance_load", "arguments": {}},
    },
    {
        "user": "wait — how deep should I actually be sowing the basil seeds?",
        "intent": "look up the planting guide for basil sowing depth and spacing",
        "call": {"name": "kb.search_guides", "arguments": {"topic": "basil"}},
    },
    {
        "user": "nice — let the crew know the harvest is coming along great",
        "intent": "post a friendly harvest update to the colony crew board",
        "call": {"name": "notify.crew",
                 "arguments": {"message": "Dome air dialed in, bed 3 watered, basil on the way — first salad harvest in a few days!"}},
    },
]
