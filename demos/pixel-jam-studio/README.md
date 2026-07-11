# Pixel Jam Studio 🎮

> A fun, cloneable **Toolbox + Routines + Copilot SDK** demo.

A tiny, silly 48-hour game jam — run by an agent. Toolbox with Tool Search on Foundry keeps the
model's context flat while it browses a big box of studio tools; **Routines** encode the jam
ceremony (kickoff → prototype → playtest → ship); and the **GitHub Copilot SDK** is what drives
the loop from your app and actually writes the game code.

At the end you get a **real playable `index.html`** in `game-output/`. Open it in a browser.
Arrow keys / `A,D` to move, `P` to pause, `R` to restart.

## Run it in 2 minutes (no Azure, no key)

Prereqs: Python 3.10+.

```bash
git clone <this-repo> && cd demos/pixel-jam-studio
make demo
make play        # opens the built game in your browser
```

You'll watch the agent take plain-English studio-mate prompts, call `tool_search` to find the
right capability, and `call_tool` to use it — while a counter shows the box has **N** tools and
the model's context has **2**. The final `code_scribe.write_game` step writes a real playable
HTML5 canvas game to disk.

## The three-pillar demo

| Pillar | What it does here |
| --- | --- |
| **Toolbox** on Foundry | One MCP endpoint, ~19 tools in the box, only 2 in the model context |
| **Routines** | Named phases (`kickoff`, `prototype`, `playtest_loop`, `ship_it`) that group the calls |
| **Copilot SDK** | Drives the loop from your app; `code_scribe.write_game` is the code-emission step a Copilot-SDK agent would perform natively |

## The jam flow

```
🎡 kickoff        → theme_wheel.spin
🎨 prototype      → asset_studio.generate  →  chiptune_jukebox.pick  →  sfx_foley.pick
                  → code_scribe.write_game     ← [Copilot SDK writes index.html here]
🎮 playtest_loop  → playtest_arcade.run (iter 1) → playtest_arcade.run (iter 2)
🚀 ship_it        → jam_judge.score → leaderboard_cabinet.post
```

## Why this shows off Copilot SDK

The Copilot CLI/SDK is at its best when an agent needs to **write real source files**. In this
demo, `code_scribe.write_game` is the "coding agent" moment: it takes the theme + sprite + audio
spec picked by earlier tool calls and emits a complete self-contained playable game. In
`--live` mode, the SDK drives the whole loop and can emit files natively without a wrapper tool.

## Go real (Foundry + Copilot SDK)

```bash
pip install -e ".[live]"        # installs github-copilot-sdk
# python python/toolbox_setup.py   # (TBD) creates the real Foundry toolbox
# then run:
python python/main.py --live
```

## Remix it

- Change the theme wheel in `mock-backends/hero_tools/theme_wheel_spin.py`.
- Add new tools by editing `mock-backends/tools.json` — the agent code doesn't change.
- Tweak the emitted game in `mock-backends/hero_tools/code_scribe_write_game.py` — that's the
  template a real Copilot-SDK agent would replace with generated code.

## Links

- Copilot SDK: https://github.com/github/copilot-sdk
- Gallery: https://toolbox.io
- Docs: Toolbox with Tool Search on Foundry — Microsoft Learn
