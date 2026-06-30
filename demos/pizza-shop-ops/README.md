# Pizza Shop Ops

> A fun, cloneable Toolbox with Tool Search on Foundry demo.

![demo](assets/demo.gif)

A tiny, fun demo of **Toolbox with Tool Search on Foundry**: a big box of tools behind one
endpoint, and an agent whose context never grows past **two** meta-tools no matter how big the box
gets. Built with the `toolbox-demo-builder` skill.

## Run it in 2 minutes (no Azure)

Prereqs: Python 3.10+ (and the .NET 8 SDK if you want the C# version). Nothing Azure.

```bash
git clone <this-repo> && cd pizza-shop-ops
make demo            # python
make demo-dotnet     # C# (same scenario, same output)
```

You'll watch the agent take a plain-English request, call `tool_search` to find the right capability,
and `call_tool` to use it — while a counter shows the box has **N** tools and the model's context has
**2**.

## What you just saw

The toolbox has `{"type": "toolbox_search_preview"}` turned on. That hides every real tool from the
model and injects two meta-tools instead: `tool_search` (describe what you need) and `call_tool`
(invoke it). So adding a 30th tool costs the model nothing — its context stays flat at two. **Big
box, tiny context.**

The scripted demo needs no model key: the *intent strings* are pre-written, but the **matching and
the counter are real** — the local emulator ranks the actual tool descriptions and reports the actual
context size.

## Go real (Foundry)

```bash
cp .env.example .env     # set FOUNDRY_PROJECT_ENDPOINT, model, server URLs
# python:
pip install -e ".[real]"
python python/toolbox_setup.py          # creates the real toolbox version (tool search on)
# then point the agent at the consumer endpoint and run a live model loop (--live)
```
For a fully hosted version, see the `azd up` notes in the comments of `toolbox_setup`. Real mode needs
a Foundry project with a deployed model.

## Remix it

Open `mock-backends/tools.json`, change a tool's description or add a new one, and rerun `make demo`.
**The agent code doesn't change** — that's the whole point of a managed toolbox: you reshape the tools
without touching the agent.

## Links

- Blog: [BLOG.md](./BLOG.md)
- Gallery: https://toolbox.io
- Docs: Toolbox with Tool Search on Foundry — Microsoft Learn
