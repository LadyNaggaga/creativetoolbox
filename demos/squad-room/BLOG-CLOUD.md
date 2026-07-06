# I gave a whole AI team one deployed Toolbox, and each member wrote its own search

The [local demo](BLOG.md) modeled a software team as three AI agents — a lead, a researcher, and a builder — and pointed all of them at **one** box of 48 tools. Every member saw only two: `tool_search` and `call_tool`. That version ran on my laptop with `make demo`. This one is **deployed** — the 48 dev tools run as a real MCP server on Azure Container Apps, a real **Foundry Toolbox with Tool Search** governs them, and a **hosted agent on Microsoft Foundry** answers for whoever is talking. Every search query below is the one the model *actually wrote*, pulled straight off the wire.

Same principle: **one box, one team, flat cost.** New part: it's live, it's governed, and I can hand you the endpoint.

## The shape of it

Three moving pieces, each a supported product surface, wired end to end — and the whole team hits the *same* one:

```
lead ┐
res. ├─▶ hosted agent (Foundry, gpt-4o) ─▶ Toolbox + Tool Search (Foundry) ─▶ MCP server (Azure Container Apps)
bld. ┘                                          tool_search / call_tool           repo · ci · issues · releases · design · kb
```

- The **hero tools** (`repo.open_pr`, `ci.run_tests`, `issues.assign`, `releases.cut`, `design.lookup_tokens`, `kb.search_docs`, …) run as a FastMCP streamable-http server on **Azure Container Apps** — the exact same `hero_tools/` logic the local demo uses, just containerized and public.
- A **Foundry Toolbox** (`squad-room`, v1) wraps that server behind one MCP endpoint with `{"type": "toolbox_search_preview"}` on, so every agent sees only `tool_search` and `call_tool` — never the 48-tool list.
- A **hosted agent** (the Agent Framework `04-foundry-toolbox` sample, customized for the squad) connects to that one toolbox endpoint. I didn't write the MCP plumbing, the `Foundry-Features` header, the token dance, or the tool loop — the sample and the platform did.

The point that survives the move to the cloud: you don't wire tools into each agent. You curate **one** governed box and point the whole team at it.

## The money shot: three roles, three searches, one box

I asked the *deployed* agent three plain questions — one per role — and read the traces back.

**The researcher, finding prior art:**

```
>_ user: "Find how theming is currently done in this codebase."

   [tool_search]  query: "find how theming is done"                  ← the model wrote this
   [matched]      squadroom.kb_search_docs
   [call_tool]    squadroom.kb_search_docs(...)
   => "ThemeProvider in src/ui/theme.tsx wraps the app; colors already
       read from CSS variables; no dark palette defined yet."

   [assistant]    "Theming is currently managed via a ThemeProvider in
                   src/ui/theme.tsx … no dark palette yet."
```

**The builder, shipping the change:**

```
>_ user: "Open a pull request that adds a dark palette to the ThemeProvider."

   [tool_search]  query: "open a pull request"                       ← the model wrote this
   [matched]      squadroom.repo_open_pr
   [call_tool]    squadroom.repo_open_pr({ title: "Add dark mode palette to ThemeProvider", … })
   => PR #128 on feature/dark-mode — 6 files, +142 / -18, ready for review
```

**The lead, cutting the release:**

```
>_ user: "Cut a release with the dark mode change."

   [tool_search]  query: "cut a release"                             ← the model wrote this
   [matched]      squadroom.releases_cut   (governed — require_approval: always)
   [call_tool]    squadroom.releases_cut({ branch: "dark-mode-feature", … })
   => [approval required] releases.cut is governed. → held for lead sign-off.

   tools in the shared box: 48   ·   tools in each member's context: 2
```

Nobody scripted those three `tool_search` strings. Each role read its own intent, described what it needed in its own words, and the *same* box ranked the right tool to the top — `kb_search_docs`, then `repo_open_pr`, then `releases_cut` — out of 48. That's the whole pitch for a team: you don't inline 48 schemas into three prompts and pray. Every agent *searches* the one box.

## The approval gate, live

`releases.cut` carries `require_approval: always` on the toolbox. Cutting a release ships to users, so it's not something an agent should do on its own say-so — no matter which team member asked. On the deployed agent:

```
>_ [lead] "Cut a release with the dark mode change."

   [assistant]  "The release is ready to include the dark mode feature. Once
                 approved, the release will create a preview version from the
                 dark-mode-feature branch and add release notes … Let me know
                 if I should proceed."
```

