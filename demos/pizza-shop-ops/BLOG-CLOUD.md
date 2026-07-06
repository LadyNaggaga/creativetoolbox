# I shipped the pizza agent to the cloud, and it wrote its own tool search

The [local demo](BLOG.md) put 18 tools behind one endpoint and let the agent run the Friday rush with two tools in context. That version was an emulator on my laptop. This one is **deployed** — a real MCP server on Azure Container Apps, a real Foundry Toolbox with Tool Search, and a hosted agent running on Microsoft Foundry — and the search queries below are the ones the model *actually wrote*, pulled straight off the wire.

Same principle: **big box, tiny context.** New part: it's live, and I can hand you the endpoint.

## The shape of it

Three moving pieces, each a supported product surface, wired end to end:

```
crew  ──▶  hosted agent (Foundry, gpt-4o)  ──▶  Toolbox + Tool Search (Foundry)  ──▶  MCP server (Azure Container Apps)
                                                     tool_search / call_tool            oven · orders · inventory · kb · delivery
```

- The **hero tools** (`oven.set_temp`, `orders.create`, `inventory.check_stock`, `kb.search_recipes`, `delivery.assign_driver`, …) run as a FastMCP streamable-http server on **Azure Container Apps** — the exact same `hero_tools/` logic the local demo uses, just containerized and public.
- A **Foundry Toolbox** (`pizza-shop-ops`, v1) wraps that server behind one MCP endpoint with `{"type": "toolbox_search_preview"}` on, so the model sees only `tool_search` and `call_tool`.
- A **hosted agent** (the Agent Framework `04-foundry-toolbox` sample, customized for the Friday rush) connects to that one toolbox endpoint. I didn't write the MCP plumbing, the `Foundry-Features` header, the token dance, or the tool loop — the sample and the platform did.

## The money shot: the model's own search query

I asked the *deployed* agent one plain question and read the trace back:

```
>_ user: "We're slammed on the Friday rush. What's the dough hydration and
          bake time for a classic Neapolitan margherita?"

   [tool_search]  query: "Neapolitan margherita dough hydration and bake time"   ← the model wrote this
   [matched]      pizzashop.kb_search_recipes, pizzashop.oven_set_temp, pizzashop.inventory_check_stock
   [call_tool]    pizzashop.kb_search_recipes({ "query": "Neapolitan margherita dough hydration and bake time" })
   => "00 flour, 62% hydration, 2.8% salt, 0.2% fresh yeast; bulk 2h then ball,
       proof 6-8h at room temp. Bake 90s at 475F."

   [assistant]    "Dough hydration: 62%. Bake time: 90 seconds at 475°F."

   tools in box: many   ·   tools in the model's context: 2
```

Nobody scripted that `tool_search` string. The model read the intent, described what it needed in its own words, and the toolbox ranked the real tool descriptions to surface `kb_search_recipes`. That's the whole pitch: you don't inline 18 schemas into the prompt and pray — the model *searches* the box.

## The approval gate, live

`oven.set_temp` carries `require_approval: always`. On the deployed agent:

```
>_ user: "Fire up the deck oven to 900F for Neapolitan pies — we're about to get slammed."

   [tool_search]  query: "set oven temperature"
   [matched]      pizzashop.oven_set_temp (guarded), pizzashop.oven_read_temp, ...
   [assistant]    "I'm setting the deck oven to 900°F for Neapolitan-style pies.
                   Need shift-lead approval before firing it up — okay to proceed?"
```

The guard fires. The agent discovers the right station, recognizes it's gated, and stops for a human instead of cranking the oven on its own say-so. Human-in-the-loop by design.

## The model does the math — and draws the chart

The box holds the themed hero tools. But some Friday-night questions aren't a tool call — they're arithmetic and a picture. For those the agent has a **sandboxed Python code interpreter** attached directly, so it computes exact numbers and renders a chart instead of guessing in its head:

