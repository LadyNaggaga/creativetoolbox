# Creative Toolbox

> Fun, cloneable demos for **Toolbox with Tool Search on Foundry**.

This repository showcases how to build AI agents that work with a managed toolbox—one endpoint, many tools, flat context cost. Every demo puts that on screen: the model only ever sees `tool_search` and `call_tool`, no matter how big the box gets.

## What's Inside

| Folder | Description |
|--------|-------------|
| [**demos/**](./demos) | Ready-to-run demo scenarios (Python + .NET) |
| [**toolbox.io/**](./toolbox.io) | Static demo gallery website |
| [**creative-handler/**](./creative-handler) | The `toolbox-demo-builder` skill for generating new demos |

## Demos

Each demo runs offline against a local mock emulator—no Azure, no API key. Clone and run `make demo` to see Tool Search in action.

| Demo | Description | Tools |
|------|-------------|-------|
| [Mars Greenhouse Ops](./demos/mars-greenhouse-ops) | Run a cheerful day in a Mars colony greenhouse—checking air, watering tomatoes, balancing grow-lights | 24 |
| [Pizza Shop Ops](./demos/pizza-shop-ops) | Handle the Friday rush without dropping a pie—Tool Search picks the station, approval gates the oven | 24 |
| [Squad Room](./demos/squad-room) | A whole AI team (lead, researcher, builder) shares one governed Toolbox | 24 |

### Quick Start

```bash
# Clone the repo
git clone https://github.com/LadyNaggaga/creativetoolbox.git
cd creativetoolbox

# Pick a demo and run it
cd demos/mars-greenhouse-ops
make demo           # Python
make demo-dotnet    # C# (same scenario)
```

**Prerequisites:** Python 3.10+ (and .NET 8 SDK for C# demos).

## The Big Idea

Traditional agent setups expose every tool to the model—context grows linearly with tools. With **Toolbox + Tool Search**, the model sees only two meta-tools:

- `tool_search` — describe what you need
- `call_tool` — invoke it

Adding a 30th tool costs the model nothing. **Big box, tiny context.**

## Gallery Website

The [`toolbox.io/`](./toolbox.io) folder contains a static website that showcases all demos. Open `index.html` locally or visit the hosted version.

## Building New Demos

The [`toolbox-demo-builder`](./creative-handler/toolbox-demo-builder.skill) skill generates new demos following the established pattern. Use it from Copilot CLI to scaffold a new scenario.

## Links

- **Docs:** Toolbox with Tool Search on Foundry — Microsoft Learn
- **Gallery:** [toolbox.io](./toolbox.io/index.html)

## License

See [LICENSE](./LICENSE) for details.
