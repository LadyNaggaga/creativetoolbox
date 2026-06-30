# I gave my flight-control agent 24 tools and it only ever saw two

I wired a fake space station up to a Toolbox on Foundry, dropped 24 tools into the box, and watched the agent fly a whole emergency with exactly **two** tools in its context the entire time. The principle the demo is built around: **big box, tiny context.**

## What it does

`space-mission-control` is a tiny, cloneable agent that runs a station emergency: the cabin gets stuffy, you need to drop orbit, power gets tight, the CO2 scrubber throws a scare, and you call it down to Houston. Five plain-English turns, each needing a *different* console. The whole thing runs locally with `make demo` — no Azure, no key, no token.

![demo](assets/demo.gif)

## The trick

The toolbox has `{"type": "toolbox_search_preview"}` turned on. That hides every real tool and gives the model two meta-tools instead: `tool_search` (describe what you need in words) and `call_tool` (invoke it by name). So no matter how many consoles sit behind the box, the model context stays flat. One tool, `telemetry.read_o2`, is **pinned** — always visible — which is why the counter reads `2 (+1 pinned)`.

```
>_ user: "wait — what's the procedure if the CO2 scrubber fails?"
   [tool_search] query: "look up the emergency checklist procedure for a scrubber failure"   // round-trip #4
   [matched]     kb.search_procedures, cargo.manifest, nav.plot_burn, comms.send_ground
   [call_tool]   kb.search_procedures({ "topic": "CO2 scrubber failure" })
   => Procedure CO2-SCRUB-1A: 1) swap to backup LiOH canister. 2) cabin fan high. 3) ...
tools in box: 24   ·   tools in model context: 2 (+1 pinned)
```

The matching is **not faked**: the local emulator ranks the actual tool descriptions, and `kb.search_procedures` surfaces first every time because its description speaks the operator vocabulary ("what do we do if X fails").

## The numbers

- Tools in the box: **24**
- Tools in the model context: **2** (`tool_search` + `call_tool`) + **1 pinned**
- `tool_search` round-trips: **5** (one per turn, each a different query)
- Lines of agent code that changed when I added a 25th tool: **0**

## The part people miss

Open `mock-backends/tools.json`, add a tool, rerun. The agent code never changes — and the context counter still says 2. That is the whole managed-toolbox thesis: you reshape the tools without touching the agent. The cost of the 24th tool, to the model, is nothing.

## Clone it

```bash
git clone <repo> && cd space-mission-control && make demo      # python
make demo-dotnet                                                # C#, identical output
```

Python and C# produce the exact same trace — the box and the scenario are shared; only the language of the client differs.

## Honest caveats

Tool Search is in preview. It buys flat context at the price of one search round-trip per intent, and match quality is *entirely* as good as your tool descriptions — a vague description and the right console will not surface on camera. Worth it the moment a box has more than ~10 tools. Below that, just hand the model the tools.