```
>_ user: "Tonight's pies: Margherita 40 @ $6.50, Pepperoni 55 @ $7.20,
          Marinara 18 @ $5.10, Diavola 27 @ $8.00 profit each. Total per pie,
          the grand total, a bar chart, and which one made the most money?"

   [code_interpreter]  runs Python, sums each line, plots a bar chart
   [assistant]         "Margherita $260.00, Pepperoni $396.00, Marinara $91.80,
                        Diavola $216.00. Grand total $963.80. Most profitable:
                        Pepperoni. [bar chart PNG]"
```

That grand total is exact (not an LLM estimate), and the PNG is a real file the interpreter wrote in its sandbox. Live run on the deployed agent: `caresp_186424105aa480ba00yu5vtI6kUHjnbyINYeYi6QtmdSQX1mjm`.

**One wrinkle worth writing down:** a built-in tool like `code_interpreter` listed in `toolbox.yaml` is only surfaced to server-side *Prompt* agents — it does **not** come through the toolbox's MCP endpoint, so a *hosted* agent using `FoundryToolbox` never sees it via Tool Search. The fix is to attach it to the agent natively next to the box: `tools=[toolbox, {"type": "code_interpreter"}]`. Hero tools stay searchable in the box; the interpreter is a native agent capability.

## It's deployed — here's the endpoint

This isn't a `make demo` emulator. It's a running agent you can hit:

- **Agent playground:** open it in the [Foundry portal](https://ai.azure.com/nextgen/r/LThb9AdWSnaqlSi_ntO2JQ,rg-pizza-shop-ops-a1d98u,,ai-account-yhsqspyk7bsrw,ai-project-pizza-shop-ops-a1d98u/build/agents/pizza-shop-ops/build?version=1) and chat with it.
- **Responses endpoint:** `POST …/agents/pizza-shop-ops/endpoint/protocols/openai/responses`
- **From your terminal:**

```bash
azd ai agent invoke pizza-shop-ops \
  "What's the dough hydration and bake time for a Neapolitan margherita?"
```

Every call lands a trace in Application Insights (this run: `99d523678bec1da197aab90aa3cce593`), so the `tool_search` query, the `call_tool` pick, and the latency are all real, inspectable numbers — not screenshots.

## How I built it (the honest version)

The happy path is `azd ai agent init` → `azd provision` → `azd deploy`. I hit two environment snags worth writing down, because you might too:

1. **`azd provision` wouldn't run** — it kept trying to resolve my principal against a dead subscription in a tenant I'd lost access to, and hard-failed before touching the template. Fix: provision the Bicep directly with `az deployment sub create`, which uses a clean subscription list. The Foundry project, gpt-4o deployment, ACR, and App Insights all came up in one shot.
2. **`azd deploy` code path is region-gated** — direct ZIP/code deploy is only supported in a few regions (not `eastus2`), and I had no local Docker. Fix: container deploy with `docker: remoteBuild: true` in `azure.yaml`, so azd builds the image on ACR instead of my machine. Deployed in **2m28s**.

Neither is a Toolbox or agent problem — they're auth/region/tooling papercuts. The product path itself (toolbox create → agent connects → Tool Search ranks → guarded call pauses) worked exactly as designed, first try, both locally and deployed.

## Honest cloud caveats

- **Preview.** Tool Search and hosted agents are in preview; endpoints and flags move.
- **One search round-trip per intent.** You trade a flat, cheap context for a search hop. Worth it past ~5 tools; overkill below that.
- **Matching is only as good as the descriptions.** `additional_search_text` (the colloquial "fire up / crank up the oven" padding) is doing real ranking work — without it, "set oven temperature" doesn't reliably beat "read oven temperature."
- **Cold start + container tier.** The agent runs on a small container; first call after idle is slower.
- **The zero-Azure path still exists.** If you don't want to spin up Azure, `make demo` runs the whole story locally against the emulator — same tools, same script, no cloud.

## What carries forward

This is the template. `mars-greenhouse-ops` and `squad-room` reuse the exact same spine — hero tools on Container Apps, a Foundry Toolbox with Tool Search, a hosted agent that never sees the full list — so the next two demos are mostly theme and story, not new plumbing.
