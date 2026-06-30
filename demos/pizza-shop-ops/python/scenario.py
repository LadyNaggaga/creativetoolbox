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
        "user": "Friday rush is kicking off — are we good on mozzarella?",
        "intent": "check how much of an ingredient we have left in stock",
        "call": {"name": "inventory.check_stock", "arguments": {"item": "mozzarella"}},
    },
    {
        "user": "fire up the deck oven for Neapolitan pies",
        "intent": "set the oven temperature and preheat it for a style of pizza",
        "call": {"name": "oven.set_temp", "arguments": {"temp": 475, "style": "Neapolitan"}},
    },
    {
        "user": "remind me the dough hydration for Neapolitan",
        "intent": "look up the recipe and dough formula for a pizza",
        "call": {"name": "kb.search_recipes", "arguments": {"dish": "Neapolitan dough"}},
    },
    {
        "user": "table 12 wants a large pepperoni, get it in",
        "intent": "create a new food order with items and a table number",
        "call": {"name": "orders.create",
                 "arguments": {"summary": "1 large pepperoni", "table": "12"}},
    },
    {
        "user": "send the next three deliveries out",
        "intent": "assign a delivery driver to outgoing orders and dispatch them",
        "call": {"name": "delivery.assign_driver", "arguments": {"count": 3}},
    },
]
