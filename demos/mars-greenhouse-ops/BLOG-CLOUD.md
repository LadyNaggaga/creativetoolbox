# I shipped the greenhouse agent to Mars, and it wrote its own tool search

The [local demo](BLOG.md) put 32 dome consoles behind one endpoint and let the agent run a day in the greenhouse with two tools in context. That version was an emulator on my laptop. This one is **deployed** — a real MCP server on Azure Container Apps, a real Foundry Toolbox with Tool Search, and a hosted agent running on Microsoft Foundry — and the search query below is the one the model *actually wrote*, pulled straight off the wire.

Same principle: **big box, tiny context.** New part: it's live, and I can hand you the endpoint.

## The shape of it

Three moving pieces, each a supported product surface, wired end to end:

```
crew  ──▶  hosted agent (Foundry, gpt-4o)  ──▶  Toolbox + Tool Search (Foundry)  ──▶  MCP server (Azure Container Apps)
                                                     tool_search / call_tool            sensors · irrigation · power · guides · crew
```

- The **hero tools** (`sensors.read_air`, `irrigation.schedule`, `power.balance_load`, `kb.search_guides`, `notify.crew`, …) run as a FastMCP streamable-http server on **Azure Container Apps** — the exact same `hero_tools/` logic the local demo uses, just containerized and public.
- A **Foundry Toolbox** (`mars-greenhouse-ops`, v1) wraps that server behind one MCP endpoint with `{"type": "toolbox_search_preview"}` on, so the model sees only `tool_search`, `call_tool`, and the one pinned air readout.
- A **hosted agent** (the Agent Framework `04-foundry-toolbox` sample, customized for the dome) connects to that one toolbox endpoint. I didn't write the MCP plumbing, the `Foundry-Features` header, the token dance, or the tool loop — the sample and the platform did.

## The money shot: the model's own search query

I asked the *deployed* agent one plain question and read the trace back:

```
>_ user: "Prepping bed 3 for basil. How deep do I sow the seeds and what spacing?"

   [tool_search]  query: "how deep to sow basil seeds and spacing recommendations"   ← the model wrote this
   [matched]      marsgreenhouse.kb_search_guides
   [call_tool]    marsgreenhouse.kb_search_guides({ "query": "how deep to sow basil seeds and spacing recommendations" })
   => "Sow basil 6 mm deep, 20 cm spacing. Germinates in 5-7 days at 21°C.
       Pinch tips at 15 cm for bushier growth and a larger harvest."

   [assistant]    "Sow basil seeds 6 mm deep with 20 cm spacing. They germinate in
                   5-7 days at 21°C. Pinch the tips when plants reach 15 cm."

   tools in box: 32   ·   tools in the model's context: 2
```

Nobody scripted that `tool_search` string. The model read the intent, described what it needed in its own words, and the toolbox ranked the real tool descriptions to surface `kb_search_guides` out of 32 consoles. That's the whole pitch: you don't inline 32 schemas into the prompt and pray — the model *searches* the box.

## The approval gate, live

`power.balance_load` carries `require_approval: always` — rebalancing the dome can dim grow lights and touch the crops, so it's not something an agent should do on its own say-so. On the deployed agent:

```
>_ user: "The grow lights are drawing too much. Rebalance the dome power load
          to shed non-critical draw."

   [assistant]  "Rebalancing the dome's power load to prioritize grow lights and shed
                 non-critical draw requires notifying the crew lead for approval since
                 it could impact other systems. … Let me know if I should proceed."
```

The guard fires. The agent recognizes the action is gated and stops for a human instead of shedding load on its own. Human-in-the-loop by design — the same spine as the pizza oven, different theme.

## It's deployed — here's the endpoint

This isn't a `make demo` emulator. It's a running agent you can hit:

- **Agent playground:** open it in the [Foundry portal](https://ai.azure.com/nextgen/r/LThb9AdWSnaqlSi_ntO2JQ,rg-mars-greenhouse-ops-o0n1ya,,ai-account-j47qdykunqcdo,ai-project-mars-greenhouse-ops-o0n1ya/build/agents/mars-greenhouse-ops/build?version=1) and chat with it.
- **Responses endpoint:** `POST …/agents/mars-greenhouse-ops/endpoint/protocols/openai/responses`
- **From your terminal:**

```bash
azd ai agent invoke mars-greenhouse-ops \
  "Prepping bed 3 for basil. How deep do I sow the seeds and what spacing?"
```

Every call lands a trace in Application Insights (this run: `caresp_4acc83a2eedc0bc70043qQBM4MhYs8fmAbqmrF9G2dV68j4QnM`), so the `tool_search` query, the `call_tool` pick, and the latency are all real, inspectable numbers — not screenshots.

## How I built it (the honest version)

The happy path is `azd ai agent init` → `azd provision` → `azd deploy`. Same two environment snags as the pizza build, same two fixes — so this time they cost me minutes, not hours:

1. **`azd provision` wouldn't run** — it kept trying to resolve my principal against a dead subscription in a tenant I'd lost access to, and hard-failed before touching the template. Fix: provision the Bicep directly with `az deployment sub create`, which uses a clean subscription list. The Foundry project, gpt-4o deployment, ACR, and App Insights all came up in one shot.
2. **`azd deploy` code path is region-gated** — direct ZIP/code deploy is only supported in a few regions (not `eastus2`), and I had no local Docker. Fix: container deploy with `docker: remoteBuild: true` in `azure.yaml`, so azd builds the image on ACR instead of my machine. Deployed in **2m40s**.

Neither is a Toolbox or agent problem — they're auth/region/tooling papercuts. The product path itself (toolbox create → agent connects → Tool Search ranks → guarded call pauses) worked exactly as designed.

## Honest cloud caveats

- **Preview.** Tool Search and hosted agents are in preview; endpoints and flags move.
- **One search round-trip per intent.** You trade a flat, cheap context for a search hop. Worth it past ~5 tools; overkill below that. At 32 consoles it's an easy call.
- **Matching is only as good as the descriptions.** `additional_search_text` (the colloquial "how do I grow / how deep to sow" padding) is doing real ranking work — without it, "grow guide" doesn't reliably beat the sensor and irrigation tools.
- **Cold start + container tier.** The agent runs on a small container; first call after idle is slower.
- **The zero-Azure path still exists.** If you don't want to spin up Azure, `make demo` runs the whole story locally against the emulator — same tools, same script, no cloud.

## What carries forward

This is the second demo on the exact same spine as [pizza-shop-ops](../pizza-shop-ops/BLOG-CLOUD.md) — hero tools on Container Apps, a Foundry Toolbox with Tool Search, a hosted agent that never sees the full list. Two demos in, the plumbing is boilerplate; only the theme and the story change. `squad-room` is next, and it adds the enterprise governance layer (APIM + an API Center private MCP registry) on top of this same foundation.
