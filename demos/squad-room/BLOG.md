# Six agents, one box: I gave a whole AI team a single Toolbox and each saw two tools

I modeled a software team as three AI agents — a lead, a researcher, and a builder — and pointed all of them at **one** governed Toolbox on Foundry. Six subtasks, six `tool_search` calls, one shared box of 48 tools, and every member's context stayed flat at two. The principle: **one box, one team, flat cost.**

## What it does

`squad-room` runs an "add dark mode" request through a team that shares a single Toolbox. The lead plans and assigns the work, the researcher digs up the existing theming pattern and design tokens, the builder opens a PR and runs CI, and the lead cuts a governed preview release. The team here is modeled on [bradygaster/squad](https://github.com/bradygaster/squad) — but the whole point is that *any* agent or agent-team consumes the same endpoint the same way. It runs locally with `make demo` — no Azure, no squad install, no key.

![demo](assets/demo.gif)

## The trick

Each member only ever sees `tool_search` and `call_tool`. They issue different intents — "assign the work", "find the theming pattern", "open a PR", "cut a release" — and the box ranks the right tool to the top each time. The release is **governed**: `releases.cut` carries `require_approval: always` and pauses for a lead sign-off.

```
>_ [lead]       "new request landed: 'add dark mode'. break it down and assign it."
   [tool_search] query: "plan and break a feature request into work items and assign them"   // #1
   [matched]     issues.assign, repo.open_pr, ci.run_tests
   [call_tool]   issues.assign({ "feature": "add dark mode" })
>_ [researcher] "how is theming already done in our codebase?"
   [tool_search] query: "search our docs and codebase for the existing theming pattern"   // #2
   [call_tool]   kb.search_docs({ "topic": "theming" })
>_ [lead]       "cut a preview release"
   [call_tool]   releases.cut(...)  => [approval required] governed; lead approved -> v1.4.0-preview
tools in the shared box: 48   ·   tools in each member's context: 2
```

## The numbers

- Tools in the shared box: **48**
- Tools in each member's context: **2** (`tool_search` + `call_tool`)
- Team members on one box: **3** (lead, researcher, builder)
- `tool_search` round-trips: **6** (each member, its own subtasks)
- Governed tools that paused for approval: **1** (`releases.cut`)
- Per-agent tool wiring I had to write: **0** — they all share the one endpoint

## The part people miss

You don't wire tools into each agent. You curate **one** box and point the whole team at it. Add a 49th tool to `tools.json` and every member can discover it through `tool_search` on the next run — no agent code changes, for any of them. Governance lives on the box, so a policy like "releases need approval" applies to the whole team at once.

## Clone it

```bash
git clone <repo> && cd squad-room && make demo      # python
make demo-dotnet                                     # C#, identical output
```

## Honest caveats

Squad is an independent community project, and this demo models the team conceptually so it runs with zero dependencies; the README shows how to wire a real Squad team (or any Agent Framework team) to the same endpoint. Tool Search is in preview — one search round-trip per intent, and match quality rides entirely on your tool descriptions. The win shows up exactly when you have many tools *and* many agents: curate once, share everywhere.
