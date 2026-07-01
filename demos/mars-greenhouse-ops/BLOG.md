# I gave my greenhouse agent 32 tools and it only ever saw two

I wired a Mars colony greenhouse up to a Toolbox on Foundry, dropped 32 tools into the box, and watched the agent run a whole day in the dome with exactly **two** tools in its context the entire time. The principle the demo is built around: **big box, tiny context.**

## What it does

`mars-greenhouse-ops` is a tiny, cloneable agent that runs a cheerful day in a Mars greenhouse: you check the dome air, give the thirsty tomatoes a drink, balance the grow-lights against the solar budget, look up how deep to sow the basil, and post a harvest update to the crew. Five plain-English turns, each needing a *different* console. The whole thing runs locally with `make demo` — no Azure, no key, no token.

![demo](assets/demo.gif)

## The trick

The toolbox has `{"type": "toolbox_search_preview"}` turned on. That hides every real tool and gives the model two meta-tools instead: `tool_search` (describe what you need in words) and `call_tool` (invoke it by name). So no matter how many consoles sit behind the box, the model context stays flat. One tool, `sensors.read_air`, is **pinned** — always visible — which is why the counter reads `2 (+1 pinned)`.

```
>_ user: "wait — how deep should I actually be sowing the basil seeds?"
   [tool_search] query: "look up the planting guide for basil sowing depth and spacing"   // round-trip #4
   [matched]     kb.search_guides, kb.search_pests, harvest.log, seeds.plant
   [call_tool]   kb.search_guides({ "topic": "basil" })
   => Guide for basil: sow 6 mm deep, 20 cm spacing, germinates in 5-7 days at 21 C ...
tools in box: 32   ·   tools in model context: 2 (+1 pinned)
```

The matching is **not faked**: the local emulator ranks the actual tool descriptions, and `kb.search_guides` surfaces first every time because its description speaks the gardener's vocabulary ("how do I grow X", "how deep to sow").

## The numbers

- Tools in the box: **32**
- Tools in the model context: **2** (`tool_search` + `call_tool`) + **1 pinned**
- `tool_search` round-trips: **5** (one per turn, each a different query)
- Lines of agent code that changed when I added a 33rd tool: **0**

## The part people miss

Open `mock-backends/tools.json`, add a tool, rerun. The agent code never changes — and the context counter still says 2. That is the whole managed-toolbox thesis: you reshape the tools without touching the agent. The cost of the 32nd tool, to the model, is nothing.

## Clone it

```bash
git clone <repo> && cd mars-greenhouse-ops && make demo      # python
make demo-dotnet                                              # C#, identical output
```

Python and C# produce the exact same trace — the box and the scenario are shared; only the language of the client differs.

## Honest caveats

Tool Search is in preview. It buys flat context at the price of one search round-trip per intent, and match quality is *entirely* as good as your tool descriptions — a vague description and the right console will not surface on camera. Worth it the moment a box has more than ~10 tools. Below that, just hand the model the tools.