The guard fires. The agent recognizes the action is governed and stops for a human instead of shipping on its own. And because the policy lives on the **box**, not in agent code, it applies to the lead, the researcher, and the builder at once — one place to govern, the whole team covered.

## It's deployed — here's the endpoint

This isn't a `make demo` emulator. It's a running agent you can hit:

- **Agent playground:** open it in the [Foundry portal](https://ai.azure.com/nextgen/r/LThb9AdWSnaqlSi_ntO2JQ,rg-squad-room-cealro,,ai-account-2hbt3dw62m7s4,ai-project-squad-room-cealro/build/agents/squad-room/build?version=1) and chat with it as any role.
- **Responses endpoint:** `POST …/agents/squad-room/endpoint/protocols/openai/responses`
- **From your terminal:**

```bash
azd ai agent invoke squad-room \
  "Find how theming is currently done in this codebase."
```

Every call lands a trace in Application Insights, so the `tool_search` query, the `call_tool` pick, and the latency are all real, inspectable numbers — not screenshots. The three runs above were:

| role | response id |
|------|-------------|
| researcher | `caresp_36f651b7d83689a800Ooh3D4wYGDn0Ymdbak5c5SNXs9Da5rLv` |
| builder | `caresp_25c2d5c4b169193900XclDOVzpnyDdAuCfmsaAdXOE6umbgOnN` |
| lead (gate) | `caresp_ca6ee55b3586325000KXopU4c5kXOpW8tWDMv6P89z4lIs8Ide` |

## How I built it (the honest version)

The happy path is `azd ai agent init` → `azd provision` → `azd deploy`. Same environment snags as the pizza and mars builds, same fixes:

1. **`azd provision` wouldn't run** — it kept trying to resolve my principal against a dead subscription in a tenant I'd lost access to, and hard-failed before touching the template. Fix: provision the Bicep directly with `az deployment sub create`, which uses a clean subscription list. The Foundry project, gpt-4o deployment, ACR, and App Insights all came up in one shot.
2. **`azd deploy` code path is region-gated** — direct ZIP/code deploy isn't supported in `eastus2`, and I had no local Docker. Fix: container deploy with `docker: remoteBuild: true` in `azure.yaml`, so azd builds the image on ACR instead of my machine. Deployed in **2m28s**.
3. **A phantom default env** — the shell kept injecting a stray `AZURE_ENV_NAME` that made azd deploy an empty environment. Fix: pin `$env:AZURE_ENV_NAME` to the real env and reset `.azure/config.json` in the same shell before `azd deploy`.

None of these is a Toolbox or agent problem — they're auth/region/tooling papercuts. The product path itself (toolbox create → agents connect → Tool Search ranks → governed release pauses) worked exactly as designed.

## Honest cloud caveats

- **Preview.** Tool Search and hosted agents are in preview; endpoints and flags move.
- **One search round-trip per intent.** You trade a flat, cheap context for a search hop — but it's *per capability*, so a whole team's worth of intents each cost one hop, not 48 inlined schemas. At 48 tools shared across three roles it's an easy call.
- **Matching is only as good as the descriptions.** `additional_search_text` (the colloquial "how is theming done / open a PR / cut a release" padding) is doing real ranking work — with 48 tools and several doc-search-shaped competitors, that padding is what keeps `kb_search_docs` on top for a vague "how do we do X" question.
- **Cold start + container tier.** The agent runs on a small container; first call after idle is slower.
- **The zero-Azure path still exists.** If you don't want to spin up Azure, `make demo` runs the whole three-role story locally against the emulator — same 48 tools, same script, no cloud.

## What carries forward

This is the third demo on the exact same spine as [pizza-shop-ops](../pizza-shop-ops/BLOG-CLOUD.md) and [mars-greenhouse-ops](../mars-greenhouse-ops/BLOG-CLOUD.md) — hero tools on Container Apps, a Foundry Toolbox with Tool Search, a hosted agent that never sees the full list. Three demos in, the plumbing is boilerplate; only the theme and the story change.

But `squad-room` is the flagship, and it isn't done: next it gets the **enterprise governance layer** — front the ACA MCP server with **API Management** and register it in an **Azure API Center private MCP registry**, so the team's agents discover only *approved* tools through a governed gateway, with audit and access control on top. The toolbox just re-points at the governed URL; everything above stays the same. That's the demo that turns "one box for a team" into "one *governed* box for an org."
