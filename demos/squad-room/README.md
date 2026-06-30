# The Squad Room

> A whole AI team shares one governed Toolbox — every member, one searchable box, flat cost.

![demo](assets/demo.gif)

A flagship demo of **Toolbox with Tool Search on Foundry**: instead of wiring tools into each agent
separately, a whole **team** of AI agents (lead / researcher / builder) consumes the *same* governed
Toolbox endpoint. Every member fires its own `tool_search` against one big box, and every member's
context stays flat at **two** meta-tools. Built with the `toolbox-demo-builder` skill.

This is the "bring any agent" story: the team here is modeled on
[bradygaster/squad](https://github.com/bradygaster/squad), but the point is that *any* agent or
agent-team — Squad, Microsoft Agent Framework, Copilot, or something custom — talks to the same
Toolbox the same way. Squad is an independent community project; it's a fun, real example of "any."

## Run it in 2 minutes (no Azure)

Prereqs: Python 3.10+ (and the .NET 8 SDK if you want the C# version). Nothing Azure, no squad install.

```bash
git clone <this-repo> && cd squad-room
make demo            # python
make demo-dotnet     # C# (same team, same scenario, same output)
```

You'll watch three team members route a "add dark mode" request through one shared box: the lead
plans and assigns, the researcher digs up the theming pattern and design tokens, the builder opens a
PR and runs CI, and the lead cuts a governed release. A counter shows the box has **24** tools while
each member's context stays at **2**.

## What you just saw

The toolbox has `{"type": "toolbox_search_preview"}` turned on, so it hides every real tool and gives
each agent two meta-tools: `tool_search` (describe what you need) and `call_tool` (invoke it). Six
different subtasks across three members, six `tool_search` calls — all against **one** box. Adding a
25th tool costs every member nothing. **One box, one team, flat cost.**

The release step shows **governance**: `releases.cut` carries `require_approval: always`, so it pauses
for a lead sign-off before it fires — the same curated, policy-bound box for the whole team.

The scripted demo needs no model key: the *intent strings* are pre-written, but the **matching and
the counter are real** — the local emulator ranks the actual tool descriptions and reports the actual
context size.

## Optional: drive the build with Squad (Role A)

Squad can also be the *build assistant* that extends this demo. It is never required to run it.

```bash
npm install -g @bradygaster/squad-cli
squad init --preset default          # scaffolds a .squad/ team in the repo
copilot --agent squad --yolo         # then drive the team to extend python/ + dotnet/ at parity
```

## Go real (Foundry)

```bash
cp .env.example .env     # set FOUNDRY_PROJECT_ENDPOINT, model, server URLs
pip install -e ".[real]"
python python/toolbox_setup.py          # creates the real toolbox version (tool search on)
# then give each team member the same toolbox MCP endpoint and run a live loop (--live)
```
Real mode needs a Foundry project with a deployed model. For a fully hosted version, see the `azd up`
notes in the comments of `toolbox_setup`.

## Remix it

Open `mock-backends/tools.json`, change a tool's description or add a new one, and rerun `make demo`.
**The team's code doesn't change** — reshape the shared box without touching any agent. That's the
managed-toolbox payoff, multiplied across a whole team.

## Links

- Blog: [BLOG.md](./BLOG.md)
- Gallery: https://toolbox.io
- Docs: Toolbox with Tool Search on Foundry — Microsoft Learn
