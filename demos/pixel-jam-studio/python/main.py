#!/usr/bin/env python3
"""
Pixel Jam Studio — a Toolbox + Routines + Copilot-SDK style demo.

Modes:
  (default)  scripted mock — talks to the local emulator; real ranking + real counter, no model key.
  --live     Copilot-SDK-driven agent loop (see docs/COPILOT_SDK.md).
  --real     wire a real Toolbox on Foundry (see toolbox_setup.py — TBD).

The magic moment: the box has N tools, the model's context has 2 (tool_search + call_tool),
AND the run finishes with a REAL playable index.html on disk in game-output/.
"""
import argparse, json, os, sys, urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import activity
import scenario

EMU = os.environ.get("TOOLBOX_MCP_ENDPOINT",
                     f"http://localhost:{os.environ.get('TOOLBOX_EMULATOR_PORT', '8765')}/toolboxes/pixel-jam-studio/mcp")
TOOLS_JSON = os.path.join(os.path.dirname(__file__), "..", "mock-backends", "tools.json")
GAME_OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "game-output", "index.html"))


def rpc(method, params=None, _id=[0]):
    _id[0] += 1
    payload = json.dumps({"jsonrpc": "2.0", "id": _id[0], "method": method, "params": params or {}}).encode()
    headers = {"Content-Type": "application/json", "Foundry-Features": "Toolboxes=V1Preview"}
    if os.environ.get("TOOLBOX_BEARER"):
        headers["Authorization"] = f"Bearer {os.environ['TOOLBOX_BEARER']}"
    req = urllib.request.Request(EMU, data=payload, headers=headers)
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())


def list_tools():
    return rpc("tools/list")["result"]["tools"]


def search(query, limit=5):
    res = rpc("tools/call", {"name": "tool_search", "arguments": {"query": query, "limit": limit}})
    return json.loads(res["result"]["content"][0]["text"])


def call(name, arguments):
    res = rpc("tools/call", {"name": "call_tool", "arguments": {"name": name, "arguments": arguments}})
    return res["result"]["content"][0]["text"]


def run_scripted():
    rpc("initialize")
    rpc("notifications/initialized")

    box_size = len(json.load(open(TOOLS_JSON))["tools"])
    visible = list_tools()
    pinned = max(0, len(visible) - 2)
    activity.header("Pixel Jam Studio  🎮")
    activity.sdk_note("Copilot SDK would drive this loop from your app; scripted mode fakes the driver.")
    activity.counter(box_size, len(visible), pinned)

    round_trip = 0
    current_routine = None
    for turn in scenario.TURNS:
        if turn.get("routine") and turn["routine"] != current_routine:
            current_routine = turn["routine"]
            activity.routine(current_routine)
        activity.user(turn["user"])
        round_trip += 1
        activity.tool_search(turn["intent"], round_trip)
        matches = search(turn["intent"])
        activity.matched([m["name"] for m in matches])
        c = turn["call"]
        activity.call_tool(c["name"], c["arguments"])
        if c["name"] == "code_scribe.write_game":
            activity.sdk_note("this is the code-emission step — a Copilot-SDK agent would write real files here.")
        activity.result(call(c["name"], c["arguments"]))

    activity.counter(box_size, len(list_tools()), pinned)
    if os.path.exists(GAME_OUT):
        print(f"\n\033[1m🎮 playable build:\033[0m file:///{GAME_OUT.replace(os.sep, '/')}")
        print("\033[2m// open that in a browser — arrow keys / A,D to move, P pause, R restart\033[0m")


def run_live():
    raise SystemExit("LIVE mode: wire the GitHub Copilot SDK here — see docs/COPILOT_SDK.md. "
                     "The SDK will drive tool_search / call_tool itself and can also emit code natively.")


def run_real():
    raise SystemExit("REAL mode: run `python toolbox_setup.py` to create the Foundry toolbox, "
                     "set TOOLBOX_MCP_ENDPOINT + TOOLBOX_BEARER, then run --live against it.")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--live", action="store_true")
    p.add_argument("--real", action="store_true")
    a = p.parse_args()
    (run_live if a.live else run_real if a.real else run_scripted)()
