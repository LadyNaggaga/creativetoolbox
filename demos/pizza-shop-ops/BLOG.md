# I put 18 tools behind one endpoint and my pizza agent saw two

I gave a Friday-night pizza shop an AI line cook, stuffed 18 tools behind a single Toolbox endpoint on Foundry, and the agent ran the whole rush with exactly **two** tools in its context. The principle the demo is built around: **big box, tiny context.**

## What it does

`pizza-shop-ops` runs the dinner rush: check the mozzarella, fire the oven, pull up a dough recipe, ring in table 12, and push three deliveries out the door. Five plain-English turns, five different stations. It runs locally with `make demo` — no Azure, no key.

![demo](assets/demo.gif)

## The trick

The toolbox has `{"type": "toolbox_search_preview"}` on, so the model only ever sees `tool_search` (say what you need) and `call_tool` (run it). Eighteen stations behind the box, two tools in front of the model. This theme also leans into **approval gating**: `oven.set_temp` carries `require_approval: always`, so firing the deck oven pauses for a shift-lead sign-off before it runs.

```
>_ user: "fire up the deck oven for Neapolitan pies"
   [tool_search] query: "set the oven temperature and preheat it for a style of pizza"   // round-trip #2
   [matched]     oven.set_temp, oven.read_temp, delivery.assign_driver, inventory.check_stock
   [call_tool]   oven.set_temp({ "temp": 475, "style": "Neapolitan" })
   => [approval required] oven.set_temp is gated. Shift-lead approved -> preheating to 475F.
tools in box: 18   ·   tools in model context: 2
```

The matching is real: the emulator ranks the actual descriptions, and `oven.set_temp` wins over the near-miss `oven.read_temp` because its description and `additional_search_text` carry the colloquial "fire up / crank up / turn on the oven."

## The numbers

- Tools in the box: **18**
- Tools in the model context: **2** (`tool_search` + `call_tool`)
- `tool_search` round-trips: **5**
- Guarded tools that paused for approval: **1** (`oven.set_temp`)
- Lines of agent code that changed when I added a 19th tool: **0**

## The part people miss

Add a tool to `mock-backends/tools.json`, rerun — the agent code is untouched and the counter still says 2. Reshape the menu of tools without rewriting the cook. That is the managed-toolbox payoff.

## Clone it

```bash
git clone <repo> && cd pizza-shop-ops && make demo      # python
make demo-dotnet                                         # C#, identical output
```

## Honest caveats

Tool Search is in preview. You pay one search round-trip per intent, and the right station only surfaces if its description matches how people actually talk — `additional_search_text` is doing real work here. Approval gating adds a human in the loop by design; that is a feature, not latency to optimize away.
